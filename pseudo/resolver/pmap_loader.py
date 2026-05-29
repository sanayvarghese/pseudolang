"""
.pmap Loader - Section 4 of the spec.

Responsibilities:
  - Parse .pmap file syntax (whitelist-only, no code execution)
  - Resolve @inherit chains with cycle detection
  - Merge pattern sets with APPEND / REPLACE / PREPEND modes
  - Detect pattern conflicts and warn
  - Build trie structure for fast first-token dispatch
  - Read/write .pmap.cache files (SHA256-based invalidation)

Pattern matching algorithm (Section 4.6):
  - No regex anywhere
  - Custom token matcher
  - Placeholder types: name, expr, number, condition, word, collection, any
  - Keyword termination for expr/condition placeholders (Section 4.4)
  - Specificity ordering (Section 4.5)
"""

import os
import json
import hashlib
import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from ..parser.tokenizer import tokenize, Token


# ──────────────────────────────────────────────────────────────
# Placeholder types
# ──────────────────────────────────────────────────────────────

PLACEHOLDER_TYPES = frozenset(['name', 'expr', 'number', 'condition', 'word', 'collection', 'any'])


@dataclass
class Placeholder:
    var_name: str   # e.g. "var", "start", "condition"
    ph_type: str    # one of PLACEHOLDER_TYPES


@dataclass
class PatternToken:
    """One token in a compiled pattern - either a literal word or a placeholder."""
    is_placeholder: bool
    literal: str = ''           # lowercase if literal
    placeholder: Optional[Placeholder] = None

    @property
    def specificity_score(self) -> int:
        return 0 if self.is_placeholder else 1


# ──────────────────────────────────────────────────────────────
# Compiled pattern
# ──────────────────────────────────────────────────────────────

