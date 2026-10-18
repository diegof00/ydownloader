# Revisión y validación — 18 de octubre de 2026

## Correcciones

- La ruta final corresponde al archivo convertido o unido por FFmpeg.
- Se descarga y procesa en una carpeta temporal exclusiva. Cancelación y errores
  limpian esa carpeta sin borrar archivos parciales ajenos.
- Los nombres de destino existentes se conservan usando un sufijo numérico.
- Video se remultiplexa a MP4 también cuando la fuente es un único WebM.
- La cancelación inmediata no se pierde al comenzar el hilo. El servicio reserva
  el adaptador hasta terminar el procesamiento y la escritura del historial.
- Cerrar la ventana durante una descarga espera la limpieza sin bloquear Tk.
- Se conserva la preferencia de formato entre sesiones.
- Configuración e historial ilegibles o con estructura inválida no impiden arrancar.
  El historial conserva entradas válidas, limita el tamaño y sincroniza el acceso
  entre el hilo de descarga y la interfaz.
- La comprobación de permisos no altera archivos del usuario.
- Los errores de FFmpeg ausente y de autenticación explican su causa.
- Se especifican los paquetes instalables y se actualiza la configuración de Ruff.
- Se retiran del índice los .pyc y se ignoran cachés, entornos y artefactos de build.

## Evidencia local

Entorno: Linux, Python 3.14.4, yt-dlp 2026.8.19 y FFmpeg instalado.

- **74 pruebas aprobadas**, sin omisiones, incluyendo la interfaz real de Tk.
- Cobertura global: **75%**; servicio de descarga: **97%**.
- Un clip sintético con video y audio se genera con FFmpeg y se sirve por HTTP
  local. yt-dlp lo descarga y FFmpeg produce MP3 o MP4. ffprobe comprueba el
  contenedor, las pistas y el códec MP3.
- Se prueban cancelación durante descarga y antes del postprocesamiento,
  reintento, errores HTTP, conservación de archivos y ausencia de temporales.
- El flujo gráfico prueba URL inválida, ambas descargas, historial, preferencias
  y cierre durante un trabajo activo.
- Ruff (lint y formato), compilación Python y `git diff --check` correctos.
- Wheel construido e instalado fuera del repositorio; importaciones y punto de
  entrada comprobados sin depender del directorio de trabajo.

Comando de la suite completa en Linux con pantalla disponible:

```bash
YDOWNLOADER_TEST_GUI=1 .venv/bin/pytest tests --cov=src --cov-report=term-missing
```

Para un entorno sin pantalla, usar `xvfb-run -a` antes del comando. Las pruebas
GUI son optativas; las pruebas de medios requieren ffmpeg y ffprobe.

## Validaciones externas y límites

Se intentó una descarga real de YouTube. El video de prueba `BaW_jenozKc` fue
reportado como no disponible. El segundo (`jNQXAC9IVRw`) exigió iniciar sesión
para confirmar que no se trataba de un bot. **No se confirmó una descarga de
YouTube exitosa**. No se leyeron cookies ni credenciales del navegador.
La aplicación todavía no incluye una opción de autenticación para esos casos.

La cancelación se observa en los hooks de descarga y entre postprocesadores.
Una conexión o un proceso FFmpeg ya iniciado puede tardar en devolver el control;
no se afirma que se interrumpa inmediatamente a mitad de una conversión.

La validación local fue en Linux. El workflow añadido ejecuta pruebas unitarias y
empaquetado con Python 3.13 y 3.14 en Linux, macOS y Windows, más integración y GUI
real bajo Xvfb en Linux. Los resultados de CI deben consultarse en el PR.
No se verificaron visualmente todas las ventanas ni todos los sitios soportados.

El PR se presenta como borrador hasta resolver la validación de YouTube y revisar
los resultados multiplataforma. LICENSE.md contiene solo el nombre de la licencia;
queda pendiente acordar su titular y completar el texto.
