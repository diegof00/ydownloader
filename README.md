# YDownloader

Una aplicación de escritorio simple para descargar videos y audio desde múltiples sitios web.

![Python](https://img.shields.io/badge/Python-3.13.2+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Características

- 🎬 **Descarga de Video**: Descarga videos en formato MP4
- 🎵 **Descarga de Audio**: Extrae solo el audio en formato MP3
- 📊 **Progreso en Tiempo Real**: Barra de progreso y estados claros
- ❌ **Cancelación**: Cancela descargas en cualquier momento
- 📜 **Historial**: Mantiene registro de las últimas 5 descargas
- 🌐 **Multiplataforma**: Funciona en Windows, macOS y Linux
- 🎯 **Fácil de Usar**: Interfaz simple para usuarios no técnicos

## Requisitos del Sistema

| Dependencia | Versión | Propósito |
|-------------|---------|-----------|
| Python | 3.13.2+ | Runtime de la aplicación |
| Tkinter | (incluido) | Interfaz gráfica |
| FFmpeg | Última | Conversión de audio/video (OBLIGATORIO) |

## Instalación por Sistema Operativo

### 🍎 macOS

```bash
# 1. Instalar Homebrew (si no lo tienes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar FFmpeg (OBLIGATORIO)
brew install ffmpeg

# 3. Instalar Python (opción A: oficial - RECOMENDADO)
# Descargar de https://www.python.org/downloads/ e instalar

# 3. Instalar Python (opción B: pyenv)
# Ver instrucciones detalladas en specs/001-media-downloader/quickstart.md

# 4. Verificar instalación
python3 -c "import tkinter; print('Tkinter OK')"
ffmpeg -version

# 5. Clonar e instalar YDownloader
git clone https://github.com/diegof00/ydownloader.git
cd ydownloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 6. Ejecutar
python -m src
```

### 🪟 Windows

```powershell
# 1. Descargar e instalar Python 3.13.2+
#    https://www.python.org/downloads/
#    ⚠️ IMPORTANTE: Marcar "Add Python to PATH" durante instalación

# 2. Instalar FFmpeg (OBLIGATORIO)
#    a) Descargar de https://www.gyan.dev/ffmpeg/builds/ (essentials build)
#    b) Extraer a C:\ffmpeg
#    c) Agregar C:\ffmpeg\bin al PATH:
#       - Buscar "Variables de entorno" en Windows
#       - Editar "Path" en variables del sistema
#       - Agregar: C:\ffmpeg\bin

# 3. Verificar instalación (PowerShell)
python -c "import tkinter; print('Tkinter OK')"
ffmpeg -version

# 4. Clonar e instalar YDownloader
git clone https://github.com/diegof00/ydownloader.git
cd ydownloader
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 5. Ejecutar
python -m src
```

### 🐧 Linux (Ubuntu/Debian)

```bash
# 1. Instalar Python y Tkinter
sudo apt update
sudo apt install python3 python3-venv python3-tk

# 2. Instalar FFmpeg (OBLIGATORIO)
sudo apt install ffmpeg

# 3. Verificar instalación
python3 -c "import tkinter; print('Tkinter OK')"
ffmpeg -version

# 4. Clonar e instalar YDownloader
git clone https://github.com/diegof00/ydownloader.git
cd ydownloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Ejecutar
python -m src
```

### 🐧 Linux (Fedora/RHEL)

```bash
# 1. Instalar Python y Tkinter
sudo dnf install python3 python3-tkinter

# 2. Instalar FFmpeg (OBLIGATORIO)
sudo dnf install ffmpeg

# 3. Verificar instalación
python3 -c "import tkinter; print('Tkinter OK')"
ffmpeg -version

# 4. Clonar e instalar YDownloader
git clone https://github.com/diegof00/ydownloader.git
cd ydownloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Ejecutar
python -m src
```

## Uso

1. **Pega la URL** del video o audio que deseas descargar
2. **Selecciona la carpeta** de destino (o usa la predeterminada)
3. **Elige el formato**: Video o Audio
4. **Haz clic en Descargar**
5. Espera a que termine (puedes cancelar en cualquier momento)

## Solución de Problemas

### "FFmpeg is not installed"

FFmpeg es **OBLIGATORIO**. Instálalo según tu sistema operativo (ver arriba).

### "No module named '_tkinter'"

- **macOS con pyenv**: Ver [instrucciones detalladas](specs/001-media-downloader/quickstart.md)
- **Linux**: `sudo apt install python3-tk` o `sudo dnf install python3-tkinter`
- **Windows**: Reinstalar Python desde python.org (Tkinter viene incluido)

### "yt-dlp errors" o sitios que no funcionan

```bash
pip install --upgrade yt-dlp
```

## Desarrollo

### Estructura del Proyecto

```
src/
├── ui/           # Interfaz gráfica (CustomTkinter)
├── domain/       # Lógica de negocio
└── infra/        # Adaptadores externos (yt-dlp, filesystem)

tests/
├── unit/         # Tests unitarios
└── integration/  # Tests de integración
```

### Ejecutar Tests

```bash
python -m pytest tests/ -v
```

Las pruebas de integración usan un clip sintético servido por HTTP local y
requieren `ffmpeg` y `ffprobe`. Para incluir el flujo de interfaz en Linux:

```bash
YDOWNLOADER_TEST_GUI=1 xvfb-run -a python -m pytest tests/
```

Ver [revisión y límites de validación](REVIEW.md), incluida la comprobación de YouTube.

### Linting

```bash
ruff check src/ tests/
```

## Aviso Legal

Esta herramienta facilita la descarga de contenido multimedia. **El usuario es responsable de verificar que tiene los permisos necesarios** para descargar y usar el contenido.

No utilices esta herramienta para infringir derechos de autor.

## Licencia

MIT License - ver [LICENSE.md](LICENSE.md) para más detalles.
