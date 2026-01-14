# Data Model: Media Downloader Desktop App

**Date**: 2026-01-13  
**Plan**: [plan.md](./plan.md)

## Entities

### Download

Representa una operación de descarga en curso o completada.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID único de la descarga |
| `url` | `str` | Yes | URL original proporcionada por el usuario |
| `title` | `str` | No | Título del contenido (extraído de metadata) |
| `output_path` | `Path` | Yes | Ruta completa del archivo destino |
| `format` | `DownloadFormat` | Yes | Formato seleccionado: VIDEO o AUDIO |
| `status` | `DownloadStatus` | Yes | Estado actual de la descarga |
| `progress` | `int` | Yes | Porcentaje de progreso (0-100) |
| `error_message` | `str` | No | Mensaje de error si status=ERROR |
| `started_at` | `datetime` | Yes | Timestamp de inicio |
| `completed_at` | `datetime` | No | Timestamp de finalización |

**Enums**:

```python
class DownloadFormat(Enum):
    VIDEO = "video"  # MP4 con video y audio
    AUDIO = "audio"  # Solo audio, MP3

class DownloadStatus(Enum):
    PENDING = "pending"        # Creado, no iniciado
    CONNECTING = "connecting"  # Conectando al servidor
    DOWNLOADING = "downloading" # Descarga en progreso
    PROCESSING = "processing"  # Post-procesamiento (conversión)
    COMPLETED = "completed"    # Finalizado exitosamente
    CANCELLED = "cancelled"    # Cancelado por el usuario
    ERROR = "error"            # Error durante la descarga
```

**State Transitions**:

```
PENDING → CONNECTING → DOWNLOADING → PROCESSING → COMPLETED
                ↓           ↓            ↓
              ERROR       ERROR        ERROR
                ↓           ↓            ↓
            CANCELLED   CANCELLED    CANCELLED
```

**Validation Rules**:
- `url` debe ser una URL válida con scheme http/https
- `progress` debe estar en rango [0, 100]
- `output_path` debe ser una ruta absoluta válida
- `completed_at` solo se establece cuando status es COMPLETED, CANCELLED, o ERROR

---

### HistoryEntry

Representa un registro en el historial de descargas (versión simplificada de Download para persistencia).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID de la descarga original |
| `title` | `str` | Yes | Título del contenido |
| `output_path` | `str` | Yes | Ruta del archivo (string para JSON) |
| `status` | `str` | Yes | Estado final: completed/cancelled/error |
| `format` | `str` | Yes | Formato: video/audio |
| `completed_at` | `str` | Yes | ISO 8601 timestamp |

**JSON Schema**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Video Tutorial",
  "output_path": "/Users/user/Downloads/Video Tutorial.mp4",
  "status": "completed",
  "format": "video",
  "completed_at": "2026-01-13T15:30:00Z"
}
```

**Business Rules**:
- Máximo 5 entradas en el historial
- Cuando se agrega la 6ta entrada, la más antigua se elimina (FIFO)
- Solo se agregan entradas cuando status es terminal (completed/cancelled/error)

---

### Settings

Preferencias de usuario persistidas entre sesiones.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `last_output_folder` | `str` | No | Downloads del usuario | Última carpeta seleccionada |
| `default_format` | `str` | No | "video" | Formato por defecto |
| `show_disclaimer` | `bool` | No | `true` | Mostrar disclaimer al iniciar |

**JSON Schema**:

```json
{
  "last_output_folder": "/Users/user/Downloads",
  "default_format": "video",
  "show_disclaimer": true
}
```

**Business Rules**:
- Si `last_output_folder` no existe o no tiene permisos, usar Downloads del sistema
- `show_disclaimer` se pone en `false` después de mostrar el disclaimer por primera vez

---

## Relationships

```
┌──────────────────┐
│     Settings     │
│  (1 instancia)   │
└──────────────────┘
         │
         │ provides default_format, last_output_folder
         ▼
┌──────────────────┐
│     Download     │
│ (1 a la vez)     │──────────────────┐
└──────────────────┘                  │
         │                            │
         │ on terminal status         │
         ▼                            │
┌──────────────────┐                  │
│  HistoryEntry    │                  │
│   (max 5)        │◄─────────────────┘
└──────────────────┘   creates entry from Download
```

## Storage Format

### history.json

```json
{
  "version": 1,
  "entries": [
    {
      "id": "...",
      "title": "...",
      "output_path": "...",
      "status": "completed",
      "format": "video",
      "completed_at": "..."
    }
  ]
}
```

### config.json

```json
{
  "version": 1,
  "last_output_folder": "/Users/user/Downloads",
  "default_format": "video",
  "show_disclaimer": false
}
```

## Domain Services

### DownloadService

Orquesta el proceso de descarga.

**Responsibilities**:
- Validar URL antes de iniciar
- Crear instancia de Download
- Delegar a infra adapter (yt-dlp)
- Emitir eventos de progreso
- Manejar cancelación
- Actualizar historial al completar

**Interface**:

```python
class DownloadService:
    def start_download(
        self,
        url: str,
        output_folder: Path,
        format: DownloadFormat,
        on_progress: Callable[[int, DownloadStatus], None],
        on_complete: Callable[[Download], None],
        on_error: Callable[[str], None],
    ) -> Download:
        """Inicia una descarga. Retorna el objeto Download creado."""
        ...
    
    def cancel_download(self, download_id: str) -> bool:
        """Cancela la descarga en curso. Retorna True si se canceló."""
        ...
    
    def get_current_download(self) -> Optional[Download]:
        """Retorna la descarga en curso, o None si no hay ninguna."""
        ...
```

### URLValidator

Valida URLs antes de intentar descarga.

**Interface**:

```python
class URLValidator:
    def validate(self, url: str) -> ValidationResult:
        """
        Valida una URL.
        Returns ValidationResult con is_valid y error_message.
        """
        ...

@dataclass
class ValidationResult:
    is_valid: bool
    error_message: str = ""
    error_code: str = ""  # "INVALID_FORMAT", "UNSUPPORTED_SITE", "EMPTY_URL"
```
