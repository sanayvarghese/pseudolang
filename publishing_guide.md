# Pseudo Publishing Guide

This guide details how to publish the **Pseudo** project to **GitHub** and **PyPI (pip)**, explains the repository architecture, and describes how the automated release pipeline functions.

---

## 📂 Directory Layout

To separate repository configuration/docs from the Python package source, the project is structured using the industry-standard **src/subdirectory** layout:

```text
pseudolang/                   ← Repository root folder (d:\Coding\work\pesudo\pseudolang)
├── .github/
│   └── workflows/
│       └── release.yml       ← GitHub Actions Release CI workflow
├── docs/                     ← Documentation (Next.js app, hosted as pseudo.wiki)
│   └── public/
│       ├── install.ps1       ← served at pseudo.wiki/install.ps1
│       └── install.sh        ← served at pseudo.wiki/install.sh
├── install/                  ← Local copies of the installation scripts
│   ├── install.ps1
│   └── install.sh
├── dist/                     ← Windows compiled executable (pseudo.exe)
├── pseudo/                   ← Python Package source code (DO NOT mix with root files!)
│   ├── __init__.py           ← Package entrypoint (holds __version__)
│   ├── __main__.py           ← CLI entrypoint wrapper
│   ├── cli.py                ← Argument parsing and CLI command handling
│   ├── compiler.py           ← Compiler/Interpreter pipeline coordination
│   ├── install.py            ← ~/.pseudo/ configuration and environment set up
│   ├── data/
│   │   └── default.pmap      ← Bundled default language mapping file
│   ├── analyzer/             ← Semantic analyzer & static complexity analyzer
│   ├── interpreter/          ← Tree-walking interpreter & built-in data structures
│   ├── parser/               ← Lexer, tokenizer, parser and expression parser
│   └── resolver/             ← Two-pass resolution and pmap loader
├── .gitignore                ← Specifies files untracked by Git (like build/ and dist/)
├── pseudo.spec               ← PyInstaller executable configuration spec file
├── pseudo_entry.py           ← Executable entrypoint (used by PyInstaller)
├── pyproject.toml            ← PyPI/pip build system configuration
├── README.md                 ← Main project documentation
└── publishing_guide.md       ← This guide
```

---

## 🛠 What is the `.spec` File?

The `pseudo.spec` file is a **PyInstaller configuration script**. It is written in Python syntax and controls how the standalone executable is built:

- **Analysis**: Finds all dependencies starting from `pseudo_entry.py`.
- **Datas**: Specifies static assets to copy into the binary-namely `('pseudo/data/default.pmap', 'pseudo/data')`.
- **Hidden Imports**: Forces PyInstaller to include dynamically imported submodules (like `pseudo.interpreter.interpreter` or `pseudo.parser.tokenizer`) that the static analyzer might otherwise miss.
- **EXE**: Combines the script, compiled python modules, and resource files into a single, executable file (`pseudo.exe`).

If you ever need to rebuild the executable locally on Windows, simply run:

```bash
pyinstaller pseudo.spec
```

This is faster and more reliable than specifying all options as CLI flags every time.

---

## 🌐 1. Publishing to GitHub

Follow these steps to initialize your Git repository locally and publish it to the **public** repo `sanayvarghese/pseudolang`:

```bash
# 1. Open your terminal in the root folder (d:\Coding\work\pesudo\pseudolang)
cd d:\Coding\work\pesudo\pseudolang

# 2. Initialize git repository
git init

# 3. Add all files to staging (tracked files defined in .gitignore will be ignored)
git add .

# 4. Commit files
git commit -m "feat: initial commit with restructured layout and workflows"

# 5. Create main branch and link to your public GitHub repo
git branch -M main
git remote add origin https://github.com/sanayvarghese/pseudolang.git

# 6. Push to GitHub
git push -u origin main
```

---

## 📦 2. Publishing to PyPI (pip)

To publish the `pseudo` package to PyPI so users can install it via `pip install runpseudo`, follow these steps:

### Step A: Install Publishing Tools

You will need `build` (to generate the package distributions) and `twine` (to securely upload them).

```bash
pip install --upgrade build twine
```

### Step B: Create a PyPI Account & Generate an API Token

1. Go to [PyPI](https://pypi.org/) and register an account.
2. Go to **Account Settings** → **API Tokens** → **Add API Token**.
3. Set the Scope to **Entire Account** (or a specific project if updating).
4. **Copy the token.** It starts with `pypi-`. _Keep it secret._

### Step C: Build the Package

From the root directory (`d:\Coding\work\pesudo\pseudolang`), run:

```bash
python -m build
```

This generates two files inside a new `dist/` folder:

- A source archive: `dist/runpseudo-0.1.2.tar.gz`
- A built wheel: `dist/runpseudo-0.1.2-py3-none-any.whl`

### Step D: Upload to PyPI

Use `twine` to upload the built packages:

```bash
python -m twine upload dist/*
```

- **Username**: Use `__token__` (literally).
- **Password**: Paste your PyPI API token (including the `pypi-` prefix).

Once completed, anyone can install your project using:

```bash
pip install runpseudo
```

---

## 🤖 3. How the Automated GitHub Release Works

We have configured a GitHub Actions workflow (`.github/workflows/release.yml`) to automatically compile and release executables for **Windows, macOS (Universal), and Linux** whenever you push a version tag.

### The Release Workflow

When you push a tag like `v0.1.2`:

1. **Parallel Build Runners**:
   - `ubuntu-latest` compiles `pseudo-linux-x64`
   - `macos-latest` compiles `pseudo-macos-universal` (Universal Mac binary)
   - `windows-latest` compiles `pseudo-windows-x64.exe` (Windows)
2. **Smoke Test**: Each runner executes `pseudo version` to verify the compiled binary functions properly.
3. **Draft Release**: Collects all 4 binaries, bundles them, and creates a release on your GitHub repository.

### How to trigger a new Release:

Whenever you release a new version:

```bash
# 1. Update the version inside pseudo/__init__.py:
#    __version__ = "1.0.1"

# 2. Commit the changes
git add .
git commit -m "chore: release version v1.0.1"

# 3. Create a Git Tag
git tag v1.0.1

# 4. Push code and tag to GitHub
git push origin main
git push origin --tags
```

Once the Actions run finishes, your release will be live, and the download scripts at `pseudo.wiki/install.ps1`/`install.sh` will fetch the latest binaries automatically.
