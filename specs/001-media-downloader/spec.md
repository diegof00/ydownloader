# Feature Specification: Media Downloader Desktop App

**Feature Branch**: `001-media-downloader`  
**Created**: 2026-01-13  
**Status**: Draft  
**Input**: User description: "App de escritorio fácil para: pegar una URL, escoger carpeta, elegir 'video' o 'audio', ver progreso, poder cancelar, y ver errores claros. Usuarios objetivo: personas no técnicas."

## Clarifications

### Session 2026-01-13

- Q: ¿Qué debe hacer la app si yt-dlp no está disponible al iniciar? → A: Empaquetar yt-dlp junto con la app (bundle completo, sin dependencia externa del usuario).
- Q: ¿La aplicación debe permitir múltiples descargas simultáneas? → A: No, una sola descarga a la vez. Si el usuario inicia una nueva mientras hay otra en progreso, debe esperar o cancelar la actual.
- Q: ¿Cómo debe el usuario poder borrar el historial de descargas? → A: Botón "Limpiar historial" que borra todos los registros de una vez.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Descargar contenido desde URL (Priority: P1)

Como usuario no técnico, quiero pegar una URL de un video o audio, elegir dónde guardarlo y en qué formato (video o audio), y ver el progreso de la descarga hasta que termine.

**Why this priority**: Esta es la funcionalidad core de la aplicación. Sin ella, la app no tiene valor. Permite al usuario completar el flujo principal de descarga.

**Independent Test**: Puede probarse abriendo la app, pegando una URL válida de prueba, seleccionando una carpeta, eligiendo formato, y verificando que el archivo se descarga correctamente con feedback de progreso.

**Acceptance Scenarios**:

1. **Given** la app está abierta y el usuario tiene una URL copiada, **When** pega la URL en el campo de entrada, selecciona una carpeta de destino, elige formato "Video", y presiona "Descargar", **Then** la descarga inicia, se muestra progreso (porcentaje o barra), estados ("Conectando...", "Descargando", "Procesando", "Listo"), y el archivo aparece en la carpeta seleccionada.

2. **Given** la app está abierta, **When** el usuario elige formato "Audio" y completa la descarga, **Then** el archivo resultante es únicamente audio (sin video), en formato común (MP3 o similar).

3. **Given** una descarga está en progreso, **When** el usuario observa la interfaz, **Then** puede ver claramente el porcentaje de progreso, el estado actual, y el nombre/título del contenido.

---

### User Story 2 - Cancelar descarga en progreso (Priority: P2)

Como usuario, quiero poder cancelar una descarga que está en progreso si cambié de opinión o si está tardando demasiado.

**Why this priority**: Dar control al usuario es esencial para una buena experiencia. Evita frustración cuando el usuario necesita detener una operación.

**Independent Test**: Iniciar una descarga de un archivo grande, presionar "Cancelar", y verificar que la descarga se detiene, la UI vuelve a estado inicial, y no queda archivo parcial (o se limpia).

**Acceptance Scenarios**:

1. **Given** una descarga está en progreso, **When** el usuario presiona el botón "Cancelar", **Then** la descarga se detiene, el estado muestra "Cancelado", y el usuario puede iniciar una nueva descarga.

2. **Given** una descarga fue cancelada, **When** el usuario revisa la carpeta de destino, **Then** no hay archivos parciales o corruptos (se eliminan automáticamente).

---

### User Story 3 - Ver y manejar errores claramente (Priority: P2)

Como usuario no técnico, quiero que cuando algo falle, la app me muestre un mensaje claro explicando qué pasó y qué puedo hacer, sin crashear ni mostrar información técnica confusa.

**Why this priority**: El manejo de errores es crítico para usuarios no técnicos. Mensajes claros reducen frustración y tickets de soporte.

**Independent Test**: Probar con URL inválida, sin conexión a internet, carpeta sin permisos, y disco lleno; verificar que cada caso muestra mensaje apropiado.

**Acceptance Scenarios**:

1. **Given** el usuario ingresa una URL con formato inválido (ej: "esto no es una url"), **When** presiona "Descargar", **Then** la app muestra mensaje "La URL ingresada no es válida. Por favor verifica e intenta de nuevo" sin crashear.

2. **Given** el usuario selecciona una carpeta donde no tiene permisos de escritura, **When** intenta descargar, **Then** la app muestra mensaje "No tienes permiso para guardar archivos en esta carpeta. Por favor selecciona otra carpeta" y permite seleccionar una nueva carpeta.

3. **Given** hay un error de red durante la descarga, **When** la conexión falla, **Then** la app muestra "Error de conexión. Verifica tu conexión a internet e intenta de nuevo" con opción de reintentar.

4. **Given** no hay suficiente espacio en disco, **When** el usuario intenta descargar, **Then** la app muestra "No hay suficiente espacio en disco. Libera espacio o elige otra ubicación".

---

### User Story 4 - Ver historial de descargas recientes (Priority: P3)

Como usuario, quiero ver un historial simple de mis últimas 5 descargas para saber qué he descargado recientemente y encontrar los archivos fácilmente.

**Why this priority**: Es una funcionalidad de conveniencia que mejora la UX pero no es esencial para el flujo principal.

**Independent Test**: Completar 6 descargas, verificar que solo las últimas 5 aparecen en el historial con título, ruta y estado.

**Acceptance Scenarios**:

1. **Given** el usuario ha completado varias descargas, **When** observa la sección de historial, **Then** ve las últimas 5 descargas con: título del contenido, ruta donde se guardó, y estado (Completado/Cancelado/Error).