@dataclass
class CompiledPattern:
    canonical: str
    tokens: List[PatternToken]
    specificity: int          # count of literal tokens
    file_order: int           # position in file (lower = higher priority)
    pattern_str: str = ''     # original pattern string
    context_requirements: List[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────
# MatchResult
# ──────────────────────────────────────────────────────────────

@dataclass
class MatchResult:
    canonical: str
    captures: Dict[str, str]  # placeholder name → raw string value
    pattern: Optional[Any] = None


# ──────────────────────────────────────────────────────────────
# Pattern parser
# ──────────────────────────────────────────────────────────────

def _parse_pattern(pattern_str: str) -> List[PatternToken]:
    """
    Parse a pattern string like:
      "for {var:name} from {start:expr} to {end:expr}"
    into a list of PatternToken objects.
    """
    tokens: List[PatternToken] = []
    i = 0
    text = pattern_str.strip()
    while i < len(text):
        if text[i] == '{':
            # Find closing }
            j = text.index('}', i)
            inner = text[i+1:j]
            if ':' in inner:
                var_name, ph_type = inner.split(':', 1)
                var_name = var_name.strip()
                ph_type = ph_type.strip().lower()
            else:
                var_name = inner.strip()
                ph_type = 'expr'
            tokens.append(PatternToken(
                is_placeholder=True,
                placeholder=Placeholder(var_name=var_name, ph_type=ph_type)
            ))
            i = j + 1
        elif text[i] in (' ', '\t'):
            i += 1
        else:
            # Collect literal word (may contain apostrophes like "isn't")
            j = i
            while j < len(text) and text[j] not in (' ', '\t', '{'):
                j += 1
            word = text[i:j].lower()
            if word:
                tokens.append(PatternToken(is_placeholder=False, literal=word))
            i = j
    return tokens


def _specificity(tokens: List[PatternToken]) -> int:
    """Count literal tokens = specificity score."""
    return sum(1 for t in tokens if not t.is_placeholder)


# ──────────────────────────────────────────────────────────────
# .pmap file parser
# ──────────────────────────────────────────────────────────────

@dataclass
class PmapFile:
    version: str = '1.0'
    pseudo_version: str = '>=1.0'
    language: str = 'English'
    author: str = ''
    inherit: Optional[str] = None
    inherit_mode: str = 'APPEND'     # APPEND | REPLACE | PREPEND
    ignore_default: bool = False
    # canonical → list of (pattern_str, context_list, is_replace_mode, file_order)
    sections: Dict[str, List] = field(default_factory=dict)
    section_modes: Dict[str, str] = field(default_factory=dict)   # canonical → APPEND|REPLACE


def parse_pmap_file(path: str) -> PmapFile:
    """
    Parse a .pmap file. Raises PmapError on invalid syntax.
    Whitelist-only: only recognized directives accepted.
    """
    if not os.path.exists(path):
        raise PmapError(f"PmapError: File not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pmap = PmapFile()
    current_canonical: Optional[str] = None
    current_context: List[str] = []
    file_order = 0

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip('\n\r')
        stripped = line.strip()

        # Blank lines
        if not stripped:
            continue

        # Comments
        if stripped.startswith('#'):
            continue

        # Metadata directives
        if stripped.startswith('@pmap-version'):
            pmap.version = stripped.split(None, 1)[1] if len(stripped.split(None, 1)) > 1 else '1.0'
            continue
        if stripped.startswith('@pseudo-version'):
            pmap.pseudo_version = stripped.split(None, 1)[1] if len(stripped.split(None, 1)) > 1 else '>=1.0'
            continue
        if stripped.startswith('@language'):
            rest = stripped.split(None, 1)[1] if len(stripped.split(None, 1)) > 1 else ''
            pmap.language = rest.strip('"\'')
            continue
        if stripped.startswith('@author'):
            rest = stripped.split(None, 1)[1] if len(stripped.split(None, 1)) > 1 else ''
            pmap.author = rest.strip('"\'')
            continue
        if stripped.startswith('@inherit'):
            parts = stripped.split()
            # @inherit file.pmap [MODE]
            if len(parts) >= 2:
                pmap.inherit = parts[1]
            if len(parts) >= 3:
                mode = parts[2].upper()
                if mode in ('APPEND', 'REPLACE', 'PREPEND'):
                    pmap.inherit_mode = mode
            continue
        if stripped == '@ignore-default':
            pmap.ignore_default = True
            continue
        if stripped.startswith('@context'):
            # @context TOP_LEVEL FUNCTION_BODY ...
            parts = stripped.split()[1:]
            current_context = parts
            continue

        # Section headers [CANONICAL_NAME] or [CANONICAL_NAME] @replace
        if stripped.startswith('[') and ']' in stripped:
            bracket_end = stripped.index(']')
            canonical = stripped[1:bracket_end].strip().upper()
            rest_after = stripped[bracket_end+1:].strip()
            mode = 'APPEND'
            if '@replace' in rest_after.lower():
                mode = 'REPLACE'
            current_canonical = canonical
            current_context = []
            if canonical not in pmap.sections:
                pmap.sections[canonical] = []
            pmap.section_modes[canonical] = mode
            continue

        # Check for forbidden content (security whitelist)
        lower = stripped.lower()
        forbidden_keywords = ['import', 'exec', 'eval', 'open(', 'os.', 'sys.',
                              'subprocess', '__import__', 'compile(']
        for fk in forbidden_keywords:
            if fk in lower:
                raise PmapError(
                    f"PmapError: Invalid .pmap: unexpected token '{fk}' at line {lineno}.\n"
                    f"  .pmap files cannot contain executable code."
                )

        # Pattern line (must be inside a section)
        if current_canonical is not None:
            # Skip lines that are just annotation/tags
            if stripped.startswith('@'):
                continue
            pmap.sections[current_canonical].append(
                (stripped, list(current_context), file_order)
            )
            file_order += 1
            continue

        # Unknown content outside a section
        # Silently skip (generous parsing)

    return pmap


class PmapError(Exception):
    pass


# ──────────────────────────────────────────────────────────────
# Trie structure for fast first-token dispatch
# ──────────────────────────────────────────────────────────────

class PatternTrie:
    """
    Groups patterns by their first literal token for O(1) dispatch.
    Patterns that start with a placeholder go into a special '*' bucket.
    """

    def __init__(self):
        # first_literal → sorted list of CompiledPattern (by specificity desc, file_order asc)
        self._buckets: Dict[str, List[CompiledPattern]] = {}

    def add(self, pattern: CompiledPattern):
        if not pattern.tokens or pattern.tokens[0].is_placeholder:
            key = '*'
        else:
            key = pattern.tokens[0].literal
        if key not in self._buckets:
            self._buckets[key] = []
        self._buckets[key].append(pattern)
        # Keep sorted: higher specificity first; tie-break by file_order asc
        self._buckets[key].sort(key=lambda p: (-p.specificity, p.file_order))

    def lookup(self, first_word: str) -> List[CompiledPattern]:
        """Return patterns that might match given the first word."""
        first_lower = first_word.lower()
        patterns = list(self._buckets.get(first_lower, []))
        patterns += self._buckets.get('*', [])
        return patterns

    def all_patterns(self) -> List[CompiledPattern]:
        result = []
        for bucket in self._buckets.values():
            result.extend(bucket)
        return result


# ──────────────────────────────────────────────────────────────
# Token-level pattern matcher (Section 4.6)
# ──────────────────────────────────────────────────────────────

# Global stop tokens (built from default.pmap literal words) - Section 4.4
DEFAULT_STOP_TOKENS = frozenset([
    'for', 'from', 'to', 'step', 'in', 'each', 'every', 'while', 'until',
    'if', 'when', 'check', 'given', 'else', 'otherwise', 'return', 'give',
    'back', 'and', 'or', 'not', 'as', 'is', 'then', 'loop', 'repeat',
    'function', 'func', 'define', 'def', 'procedure', 'foreach', 'traverse',
    'through', 'algorithm', 'recursive', 'helper', 'method',
])


def try_match(
    pattern: CompiledPattern,
    input_words: List[str],
    stop_tokens: frozenset,
    context: str = 'TOP_LEVEL',
) -> Optional[Dict[str, str]]:
    """
    Try to match pattern against input_words.
    Returns captures dict on success, None on failure.
    Implements algorithm from Section 4.6.
    """
    # Context check
    if pattern.context_requirements:
        if context not in pattern.context_requirements:
            return None

    ptoks = pattern.tokens
    itoks = [w.lower() for w in input_words]   # case-insensitive
    original = input_words                       # preserve case for captures

    p = 0
    i = 0
    captures: Dict[str, str] = {}

    while p < len(ptoks) and i < len(itoks):
        pt = ptoks[p]

        if not pt.is_placeholder:
            # Literal match
            if itoks[i] == pt.literal:
                p += 1
                i += 1
            else:
                return None   # literal mismatch

        else:
            ph = pt.placeholder
            # Find next literal in pattern to know the stop boundary
            next_literal = None
            for pp in range(p + 1, len(ptoks)):
                if not ptoks[pp].is_placeholder:
                    next_literal = ptoks[pp].literal
                    break

            collected_indices = []
            while i < len(itoks):
                word_lower = itoks[i]
                if next_literal is not None and word_lower == next_literal:
                    break
                # For name/number/word types: check type constraint
                if ph.ph_type == 'name':
                    # Must be valid identifier - single word, no operators
                    if not _is_identifier(original[i]):
                        break
                elif ph.ph_type == 'number':
                    if not _is_number(original[i]):
                        break
                elif ph.ph_type == 'word':
                    if not original[i].isalpha():
                        break
                else:
                    # expr / condition / collection / any:
                    # stop at stop tokens ONLY when next_literal is None
                    if next_literal is None and ph.ph_type in ('expr', 'condition', 'collection'):
                        if word_lower in stop_tokens:
                            break
                collected_indices.append(i)
                i += 1

            if ph.ph_type == 'name' and len(collected_indices) != 1:
                # name must be exactly one token
                return None

            captures[ph.var_name] = ' '.join(original[idx] for idx in collected_indices)
            p += 1

    # All pattern tokens must be consumed
    if p < len(ptoks):
        return None
    # All input words should be consumed (allows trailing colon to be stripped separately)
    # (colons are stripped before matching)
    return captures


def _is_identifier(word: str) -> bool:
    """Check if word is a valid identifier."""
    if not word:
        return False
    if not (word[0].isalpha() or word[0] == '_'):
        return False
    for ch in word[1:]:
        if not (ch.isalnum() or ch == '_'):
            return False
    return True


def _is_number(word: str) -> bool:
    """Check if word is a numeric literal."""
    try:
        float(word)
        return True
    except ValueError:
        return False


# ──────────────────────────────────────────────────────────────
# PmapLoader - main entry point
# ──────────────────────────────────────────────────────────────

class PmapLoader:
    """
    Loads, merges, caches, and provides pattern lookup for .pmap files.
    """

    def __init__(self, pmap_path: str, cache_dir: Optional[str] = None,
                 compiler_version: str = '1.0'):
        self.pmap_path = pmap_path
        self.cache_dir = cache_dir
        self.compiler_version = compiler_version
        self._trie: Optional[PatternTrie] = None
        self._stop_tokens: frozenset = DEFAULT_STOP_TOKENS
        self._patterns: List[CompiledPattern] = []
        self.warnings: List[str] = []

    def load(self) -> PatternTrie:
        """Load the .pmap file (with cache) and return a ready PatternTrie."""
        # Try cache first
        cache_path = self._cache_path()
        if cache_path and self._cache_valid(cache_path):
            trie, patterns = self._load_cache(cache_path)
            self._trie = trie
            self._patterns = patterns
            return trie

        # Full load
        trie, patterns = self._full_load()
        self._trie = trie
        self._patterns = patterns

        if cache_path:
            self._save_cache(cache_path, trie, patterns)

        return trie

    def _full_load(self) -> Tuple[PatternTrie, List[CompiledPattern]]:
        """Load, merge, and compile patterns from pmap file + inheritance chain."""
        all_patterns = self._load_chain(self.pmap_path, loading_stack=[])
        self._detect_conflicts(all_patterns)
        trie = PatternTrie()
        for p in all_patterns:
            trie.add(p)

        # Collect custom stop tokens from all literal pattern words
        extra_stops = set()
        for p in all_patterns:
            for tok in p.tokens:
                if not tok.is_placeholder and tok.literal.replace("'", "").isalpha():
                    extra_stops.add(tok.literal)
        self._stop_tokens = DEFAULT_STOP_TOKENS | frozenset(extra_stops)

        return trie, all_patterns

    def _load_chain(self, path: str, loading_stack: List[str],
                    global_file_order: List[int] = None) -> List[CompiledPattern]:
        """Recursively load pmap file with inheritance, cycle detection."""
        if global_file_order is None:
            global_file_order = [0]

        abs_path = os.path.abspath(path)
        if abs_path in loading_stack:
            chain = ' → '.join(loading_stack + [abs_path])
            raise PmapError(f"PmapError: Circular inheritance detected: {chain}")

        loading_stack = loading_stack + [abs_path]

        pmap = parse_pmap_file(path)

        # Compile this file's patterns
        my_patterns: Dict[str, List[CompiledPattern]] = {}
        for canonical, entries in pmap.sections.items():
            my_patterns[canonical] = []
            for (pattern_str, context, _) in entries:
                ptoks = _parse_pattern(pattern_str)
                sp = _specificity(ptoks)
                cp = CompiledPattern(
                    canonical=canonical,
                    tokens=ptoks,
                    specificity=sp,
                    file_order=global_file_order[0],
                    pattern_str=pattern_str,
                    context_requirements=context,
                )
                global_file_order[0] += 1
                my_patterns[canonical].append(cp)

        if not pmap.inherit:
            # No parent - just return our patterns
            result = []
            for patterns in my_patterns.values():
                result.extend(patterns)
            return result

        # Load parent
        parent_path = _resolve_pmap_path(pmap.inherit, path)
        parent_patterns_list = self._load_chain(parent_path, loading_stack, global_file_order)
        parent_by_canonical: Dict[str, List[CompiledPattern]] = {}
        for cp in parent_patterns_list:
            parent_by_canonical.setdefault(cp.canonical, []).append(cp)

        # Merge based on mode
        merged: Dict[str, List[CompiledPattern]] = {}
        all_canonicals = set(my_patterns.keys()) | set(parent_by_canonical.keys())

        for canonical in all_canonicals:
            mine = my_patterns.get(canonical, [])
            parent = parent_by_canonical.get(canonical, [])
            mode = pmap.section_modes.get(canonical, pmap.inherit_mode)

            if pmap.ignore_default:
                merged[canonical] = mine
            elif mode == 'REPLACE':
                merged[canonical] = mine   # completely replace parent
            elif mode == 'PREPEND':
                merged[canonical] = parent + mine   # parent first
            else:  # APPEND (default)
                merged[canonical] = mine + parent   # child first (higher priority)

        result = []
        for patterns in merged.values():
            result.extend(patterns)
        return result

    def match(self, words: List[str], context: str = 'TOP_LEVEL') -> Optional[MatchResult]:
        """
        Try to match an input word list against all patterns.
        Returns MatchResult or None.
        """
        if not self._trie or not words:
            return None

        candidates = self._trie.lookup(words[0])

        for pattern in candidates:
            captures = try_match(pattern, words, self._stop_tokens, context)
            if captures is not None:
                return MatchResult(canonical=pattern.canonical, captures=captures, pattern=pattern)

        return None

    def _detect_conflicts(self, patterns: List[CompiledPattern]):
        # Same-canonical check:
        by_canonical: Dict[str, List[CompiledPattern]] = {}
        for p in patterns:
            by_canonical.setdefault(p.canonical, []).append(p)

        for canonical, pats in by_canonical.items():
            # Sort pats by priority: specificity desc, file_order asc
            sorted_pats = sorted(pats, key=lambda p: (-p.specificity, p.file_order))
            for i in range(len(sorted_pats)):
                for j in range(i + 1, len(sorted_pats)):
                    a = sorted_pats[i]
                    b = sorted_pats[j]
                    if self._patterns_conflict(a.tokens, b.tokens):
                        # b is unreachable because it is checked after a, and a is a superset of b
                        warn_msg = (
                            f"Warning: Pattern '{b.pattern_str}' in section [{canonical}] is unreachable. "
                            f"It is conflicted by '{a.pattern_str}'."
                        )
                        self.warnings.append(warn_msg)

        # Cross-canonical check:
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                a = patterns[i]
                b = patterns[j]
                if a.canonical != b.canonical:
                    # check if they have the exact same signature
                    if len(a.tokens) == len(b.tokens):
                        identical = True
                        for ta, tb in zip(a.tokens, b.tokens):
                            if ta.is_placeholder != tb.is_placeholder:
                                identical = False
                                break
                            if ta.is_placeholder:
                                if ta.placeholder.ph_type != tb.placeholder.ph_type:
                                    identical = False
                                    break
                            else:
                                if ta.literal != tb.literal:
                                    identical = False
                                    break
                        if identical:
                            raise PmapError(
                                f"PmapError: ambiguous mapping: pattern '{a.pattern_str}' "
                                f"maps to both [{a.canonical}] and [{b.canonical}]."
                            )

    def _patterns_conflict(self, a: List[PatternToken], b: List[PatternToken]) -> bool:
        """Returns True if any input matching b will also be matched by a (i.e., a is a superset of b)."""
        if len(a) != len(b):
            return False
        for ta, tb in zip(a, b):
            if not ta.is_placeholder and not tb.is_placeholder:
                if ta.literal != tb.literal:
                    return False
            elif ta.is_placeholder and tb.is_placeholder:
                pa, pb = ta.placeholder.ph_type, tb.placeholder.ph_type
                if pa == pb:
                    continue
                if pa in ('any', 'expr'):
                    continue
                if pa == 'condition' and pb in ('expr', 'bool'):
                    continue
                return False
            elif ta.is_placeholder and not tb.is_placeholder:
                continue
            else:
                return False
        return True

    @property
    def stop_tokens(self) -> frozenset:
        return self._stop_tokens

    # ── Cache helpers ──────────────────────────────────────────

    def _cache_path(self) -> Optional[str]:
        if not self.cache_dir:
            return None
        base = os.path.basename(self.pmap_path)
        return os.path.join(self.cache_dir, base + '.cache')

    def _cache_valid(self, cache_path: str) -> bool:
        if not os.path.exists(cache_path):
            return False
        try:
            with open(cache_path, 'rb') as f:
                cached = pickle.load(f)
            pmap_hash = _sha256(self.pmap_path)
            return (cached.get('hash') == pmap_hash and
                    cached.get('version') == self.compiler_version)
        except Exception:
            return False

    def _load_cache(self, cache_path: str) -> Tuple[PatternTrie, List[CompiledPattern]]:
        with open(cache_path, 'rb') as f:
            cached = pickle.load(f)
        patterns = cached['patterns']
        self.warnings = cached.get('warnings', [])
        trie = PatternTrie()
        for p in patterns:
            trie.add(p)
        # Rebuild stop tokens
        extra_stops = set()
        for p in patterns:
            for tok in p.tokens:
                if not tok.is_placeholder and tok.literal.replace("'", "").isalpha():
                    extra_stops.add(tok.literal)
        self._stop_tokens = DEFAULT_STOP_TOKENS | frozenset(extra_stops)
        return trie, patterns

    def _save_cache(self, cache_path: str, trie: PatternTrie,
                    patterns: List[CompiledPattern]):
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump({
                'hash': _sha256(self.pmap_path),
                'version': self.compiler_version,
                'patterns': patterns,
                'warnings': self.warnings,
            }, f)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def _resolve_pmap_path(inherit_name: str, relative_to: str) -> str:
    """Resolve inherit path relative to the current .pmap file's directory."""
    base_dir = os.path.dirname(os.path.abspath(relative_to))
    candidate = os.path.join(base_dir, inherit_name)
    if os.path.exists(candidate):
        return candidate
    # Try pseudo home
    pseudo_home = os.path.join(os.path.expanduser('~'), '.pseudo')
    for subdir in ('core', 'custom', ''):
        p = os.path.join(pseudo_home, subdir, inherit_name)
        if os.path.exists(p):
            return p
    return candidate   # will fail when loaded (file not found error)
