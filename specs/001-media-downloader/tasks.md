# Tasks: Media Downloader Desktop App

**Input**: Design documents from `/specs/001-media-downloader/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included for domain layer (validators, models, download_service) as specified in plan.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3, US4 (maps to user stories from spec.md)
- Paths use `src/` and `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md in src/, tests/, assets/
- [x] T002 Create requirements.txt with customtkinter>=5.2.0, yt-dlp>=2024.1.0, pytest>=7.4.0, ruff>=0.1.0
- [x] T003 [P] Create pyproject.toml with project metadata and ruff configuration
- [x] T004 [P] Create src/__init__.py with version info
- [x] T005 [P] Create src/__main__.py entry point for `python -m src`
- [x] T006 [P] Create tests/__init__.py and tests/conftest.py with shared fixtures

**Checkpoint**: Project structure ready, dependencies defined

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create domain exceptions in src/domain/errors.py (DomainError, InvalidURLError, UnsupportedSiteError, DownloadError, PermissionError, DiskSpaceError, CancelledException, ContentUnavailableError)
- [x] T008 [P] Create enums DownloadFormat and DownloadStatus in src/domain/models.py
- [x] T009 [P] Create Download dataclass in src/domain/models.py
- [x] T010 [P] Create HistoryEntry dataclass in src/domain/models.py
- [x] T011 [P] Create Settings dataclass in src/domain/models.py
- [x] T012 Create platform utilities in src/infra/platform.py (get_downloads_folder, get_app_data_folder for Windows/macOS/Linux)
- [x] T013 [P] Create src/ui/__init__.py and src/ui/widgets/__init__.py and src/ui/dialogs/__init__.py
- [x] T014 [P] Create src/domain/__init__.py with public exports
- [x] T015 [P] Create src/infra/__init__.py with public exports

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Descargar contenido desde URL (Priority: P1) 🎯 MVP

**Goal**: Usuario puede pegar URL, seleccionar carpeta y formato, ver progreso, y obtener archivo descargado

**Independent Test**: Abrir app, pegar URL de YouTube, seleccionar carpeta, elegir Video, click Descargar, verificar archivo en carpeta

### Tests for User Story 1

- [x] T016 [P] [US1] Create unit tests for URLValidator in tests/unit/test_validators.py
- [x] T017 [P] [US1] Create unit tests for Download model in tests/unit/test_models.py
- [x] T018 [P] [US1] Create unit tests for DownloadService in tests/unit/test_download_service.py

### Implementation for User Story 1

- [x] T019 [US1] Implement URLValidator in src/domain/validators.py (validate format, check yt-dlp extractors)
- [x] T020 [US1] Implement FileSystem adapter in src/infra/file_system.py (can_write, get_available_space, get_unique_filename, delete_file)
- [x] T021 [US1] Implement ConfigStore adapter in src/infra/config_store.py (load/save config.json, get/set last_output_folder)
- [x] T022 [US1] Implement YtdlpAdapter in src/infra/ytdlp_adapter.py (download with progress hooks, validate_url)
- [x] T023 [US1] Implement DownloadService in src/domain/download_service.py (start_download, validate, delegate to adapter, emit progress)
- [x] T024 [P] [US1] Create URLInput widget in src/ui/widgets/url_input.py (CTkEntry with paste support)
- [x] T025 [P] [US1] Create FolderPicker widget in src/ui/widgets/folder_picker.py (CTkButton + filedialog)
- [x] T026 [P] [US1] Create FormatSelector widget in src/ui/widgets/format_selector.py (CTkSegmentedButton Video/Audio)
- [x] T027 [P] [US1] Create ProgressBar widget in src/ui/widgets/progress_bar.py (CTkProgressBar + status label)
- [x] T028 [US1] Create DownloadButton widget in src/ui/widgets/download_button.py (CTkButton that toggles to Cancel)
- [x] T029 [US1] Create MainWindow in src/ui/main_window.py (compose widgets, wire to DownloadService, threading with queue)
- [x] T030 [US1] Create App bootstrap in src/app.py (initialize services, create MainWindow, run mainloop)
- [x] T031 [US1] Run tests and verify all pass: pytest tests/unit/ -v

**Checkpoint**: User Story 1 fully functional - can download video/audio with progress

---

## Phase 4: User Story 2 - Cancelar descarga en progreso (Priority: P2)

**Goal**: Usuario puede cancelar descarga activa, UI vuelve a estado inicial, archivos parciales se limpian

**Independent Test**: Iniciar descarga grande, click Cancelar, verificar que se detiene en <2s, sin archivos parciales

### Implementation for User Story 2

- [x] T032 [US2] Add cancel_download method to DownloadService in src/domain/download_service.py
- [x] T033 [US2] Implement cancel() with threading.Event in YtdlpAdapter in src/infra/ytdlp_adapter.py
- [x] T034 [US2] Add partial file cleanup on cancel in FileSystem in src/infra/file_system.py
- [x] T035 [US2] Update DownloadButton to show "Cancelar" during download in src/ui/widgets/download_button.py
- [x] T036 [US2] Wire cancel button to DownloadService.cancel_download in src/ui/main_window.py
- [x] T037 [US2] Update ProgressBar to show "Cancelado" status in src/ui/widgets/progress_bar.py