2. **Given** hay menos de 5 descargas en el historial, **When** el usuario abre la app, **Then** solo se muestran las descargas existentes sin espacios vacíos.

3. **Given** el historial tiene 5 elementos, **When** se completa una nueva descarga, **Then** la descarga más antigua se elimina y la nueva aparece al inicio de la lista.

4. **Given** el historial tiene elementos, **When** el usuario presiona "Limpiar historial", **Then** todos los registros se eliminan y el historial queda vacío.

---

### Edge Cases

- **URL válida pero contenido no disponible**: Mostrar "El contenido no está disponible o fue eliminado".
- **Pérdida de conexión durante descarga**: Pausar/reintentar automáticamente 3 veces antes de mostrar error.
- **Usuario cierra la app durante descarga**: Mostrar confirmación "Hay una descarga en progreso. ¿Deseas cancelarla y salir?".
- **URL de sitio no soportado**: Mostrar "Este sitio no está soportado actualmente" (asumiendo que hay una lista de sitios compatibles).
- **Archivo con nombre duplicado en destino**: Agregar sufijo numérico automáticamente (ej: "video (1).mp4").

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir al usuario pegar o escribir una URL en un campo de entrada visible.
- **FR-002**: El sistema DEBE validar el formato de la URL antes de intentar la descarga y mostrar error claro si es inválida.
- **FR-003**: El sistema DEBE permitir al usuario seleccionar la carpeta de destino mediante un diálogo de selección de carpetas del sistema operativo.
- **FR-004**: El sistema DEBE recordar la última carpeta seleccionada entre sesiones.
- **FR-005**: El sistema DEBE ofrecer opción de formato: "Video" (archivo con video y audio) o "Audio" (solo audio, formato MP3 o equivalente).
- **FR-006**: El sistema DEBE mostrar progreso de descarga mediante barra de progreso y/o porcentaje numérico.
- **FR-007**: El sistema DEBE mostrar estados de la operación: "Conectando...", "Descargando", "Procesando", "Listo", "Error", "Cancelado".
- **FR-008**: El sistema DEBE proporcionar un botón "Cancelar" visible durante la descarga que detiene la operación inmediatamente.
- **FR-009**: El sistema DEBE eliminar archivos parciales cuando se cancela una descarga.
- **FR-010**: El sistema DEBE verificar permisos de escritura en la carpeta destino antes de iniciar la descarga.
- **FR-011**: El sistema DEBE mostrar mensajes de error en lenguaje simple, sin jerga técnica.
- **FR-012**: El sistema DEBE mantener un historial de las últimas 5 descargas con: título, ruta del archivo, y estado final.
- **FR-013**: El sistema DEBE persistir el historial entre sesiones de la aplicación.
- **FR-014**: La interfaz DEBE permanecer responsiva (no congelarse) durante las descargas.
- **FR-015**: El sistema DEBE mostrar confirmación antes de cerrar la app si hay una descarga en progreso.
- **FR-016**: El sistema DEBE manejar nombres de archivo duplicados agregando sufijo numérico.
- **FR-017**: El sistema DEBE mostrar el título del contenido (cuando esté disponible) durante y después de la descarga.
- **FR-018**: El sistema DEBE permitir solo una descarga activa a la vez. El botón "Descargar" se deshabilita mientras hay una descarga en progreso.
- **FR-019**: El sistema DEBE proporcionar un botón "Limpiar historial" que elimina todos los registros del historial de descargas.

### Key Entities

- **Descarga (Download)**: Representa una operación de descarga. Atributos: URL origen, título del contenido, ruta destino, formato seleccionado (video/audio), estado (en progreso/completado/cancelado/error), progreso (0-100%), mensaje de error (si aplica), fecha/hora.

- **Historial (History)**: Colección ordenada de las últimas 5 descargas completadas, canceladas o fallidas. Se persiste entre sesiones.

- **Configuración (Settings)**: Preferencias del usuario. Atributos: última carpeta de destino seleccionada, formato preferido por defecto (opcional).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El usuario puede iniciar una descarga en máximo 3 clics/acciones después de abrir la aplicación (pegar URL, seleccionar carpeta si es primera vez, clic en descargar).

- **SC-002**: El 95% de los usuarios no técnicos pueden completar una descarga exitosamente en su primer intento sin asistencia.

- **SC-003**: Los mensajes de error son comprensibles para usuarios sin conocimientos técnicos (validar con pruebas de usuario).

- **SC-004**: La interfaz permanece responsiva (responde a clics en menos de 500ms) durante operaciones de descarga.

- **SC-005**: El tiempo desde clic en "Cancelar" hasta que la descarga se detiene es menor a 2 segundos.

- **SC-006**: El historial muestra correctamente las últimas 5 descargas después de reiniciar la aplicación.

- **SC-007**: La aplicación muestra progreso actualizado al menos cada 2 segundos durante descargas activas.

- **SC-008**: Todos los escenarios de error definidos muestran mensajes amigables sin exponer información técnica al usuario.

## Assumptions

- La aplicación incluirá yt-dlp empaquetado (bundle completo), sin requerir instalación separada por parte del usuario.
- El usuario tiene conexión a internet funcional (la app no está diseñada para trabajo offline).
- Los formatos de salida serán los más comunes y compatibles (MP4 para video, MP3 para audio).
- El historial se almacena localmente en el dispositivo del usuario.
- No se requiere autenticación del usuario ni cuentas.
- La aplicación no reproduce el contenido descargado, solo facilita la descarga.
