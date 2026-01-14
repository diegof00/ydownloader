# Research: Media Downloader Desktop App

**Date**: 2026-01-13  
**Plan**: [plan.md](./plan.md)

## Decisions

### 1. GUI Framework: CustomTkinter

**Decision**: Usar CustomTkinter como framework GUI principal.

**Rationale**:
- Basado en Tkinter (incluido en Python stdlib), pero con apariencia moderna
- Temas claros/oscuros automáticos según sistema operativo
- Widgets modernos sin dependencias pesadas como Qt
- Compatible con PyInstaller para empaquetado
- Licencia MIT, sin restricciones comerciales

**Alternatives Considered**:
- **Tkinter estándar**: Funcional pero apariencia anticuada (rechazado por UX)
- **PyQt/PySide**: Más potente pero licencia compleja (GPL/LGPL) y mayor tamaño de bundle
- **wxPython**: Buena portabilidad pero API menos intuitiva
- **Dear PyGui**: Rendimiento GPU pero menos widgets estándar

### 2. Motor de Descarga: yt-dlp (bundled)

**Decision**: Usar yt-dlp como librería Python, bundled con la aplicación.

**Rationale**:
- Soporta 1000+ sitios de video/audio
- API Python nativa (no requiere subprocess para funcionalidad básica)
- Activamente mantenido (fork de youtube-dl)
- Hooks de progreso para actualizar UI en tiempo real
- Puede bundlearse con PyInstaller

**Integration Pattern**:
```python
import yt_dlp

ydl_opts = {
    'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
    'outtmpl': str(output_path / '%(title)s.%(ext)s'),
    'progress_hooks': [progress_callback],
    'postprocessors': [...] if audio_only else [],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
```

**Alternatives Considered**:
- **youtube-dl**: Menos mantenido, yt-dlp es el sucesor activo
- **pytube**: Solo YouTube, menos formatos
- **requests manual**: Requiere implementar parsing de cada sitio

### 3. Threading Model: threading.Thread + Queue

**Decision**: Usar `threading.Thread` con `queue.Queue` para comunicación UI-worker.

**Rationale**:
- CustomTkinter/Tkinter requiere que modificaciones de UI ocurran en main thread
- Thread separado para descarga, Queue para enviar actualizaciones de progreso
- `after()` de Tkinter para polling seguro de la Queue desde main thread
- Patrón simple y probado, sin dependencias adicionales

**Pattern**:
```python
import threading
import queue

class DownloadWorker(threading.Thread):
    def __init__(self, url, output_path, progress_queue):
        super().__init__(daemon=True)
        self.url = url
        self.output_path = output_path
        self.progress_queue = progress_queue
        self._cancel_event = threading.Event()
    
    def run(self):
        # Download logic, put updates in queue
        self.progress_queue.put(('progress', 50))
    
    def cancel(self):
        self._cancel_event.set()
```

**Alternatives Considered**:
- **asyncio**: Más complejo de integrar con Tkinter event loop
- **concurrent.futures**: Similar a threading, pero Thread ofrece más control para cancelación
- **multiprocessing**: Overkill para una sola descarga, complejidad de IPC

### 4. Persistencia: JSON Local

**Decision**: Usar archivos JSON en directorio de usuario para historial y configuración.

**Rationale**:
- Suficiente para 5 registros de historial + configuración simple
- No requiere dependencias (json en stdlib)
- Fácil de inspeccionar/debuggear
- Portable entre sistemas operativos
- Fácil de borrar por el usuario (Principio VIII)

**Storage Location**:
- Windows: `%APPDATA%\YDownloader\`
- macOS: `~/Library/Application Support/YDownloader/`
- Linux: `~/.config/ydownloader/`

**Alternatives Considered**:
- **SQLite**: Overkill para 5 registros, añade complejidad
- **pickle**: Inseguro, no legible
- **YAML/TOML**: Requiere dependencia adicional

### 5. Validación de URLs

**Decision**: Validación en dos fases: formato básico + verificación con yt-dlp.

**Rationale**:
- Fase 1: `urllib.parse` para validar estructura básica (schema, netloc)
- Fase 2: `yt_dlp.extractor` para verificar si el sitio está soportado
- Mensajes de error diferenciados: "URL inválida" vs "Sitio no soportado"

**Pattern**:
```python
from urllib.parse import urlparse
import yt_dlp

def validate_url(url: str) -> tuple[bool, str]:
    # Phase 1: Format validation
    try:
        result = urlparse(url)
        if not all([result.scheme in ('http', 'https'), result.netloc]):
            return False, "URL inválida"
    except Exception:
        return False, "URL inválida"
    
    # Phase 2: Extractor check
    extractors = yt_dlp.extractor.gen_extractors()
    for extractor in extractors:
        if extractor.suitable(url):
            return True, ""
    
    return False, "Sitio no soportado"
```

### 6. Empaquetado: PyInstaller

**Decision**: Usar PyInstaller para crear ejecutables standalone.

**Rationale**:
- Soporta Windows, macOS, Linux
- Puede incluir yt-dlp y ffmpeg como binarios bundled
- Un solo archivo ejecutable o directorio autocontenido
- Compatible con CustomTkinter

**Considerations for Design**:
- Evitar imports dinámicos que confundan a PyInstaller
- Usar `pathlib.Path` para recursos relativos
- Incluir hook para yt-dlp en spec file

**Alternatives Considered**:
- **cx_Freeze**: Similar pero menos mantenido
- **Nuitka**: Compilación a C, más complejo
- **py2exe**: Solo Windows

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| ¿Bundlear ffmpeg? | Sí, yt-dlp lo requiere para conversión a MP3 |
| ¿Formato de audio? | MP3 (128kbps default) por compatibilidad universal |
| ¿Formato de video? | MP4 (H.264) por compatibilidad universal |
| ¿Límite de tamaño? | Sin límite, pero advertir si >1GB |
