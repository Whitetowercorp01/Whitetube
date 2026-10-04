#  WhiteTube

**WhiteTube** es una aplicación en Python creada para descargar canciones y playlists completas de YouTube directamente a tu computadora en formato **MP3 de alta fidelidad (hasta 320 kbps)**, incluyendo metadatos (artista, título) y carátula del video integrada automáticamente.

---

##  Inicio Rápido en Windows

Tienes dos opciones muy sencillas para abrir WhiteTube:

### Opción 1: Con Doble Clic (Recomendada)
- Haz doble clic en el archivo **`iniciar_whitetube.bat`**.
- El script verificará automáticamente las librerías necesarias y abrirá la **interfaz gráfica**.

*(Si prefieres usar la consola, haz doble clic en `iniciar_whitetube_consola.bat`).*

---

### Opción 2: Desde la Terminal (PowerShell / CMD)
Abre la carpeta del proyecto en una consola y ejecuta:

```powershell
# Interfaz Gráfica (Por defecto)
py whitetube.py

# Modo Consola Interactivo
py whitetube.py --cli

# Descarga directa rápida desde terminal
py whitetube.py "Queen Bohemian Rhapsody"
py whitetube.py "https://www.youtube.com/watch?v=fJ9rUzIMcZQ" --quality 320
```

---

##  Características Principales

1. **Búsqueda Directa o Enlaces**:
   - Puedes pegar cualquier enlace de YouTube estándar (`youtube.com`), enlace corto (`youtu.be`), YouTube Music (`music.youtube.com`) o YouTube Shorts.
   - También puedes **escribir directamente el nombre de la canción** (ej: *"Coldplay Viva la Vida"*) y WhiteTube la encontrará y descargará automáticamente.
2. **Conversión a MP3 sin complicaciones**:
   - Utiliza `yt-dlp` junto con el motor `imageio-ffmpeg` integrado, por lo que **no requieres instalar ni configurar manualmente FFmpeg en el sistema**.
3. **Calidad de Audio Configurable**:
   - **320 kbps** (Máxima calidad de audio / HQ).
   - **192 kbps** (Calidad estándar).
   - **128 kbps** (Tamaño ligero).
4. **Metadatos y Carátulas**:
   - Cada archivo MP3 guardado incluye el nombre del artista, el título y la miniatura del video incrustada como portada de álbum.
5. **Carpeta de Descargas**:
   - Por defecto guarda tus canciones en tu carpeta personal de Windows: `Música\WhiteTube`.
   - Puedes cambiar la carpeta de destino con un solo clic o abrirla en el Explorador de archivos con el botón **📂 Abrir**.
6. **Descarga de Playlists**:
   - Soporte para descargar listas de reproducción completas organizadas en su propia subcarpeta.

---

##  Estructura del Proyecto

- `whitetube.py`: Punto de entrada principal del programa.
- `gui.py`: Interfaz gráfica con diseño limpio ("WhiteTube") creada con Tkinter/ttk.
- `cli.py`: Interfaz de línea de comandos interactiva y directa.
- `downloader.py`: Motor de descarga, extracción de audio y resolución de FFmpeg.
- `iniciar_whitetube.bat`: Lanzador de 1 solo clic para Windows (GUI).
- `iniciar_whitetube_consola.bat`: Lanzador de 1 solo clic para Windows (Consola).
- `requirements.txt`: Dependencias del proyecto (`yt-dlp`, `imageio-ffmpeg`, `mutagen`, `pillow`).

---

##  Instalación Manual de Dependencias

Si necesitas reinstalar dependencias en cualquier momento:

```powershell
py -m pip install -r requirements.txt
```
