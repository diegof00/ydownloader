# Internal Interfaces: Media Downloader

**Date**: 2026-01-13  
**Plan**: [../plan.md](../plan.md)

Este documento define los contratos entre capas de la arquitectura. No hay API externa (es una app de escritorio), pero estas interfaces permiten testing y desacoplamiento.

## Layer Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                        UI Layer                          │
│  (CustomTkinter widgets, event handlers)                │
│                                                          │
│  Depends on: DownloadServiceProtocol, callbacks         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                        │
│  (DownloadService, URLValidator, Models)                │
│                                                          │
│  Depends on: DownloaderProtocol, StorageProtocol        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      Infra Layer                         │
│  (YtdlpAdapter, FileSystem, ConfigStore, HistoryStore) │
│                                                          │
│  Implements: DownloaderProtocol, StorageProtocol        │
└─────────────────────────────────────────────────────────┘
```

## Protocols (Interfaces)

### DownloaderProtocol

Contrato para el adaptador de descarga. Implementado por `YtdlpAdapter`.

```python
from typing import Protocol, Callable, Optional
from pathlib import Path
from domain.models import DownloadFormat, DownloadStatus

class DownloadProgress:
    """Información de progreso de descarga."""
    percent: int              # 0-100
    status: DownloadStatus
    title: Optional[str]      # Título extraído del contenido
    eta: Optional[int]        # Segundos restantes estimados
    speed: Optional[str]      # Velocidad legible (ej: "1.5 MiB/s")

class DownloaderProtocol(Protocol):
    def download(
        self,
        url: str,
        output_folder: Path,
        format: DownloadFormat,
        on_progress: Callable[[DownloadProgress], None],
    ) -> Path:
        """
        Descarga contenido desde URL.
        
        Args:
            url: URL del contenido a descargar
            output_folder: Carpeta donde guardar el archivo
            format: VIDEO o AUDIO
            on_progress: Callback para reportar progreso
            
        Returns:
            Path del archivo descargado
            
        Raises:
            DownloadError: Si la descarga falla
            CancelledException: Si se canceló
        """
        ...
    
    def cancel(self) -> None:
        """Cancela la descarga en curso."""
        ...
    
    def validate_url(self, url: str) -> tuple[bool, str]:
        """
        Valida si la URL es soportada.
        
        Returns:
            (is_valid, error_message)
        """
        ...
```

### HistoryStorageProtocol

Contrato para persistencia del historial. Implementado por `HistoryStore`.

```python
from typing import Protocol
from domain.models import HistoryEntry

class HistoryStorageProtocol(Protocol):
    def load(self) -> list[HistoryEntry]:
        """Carga el historial desde almacenamiento."""
        ...
    
    def save(self, entries: list[HistoryEntry]) -> None:
        """Guarda el historial en almacenamiento."""
        ...
    
    def add(self, entry: HistoryEntry) -> None:
        """
        Agrega una entrada al historial.
        Mantiene máximo 5 entradas (elimina la más antigua si es necesario).
        """
        ...
    
    def clear(self) -> None:
        """Borra todo el historial."""
        ...
```

### ConfigStorageProtocol

Contrato para persistencia de configuración. Implementado por `ConfigStore`.

```python
from typing import Protocol, Optional
from pathlib import Path
from domain.models import DownloadFormat

class ConfigStorageProtocol(Protocol):
    def get_last_output_folder(self) -> Optional[Path]:
        """Retorna la última carpeta de salida, o None si no hay."""
        ...
    
    def set_last_output_folder(self, folder: Path) -> None:
        """Guarda la última carpeta de salida."""
        ...
    
    def get_default_format(self) -> DownloadFormat:
        """Retorna el formato por defecto."""
        ...
    
    def set_default_format(self, format: DownloadFormat) -> None:
        """Guarda el formato por defecto."""
        ...
    
    def should_show_disclaimer(self) -> bool:
        """Retorna True si debe mostrarse el disclaimer."""
        ...
    
    def mark_disclaimer_shown(self) -> None:
        """Marca el disclaimer como mostrado."""
        ...
```

### FileSystemProtocol

Contrato para operaciones de filesystem. Implementado por `FileSystem`.

```python
from typing import Protocol
from pathlib import Path

class FileSystemProtocol(Protocol):
    def can_write(self, folder: Path) -> bool:
        """Verifica si se puede escribir en la carpeta."""
        ...
    
    def get_available_space(self, folder: Path) -> int:
        """Retorna espacio disponible en bytes."""
        ...
    
    def delete_file(self, path: Path) -> bool:
        """Elimina un archivo. Retorna True si se eliminó."""
        ...
    
    def get_unique_filename(self, folder: Path, base_name: str, extension: str) -> Path:
        """
        Genera un nombre de archivo único.
        Si existe "video.mp4", retorna "video (1).mp4".
        """
        ...
    
    def get_downloads_folder(self) -> Path:
        """Retorna la carpeta de Downloads del sistema."""
        ...
    
    def get_app_data_folder(self) -> Path:
        """Retorna la carpeta de datos de la aplicación."""
        ...
```

## Callback Contracts

### Progress Callback (UI → Domain)

```python
# Tipo de callback que la UI pasa al DownloadService
ProgressCallback = Callable[[int, DownloadStatus, Optional[str]], None]
# Args: (percent, status, title)

# Uso en UI:
def on_progress(percent: int, status: DownloadStatus, title: Optional[str]):
    self.progress_bar.set(percent / 100)
    self.status_label.configure(text=status.value)
    if title:
        self.title_label.configure(text=title)
```

### Completion Callback (UI → Domain)

```python
# Callback cuando la descarga termina (éxito o error)
CompletionCallback = Callable[[Download], None]

# Uso en UI:
def on_complete(download: Download):
    if download.status == DownloadStatus.COMPLETED:
        self.show_success(download)
    elif download.status == DownloadStatus.ERROR:
        self.show_error(download.error_message)
```

## Error Contracts

### Domain Exceptions

```python
class DomainError(Exception):
    """Base para errores de dominio."""
    def __init__(self, message: str, user_message: str):
        super().__init__(message)
        self.user_message = user_message  # Mensaje amigable para mostrar

class InvalidURLError(DomainError):
    """URL con formato inválido."""
    pass

class UnsupportedSiteError(DomainError):
    """Sitio no soportado por yt-dlp."""
    pass

class DownloadError(DomainError):
    """Error durante la descarga."""
    pass

class PermissionError(DomainError):
    """Sin permisos de escritura."""
    pass

class DiskSpaceError(DomainError):
    """Espacio insuficiente en disco."""
    pass

class CancelledException(DomainError):
    """Descarga cancelada por el usuario."""
    pass

class ContentUnavailableError(DomainError):
    """Contenido no disponible o eliminado."""
    pass
```

## Event Flow Example

```
1. User clicks "Descargar"
   UI → DownloadService.start_download(url, folder, format, on_progress, on_complete)

2. DownloadService validates URL
   DownloadService → URLValidator.validate(url)
   
3. If invalid, error callback
   DownloadService → on_error("URL inválida")
   UI updates error message

4. If valid, create Download and delegate to adapter
   DownloadService → YtdlpAdapter.download(url, folder, format, internal_progress)

5. Adapter reports progress
   YtdlpAdapter → internal_progress(DownloadProgress)
   DownloadService → on_progress(percent, status, title)
   UI updates progress bar

6. On completion
   YtdlpAdapter returns → DownloadService updates Download
   DownloadService → HistoryStore.add(entry)
   DownloadService → on_complete(download)
   UI shows success/error
```
