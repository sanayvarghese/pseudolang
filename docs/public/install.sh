#!/usr/bin/env bash
# Pseudo Installer for macOS & Linux
# Hosted at: https://pseudo.wiki/install.sh
# Usage: curl -fsSL https://pseudo.wiki/install.sh | bash

set -e

REPO="sanayvarghese/pseudolang"
PSEUDO_VERSION="${PSEUDO_VERSION:-latest}"
INSTALL_DIR="${PSEUDO_INSTALL_DIR:-$HOME/.local/bin}"

BOLD="\033[1m"; CYAN="\033[1;36m"; GREEN="\033[1;32m"
YELLOW="\033[1;33m"; RED="\033[1;31m"; DIM="\033[2m"; RESET="\033[0m"

print_header() {
  printf "\n"
  printf "${YELLOW}  Write pseudocode. Actually run it.${RESET}\n"
  printf "${DIM}  No Python required - standalone binary.${RESET}\n\n"
}

step()  { printf "${GREEN}  [*]${RESET} %s\n" "$1"; }
info()  { printf "${CYAN}  [i]${RESET} %s\n" "$1"; }
warn()  { printf "${YELLOW}  [!]${RESET} %s\n" "$1"; }
error() { printf "${RED}  [x]${RESET} %s\n" "$1"; exit 1; }

print_header

# ── Detect OS + arch ─────────────────────────────────────────
OS="$(uname -s)"; ARCH="$(uname -m)"
case "$OS" in
  Darwin)
    case "$ARCH" in
      arm64|x86_64) ASSET="pseudo-macos-universal" ;;
      *) error "Unsupported macOS arch: $ARCH" ;;
    esac ;;
  Linux)
    case "$ARCH" in
      x86_64)        ASSET="pseudo-linux-x64"   ;;
      aarch64|arm64) ASSET="pseudo-linux-arm64" ;;
      *) error "Unsupported Linux arch: $ARCH" ;;
    esac ;;
  *) error "Unsupported OS: $OS. Use install.ps1 on Windows." ;;
esac
info "Detected: $OS / $ARCH → $ASSET"

# ── Resolve download URL ──────────────────────────────────────
step "Resolving release URL..."
if [ "$PSEUDO_VERSION" = "latest" ]; then
  BASE_URL="https://github.com/$REPO/releases/latest/download"
else
  BASE_URL="https://github.com/$REPO/releases/download/v$PSEUDO_VERSION"
fi
DOWNLOAD_URL="$BASE_URL/$ASSET"
info "URL: $DOWNLOAD_URL"

# ── Pick downloader ───────────────────────────────────────────
if command -v curl &>/dev/null; then   DL="curl"
elif command -v wget &>/dev/null; then DL="wget"
else error "curl or wget is required. Please install one."; fi

# ── Create install dir & download ────────────────────────────
step "Creating install directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
DEST="$INSTALL_DIR/pseudo"

step "Downloading $ASSET..."
TMP="$(mktemp)"
if [ "$DL" = "curl" ]; then
  curl -fSL --progress-bar "$DOWNLOAD_URL" -o "$TMP" || \
    error "Download failed. Check: https://github.com/$REPO/releases"
else
  wget -q --show-progress "$DOWNLOAD_URL" -O "$TMP" || \
    error "Download failed. Check: https://github.com/$REPO/releases"
fi
chmod +x "$TMP"
mv "$TMP" "$DEST"
info "Installed: $DEST ($(du -sh "$DEST" 2>/dev/null | cut -f1 || echo '?'))"

# ── Add to PATH ───────────────────────────────────────────────
step "Adding $INSTALL_DIR to PATH..."

add_to_path() {
  local F="$1"
  local LINE="export PATH=\"$INSTALL_DIR:\$PATH\""
  [ -f "$F" ] || return
  if grep -qF "$INSTALL_DIR" "$F" 2>/dev/null; then
    info "Already in $F"
  else
    printf '\n# Added by Pseudo installer\n%s\n' "$LINE" >> "$F"
    info "Added PATH entry to $F"
  fi
}

add_to_path "$HOME/.bashrc"
add_to_path "$HOME/.bash_profile"
add_to_path "$HOME/.zshrc"
add_to_path "$HOME/.profile"

export PATH="$INSTALL_DIR:$PATH"   # active in this session immediately

# ── Verify ───────────────────────────────────────────────────
step "Verifying..."
if VER=$("$DEST" version 2>/dev/null); then
  info "Installed: $VER"
else
  warn "Binary is at $DEST - try: $DEST version"
fi

# ── Done ─────────────────────────────────────────────────────
printf "\n${GREEN}  ╔═══════════════════════════════════════════╗${RESET}\n"
printf "${GREEN}  ║   Pseudo installed successfully!   🎉    ║${RESET}\n"
printf "${GREEN}  ╚═══════════════════════════════════════════╝${RESET}\n\n"
printf "  ${BOLD}Restart your terminal, then:${RESET}\n"
printf "  ${CYAN}  pseudo version${RESET}\n"
printf "  ${CYAN}  pseudo run hello.pseudo${RESET}\n\n"
printf "  ${DIM}Or source now:  source ~/.bashrc  (bash) / source ~/.zshrc  (zsh)${RESET}\n"
printf "  ${DIM}Docs: https://pseudo.wiki${RESET}\n\n"
