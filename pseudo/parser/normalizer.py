"""
Normalization Pipeline - applied to line CONTENT only (not leading whitespace).

As per Section 4.15:
  1. Unicode NFC normalize
  2. Strip BOM and zero-width characters
  3. Collapse multiple whitespace to single space
  4. Strip trailing whitespace
  5. Convert tabs to spaces in content only
  6. strip()
  7. Case normalization is done at matching time (case-insensitive)
"""

import unicodedata
import re

# Zero-width characters to strip
_ZERO_WIDTH = frozenset([
    '\u200b',  # zero width space
    '\u200c',  # zero width non-joiner
    '\u200d',  # zero width joiner
    '\ufeff',  # BOM / zero width no-break space
    '\u2060',  # word joiner
    '\u00ad',  # soft hyphen
])


def normalize_content(text: str) -> str:
    """
    Apply the full normalization pipeline to a line's content.
    This must NOT be applied to leading whitespace.
    """
    # 1. Unicode NFC normalize
    text = unicodedata.normalize('NFC', text)

    # 2. Strip BOM and zero-width characters
    text = ''.join(ch for ch in text if ch not in _ZERO_WIDTH)

    # 3. Collapse multiple whitespace to single space
    #    (simple manual collapse - no regex per spec philosophy)
    result = []
    prev_space = False
    for ch in text:
        if ch in (' ', '\t'):
            if not prev_space:
                result.append(' ')
            prev_space = True
        else:
            result.append(ch)
            prev_space = False
    text = ''.join(result)

    # 4. Strip trailing whitespace (already handled by collapse + strip below)
    # 5. Convert tabs to spaces in content (already done in collapse above)
    # 6. strip
    return text.strip()
