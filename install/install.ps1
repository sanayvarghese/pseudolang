# Pseudo Installer for Windows (PowerShell)
# Hosted at: https://pseudo.wiki/install.ps1
# Usage: iwr -useb https://pseudo.wiki/install.ps1 | iex

param(
    [string]$Version    = "latest",
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\pseudo",
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$REPO     = "sanayvarghese/pseudolang"
$BIN_NAME = "pseudo.exe"

function Print-Header {
    Write-Host ""
    Write-Host "  ██████╗ ███████╗███████╗██╗   ██╗██████╗  ██████╗ " -ForegroundColor Cyan
    Write-Host "  ██╔══██╗██╔════╝██╔════╝██║   ██║██╔══██╗██╔═══██╗" -ForegroundColor Cyan
    Write-Host "  ██████╔╝█████╗  ███████╗██║   ██║██║  ██║██║   ██║" -ForegroundColor Cyan
    Write-Host "  ██╔═══╝ ██╔══╝  ╚════██║██║   ██║██║  ██║██║   ██║" -ForegroundColor Cyan
    Write-Host "  ██║     ███████╗███████║╚██████╔╝██████╔╝╚██████╔╝" -ForegroundColor Cyan
    Write-Host "  ╚═╝     ╚══════╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ " -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Write pseudocode. Actually run it." -ForegroundColor Yellow
    Write-Host "  No Python required — standalone binary." -ForegroundColor DarkGray
    Write-Host ""
}

function Step  { param($m) Write-Host "  [*] $m" -ForegroundColor Green }
function Info  { param($m) Write-Host "  [i] $m" -ForegroundColor Cyan }
function Warn  { param($m) Write-Host "  [!] $m" -ForegroundColor Yellow }
function Err   { param($m) Write-Host "  [x] $m" -ForegroundColor Red; exit 1 }

if ($Help) {
    Print-Header
    Write-Host "  Options:"
    Write-Host "    -Version <tag>      Specific release (default: latest)"
    Write-Host "    -InstallDir <path>  Where to place pseudo.exe"
    Write-Host "    -Help               This message"
    exit 0
}

Print-Header

# ── Resolve download URL ──────────────────────────────────────
Step "Resolving download URL..."
$BaseUrl     = if ($Version -eq "latest") {
    "https://github.com/$REPO/releases/latest/download"
} else {
    "https://github.com/$REPO/releases/download/v$Version"
}
$DownloadUrl = "$BaseUrl/pseudo-windows-x64.exe"
Info "URL: $DownloadUrl"

# ── Create install directory ──────────────────────────────────
Step "Creating install directory: $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$DestPath = Join-Path $InstallDir $BIN_NAME

# ── Download binary ───────────────────────────────────────────
Step "Downloading pseudo.exe..."
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $DestPath -UseBasicParsing
} catch {
    Err "Download failed: $_`n  Check: https://github.com/$REPO/releases"
}
$size = [math]::Round((Get-Item $DestPath).Length / 1MB, 1)
Info "Downloaded: $DestPath ($size MB)"

# ── Add to User PATH (no admin required) ─────────────────────
Step "Adding $InstallDir to your PATH..."
$RegPath = 'HKCU:\Environment'
$OldPath = (Get-ItemProperty -Path $RegPath -Name Path -ErrorAction SilentlyContinue).Path
$OldPath = if ($OldPath) { $OldPath } else { "" }

if ($OldPath -notlike "*$InstallDir*") {
    $NewPath = ($OldPath.TrimEnd(';') + ";$InstallDir").TrimStart(';')
    Set-ItemProperty -Path $RegPath -Name Path -Value $NewPath

    # Broadcast environment change to open terminals
    $sig = '[DllImport("user32.dll",CharSet=CharSet.Auto)]public static extern IntPtr SendMessageTimeout(IntPtr h,uint m,UIntPtr w,string l,uint f,uint t,out UIntPtr r);'
    $t = Add-Type -MemberDefinition $sig -Name "WinMsg" -Namespace "Pseudo" -PassThru -ErrorAction SilentlyContinue
    if ($t) {
        $r = [UIntPtr]::Zero
        $t::SendMessageTimeout([IntPtr]0xffff, 0x1A, [UIntPtr]::Zero, "Environment", 2, 5000, [ref]$r) | Out-Null
    }
    Info "PATH updated. Open a new terminal to use 'pseudo' anywhere."
} else {
    Info "$InstallDir is already in PATH."
}

# Make pseudo available in this session immediately
$env:PATH = "$env:PATH;$InstallDir"

# ── Verify ───────────────────────────────────────────────────
Step "Verifying..."
try {
    $ver = & $DestPath version 2>&1
    Info "Installed: $ver"
} catch {
    Warn "Binary is at $DestPath — open a new terminal and run: pseudo version"
}

# ── Done ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔═══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║   Pseudo installed successfully!   🎉    ║" -ForegroundColor Green
Write-Host "  ╚═══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Open a new terminal, then:" -ForegroundColor White
Write-Host "    pseudo version" -ForegroundColor Cyan
Write-Host "    pseudo run hello.pseudo" -ForegroundColor Cyan
Write-Host "    pseudo init" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Docs: https://pseudo.wiki" -ForegroundColor DarkCyan
Write-Host ""
