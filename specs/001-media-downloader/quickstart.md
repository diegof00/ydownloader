# Quickstart: Media Downloader Desktop App

**Date**: 2026-01-14  
**Plan**: [plan.md](./plan.md)

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.13.2+ | With Tkinter support |
| FFmpeg | Latest | **REQUIRED** for audio/video processing |
| pip | Latest | Python package manager |

## System Setup by OS

### 🍎 macOS

#### Option A: Official Python (Recommended)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Install FFmpeg:
   ```bash
   brew install ffmpeg
   ```
3. Verify:
   ```bash
   python3 -c "import tkinter; print('Tkinter OK')"
   ffmpeg -version
   ```

#### Option B: pyenv (Advanced)

If using pyenv, Python must be compiled with Tcl/Tk support:

```bash
# 1. Install tcl-tk via Homebrew
brew install tcl-tk ffmpeg

# 2. Set environment variables for Tcl/Tk 9.x
export LDFLAGS="-L$(brew --prefix tcl-tk)/lib"
export CPPFLAGS="-I$(brew --prefix tcl-tk)/include"
export PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig"
export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' \
  --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl9.0 -ltk9.0'"

# 3. Install Python
pyenv install 3.13.2

# 4. Verify Tcl version (should show 9.x)
python3 -c "import tkinter; print(tkinter.Tcl().eval('info patchlevel'))"
```

### 🪟 Windows

1. **Download Python 3.13.2+** from [python.org](https://www.python.org/downloads/)
   - ⚠️ Check **"Add Python to PATH"** during installation
   - Tkinter is included automatically

2. **Install FFmpeg**:
   - Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (essentials build)
   - Extract to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to system PATH:
     - Search "Environment Variables" in Windows
     - Edit "Path" → New → `C:\ffmpeg\bin`

3. **Verify** (PowerShell):
   ```powershell
   python -c "import tkinter; print('Tkinter OK')"
   ffmpeg -version
   ```

### 🐧 Linux (Ubuntu/Debian)

```bash
# Install all dependencies
sudo apt update
sudo apt install python3 python3-venv python3-tk ffmpeg

# Verify
python3 -c "import tkinter; print('Tkinter OK')"
ffmpeg -version
```

### 🐧 Linux (Fedora/RHEL)

```bash
# Install all dependencies
sudo dnf install python3 python3-tkinter ffmpeg

# Verify
python3 -c "import tkinter; print('Tkinter OK')"
ffmpeg -version
```

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/diegof00/ydownloader.git
cd ydownloader
```

### 2. Verify Prerequisites

```bash
# Both must succeed
python3 -c "import tkinter; print('Tkinter OK')"
ffmpeg -version
```

### 3. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python -m src
```

### 6. Run Tests

```bash
pytest tests/ -v
```

### 7. Run Linting

```bash
ruff check src/ tests/
```

## Project Structure

```
ydownloader/
├── src/
│   ├── __main__.py      # Entry point
│   ├── app.py           # Application bootstrap
│   ├── ui/              # GUI components (CustomTkinter)
│   ├── domain/          # Business logic
│   └── infra/           # External adapters (yt-dlp, filesystem)
├── tests/
│   ├── unit/            # Unit tests for domain
│   └── integration/     # Integration tests
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project config
└── README.md            # User documentation
```

## Quick Validation Checklist

After setup, verify:

- [ ] `python -m src` opens the application window
- [ ] Window shows: URL input, folder picker, format selector, download button
- [ ] Pasting a YouTube URL and clicking download starts the process
- [ ] Progress bar updates during download
- [ ] Cancel button stops the download
- [ ] History shows completed download
- [ ] Close confirmation appears if download is in progress

## Common Issues

### "FFmpeg is not installed"

FFmpeg is **required** for yt-dlp to merge video and audio streams:

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg` |
| Windows | [Download from gyan.dev](https://www.gyan.dev/ffmpeg/builds/) |

### "No module named '_tkinter'"

Python was compiled without Tkinter support:

| OS | Solution |
|----|----------|
| macOS (pyenv) | See pyenv setup above (compile with tcl-tk) |
| Ubuntu/Debian | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| Windows | Reinstall from python.org |

### "yt-dlp errors" or sites not working

```bash
pip install --upgrade yt-dlp
```

## Development Commands

| Command | Description |
|---------|-------------|
| `python -m src` | Run the application |
| `pytest tests/` | Run all tests |
| `pytest tests/unit/` | Run unit tests only |
| `pytest --cov=src` | Run tests with coverage |
| `ruff check .` | Check linting |
| `ruff check . --fix` | Auto-fix linting issues |

## Building Executable (Future Phase)

```bash
pyinstaller --onefile --windowed --name YDownloader src/__main__.py
```

Output: `dist/YDownloader` (macOS/Linux) or `dist/YDownloader.exe` (Windows)
