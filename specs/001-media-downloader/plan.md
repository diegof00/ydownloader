# Implementation Plan: Media Downloader Desktop App

**Branch**: `001-media-downloader` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-media-downloader/spec.md`

## Summary

Aplicación de escritorio GUI para descargar contenido de video/audio desde URLs. El usuario pega una URL, selecciona carpeta destino y formato (video/audio), ve el progreso en tiempo real, y puede cancelar. Incluye historial de las últimas 5 descargas con persistencia local.

**Enfoque técnico**: Arquitectura por capas (UI → Domain → Infra) con CustomTkinter para GUI, yt-dlp bundled para descargas, threading para operaciones en background, y JSON local para persistencia.

## Technical Context

**Language/Version**: Python 3.13.2+  
**Primary Dependencies**: CustomTkinter (GUI), yt-dlp (descargas, bundled)  
**Storage**: JSON local (`~/.ydownloader/history.json`, `~/.ydownloader/config.json`)  
**Testing**: pytest para tests unitarios  
**Target Platform**: Windows, macOS, Linux (desktop multiplataforma)  
**Project Type**: Single project (desktop app)  
**Performance Goals**: UI responsiva (<500ms), progreso actualizado cada 2s, cancelación <2s  
**Constraints**: Una descarga a la vez, historial limitado a 5 elementos, yt-dlp bundled  
**Scale/Scope**: Uso personal, single-user, sin servidor backend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Verificación |
|-----------|--------|--------------|
| I. UX Simple | ✅ PASS | Una pantalla, 3 clics máximo, controles esenciales |
| II. Non-Blocking UI | ✅ PASS | Threading para descargas, callbacks para actualizar UI |
| III. Validación y Errores | ✅ PASS | Validación de URLs, permisos, espacio; mensajes amigables |
| IV. Logging Visible | ✅ PASS | Área de estado en UI + logs técnicos opcionales |
| V. Seguridad | ✅ PASS | yt-dlp invocado con lista de args, no shell=True |
| VI. Calidad de Código | ✅ PASS | Estructura ui/domain/infra, tests para domain |
| VII. Portabilidad | ✅ PASS | CustomTkinter + pathlib, PyInstaller-ready |
| VIII. Responsabilidad Legal | ✅ PASS | Disclaimer en "Acerca de", botón limpiar historial |

**Gate Status**: ✅ ALL PASS - Proceder con Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-media-downloader/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal interfaces)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── __main__.py          # Entry point: python -m src
├── app.py               # Application bootstrap
│
├── ui/                  # Capa de presentación (CustomTkinter)
│   ├── __init__.py
│   ├── main_window.py   # Ventana principal
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── url_input.py      # Campo de entrada URL
│   │   ├── folder_picker.py  # Selector de carpeta
│   │   ├── format_selector.py # Toggle video/audio
│   │   ├── progress_bar.py   # Barra de progreso + estado
│   │   ├── download_button.py # Botón descargar/cancelar
│   │   └── history_panel.py  # Panel de historial
│   └── dialogs/
│       ├── __init__.py
│       ├── error_dialog.py   # Diálogos de error
│       └── about_dialog.py   # Disclaimer legal
│
├── domain/              # Lógica de negocio (sin I/O)
│   ├── __init__.py
│   ├── models.py        # Download, HistoryEntry, Settings
│   ├── download_service.py  # Orquestación de descargas
│   ├── validators.py    # Validación de URLs
│   └── errors.py        # Excepciones de dominio
│
└── infra/               # Adaptadores de infraestructura
    ├── __init__.py
    ├── ytdlp_adapter.py # Wrapper seguro para yt-dlp
    ├── file_system.py   # Operaciones de filesystem
    ├── config_store.py  # Persistencia de configuración (JSON)
    ├── history_store.py # Persistencia de historial (JSON)
    └── platform.py      # Utilidades específicas de OS

tests/
├── __init__.py
├── conftest.py          # Fixtures compartidos
├── unit/
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_models.py
│   └── test_download_service.py
└── integration/
    ├── __init__.py
    ├── test_ytdlp_adapter.py
    └── test_stores.py

assets/
├── icon.png             # Icono de la aplicación
└── icon.ico             # Icono para Windows
```

**Structure Decision**: Arquitectura hexagonal con 3 capas claras. La capa `ui/` solo maneja presentación y delega a `domain/`. La capa `domain/` contiene toda la lógica de negocio sin dependencias de I/O. La capa `infra/` implementa los adaptadores para yt-dlp, filesystem y persistencia.

## Complexity Tracking

> No hay violaciones de la constitución. El diseño es simple y cumple con todos los principios.

| Aspecto | Decisión | Justificación |
|---------|----------|---------------|
| Una descarga a la vez | Simplificación | Reduce complejidad de UI y threading, alinea con Principio I |
| JSON para persistencia | Simplicidad | Suficiente para 5 registros + config, evita dependencia de SQLite |
| yt-dlp bundled | UX | Usuario no técnico no debe instalar dependencias externas |