**Checkpoint**: User Story 2 complete - cancellation works with cleanup

---

## Phase 5: User Story 3 - Ver y manejar errores claramente (Priority: P2)

**Goal**: Errores muestran mensajes amigables sin jerga técnica, usuario sabe qué hacer

**Independent Test**: Probar con URL inválida, carpeta sin permisos, sin conexión; verificar mensajes claros

### Implementation for User Story 3

- [x] T038 [US3] Create ErrorDialog in src/ui/dialogs/error_dialog.py (CTkToplevel with user-friendly message)
- [x] T039 [US3] Add permission validation before download in DownloadService in src/domain/download_service.py
- [x] T040 [US3] Add disk space check before download in DownloadService in src/domain/download_service.py
- [x] T041 [US3] Map DomainError.user_message to ErrorDialog in src/ui/main_window.py
- [x] T042 [US3] Add retry option for network errors in ErrorDialog in src/ui/dialogs/error_dialog.py
- [x] T043 [US3] Add "select another folder" flow for permission errors in src/ui/main_window.py

**Checkpoint**: User Story 3 complete - all error scenarios show friendly messages

---

## Phase 6: User Story 4 - Ver historial de descargas recientes (Priority: P3)

**Goal**: Usuario ve últimas 5 descargas con título, ruta, estado; puede limpiar historial

**Independent Test**: Completar 6 descargas, verificar solo 5 en historial; click Limpiar, verificar vacío

### Implementation for User Story 4

- [x] T044 [US4] Implement HistoryStore adapter in src/infra/history_store.py (load, save, add with FIFO limit 5, clear)
- [x] T045 [US4] Add history management to DownloadService in src/domain/download_service.py (add entry on completion)
- [x] T046 [US4] Create HistoryPanel widget in src/ui/widgets/history_panel.py (CTkScrollableFrame with entries)
- [x] T047 [US4] Add "Limpiar historial" button to HistoryPanel in src/ui/widgets/history_panel.py
- [x] T048 [US4] Wire HistoryPanel to HistoryStore in src/ui/main_window.py
- [x] T049 [US4] Create AboutDialog with legal disclaimer in src/ui/dialogs/about_dialog.py
- [x] T050 [US4] Add disclaimer on first launch using ConfigStore.should_show_disclaimer in src/app.py

**Checkpoint**: User Story 4 complete - history visible and clearable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T051 Add close confirmation dialog when download in progress in src/ui/main_window.py
- [ ] T052 [P] Add application icon to assets/icon.png and assets/icon.ico
- [x] T053 [P] Create README.md with installation and usage instructions
- [ ] T054 Run full test suite: pytest tests/ -v --cov=src
- [x] T055 Run linting: ruff check src/ tests/ --fix
- [ ] T056 Validate quickstart.md: follow steps and verify app works end-to-end

**Checkpoint**: Application ready for release

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - MVP, must complete first
- **Phase 4 (US2)**: Depends on Phase 3 - extends download functionality
- **Phase 5 (US3)**: Depends on Phase 3 - extends error handling
- **Phase 6 (US4)**: Depends on Phase 3 - adds history feature
- **Phase 7 (Polish)**: Depends on all user stories

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (P1) | Phase 2 | None (MVP first) |
| US2 (P2) | US1 | US3 (after US1 complete) |
| US3 (P2) | US1 | US2 (after US1 complete) |
| US4 (P3) | US1 | US2, US3 (after US1 complete) |

### Within Each User Story

1. Tests first (T016-T018 for US1)
2. Domain/validators before services
3. Infra adapters before domain services
4. Domain services before UI
5. Individual widgets before MainWindow integration

---

## Parallel Execution Examples

### Phase 2: Foundation (parallel tasks)

```bash
# Can run simultaneously:
T008: Create enums in models.py
T009: Create Download dataclass
T010: Create HistoryEntry dataclass
T011: Create Settings dataclass
T013: Create UI __init__.py files
T014: Create domain __init__.py
T015: Create infra __init__.py
```

### Phase 3: User Story 1 (parallel widgets)

```bash
# Can run simultaneously after T023 (DownloadService):
T024: URLInput widget
T025: FolderPicker widget
T026: FormatSelector widget
T027: ProgressBar widget
```

### After US1 Complete (parallel stories)

```bash
# Can run simultaneously:
Phase 4 (US2): Cancel functionality
Phase 5 (US3): Error handling
Phase 6 (US4): History feature
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T015)
3. Complete Phase 3: User Story 1 (T016-T031)
4. **STOP and VALIDATE**: Run app, download a video successfully
5. Release MVP if acceptable

### Incremental Delivery

| Milestone | Stories | Deliverable |
|-----------|---------|-------------|
| MVP | US1 | Basic download functionality |
| v0.2 | US1 + US2 | Download with cancel |
| v0.3 | US1 + US2 + US3 | Robust error handling |
| v1.0 | All stories + Polish | Full featured app |

---

## Notes

- Total tasks: **56**
- Parallel opportunities: **23 tasks** marked with [P]
- Tests included: **3 test files** for domain layer
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (31 tasks)**
- All tasks have explicit file paths
- Each user story is independently testable after completion
