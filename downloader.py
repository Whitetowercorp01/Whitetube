# -*- coding: utf-8 -*-
import os
import sys
import shutil
import re
from typing import Callable, Optional, Dict, Any, List

# Configurar encoding seguro en Windows
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_ffmpeg_path() -> Optional[str]:
    """
    Localiza el ejecutable de FFmpeg:
    1. Revisa el PATH del sistema operativo.
    2. Revisa imageio_ffmpeg instalado en Python.
    3. Revisa una carpeta local 'bin' junto al proyecto.
    """
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg and os.path.exists(system_ffmpeg):
        return system_ffmpeg

    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            return ffmpeg_exe
    except Exception:
        pass

    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_bin = os.path.join(base_dir, "bin", "ffmpeg.exe")
    if os.path.exists(local_bin):
        return local_bin

    return None


def clean_leftover_thumbnails(target_dir: str):
    """
    Elimina archivos de imagen huérfanos (.webp, .jpg, .png)
    que yt-dlp pueda haber dejado tras incrustar la carátula en el MP3.
    """
    try:
        if not os.path.exists(target_dir):
            return
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.lower().endswith((".webp", ".jpg", ".png", ".jpeg")):
                    base_name, _ = os.path.splitext(file)
                    mp3_counterpart = os.path.join(root, base_name + ".mp3")
                    # Si existe el MP3 correspondiente, la carátula ya está incrustada
                    if os.path.exists(mp3_counterpart):
                        try:
                            os.remove(os.path.join(root, file))
                        except Exception:
                            pass
    except Exception:
        pass


def sanitize_filename_title(title: str) -> str:
    """
    Limpia caracteres problemáticos o emojis excesivos para nombres de carpeta en Windows.
    """
    cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
    return cleaned.strip() or "WhiteTube_Playlist"


class WhiteTubeDownloader:
    def __init__(self, output_dir: Optional[str] = None, quality: str = "320"):
        """
        :param output_dir: Carpeta de destino para los archivos MP3.
        :param quality: Calidad de audio en kbps ('128', '192', '256', '320').
        """
        if not output_dir:
            music_dir = os.path.join(os.path.expanduser("~"), "Music", "WhiteTube")
            self.output_dir = music_dir
        else:
            self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)
        self.quality = str(quality)
        self.ffmpeg_path = get_ffmpeg_path()

    def download_song(
        self,
        query_or_url: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Descarga una canción individual y la convierte a MP3 con metadatos y carátula.
        """
        import yt_dlp

        if not self.ffmpeg_path:
            raise RuntimeError(
                "FFmpeg no está disponible. Asegúrate de tener imageio-ffmpeg instalado."
            )

        target = query_or_url.strip()
        is_url = target.startswith(("http://", "https://"))

        # Si es un enlace de video individual que contiene &list=, aislar el video
        if is_url and ("watch?v=" in target or "youtu.be/" in target) and "&list=" in target:
            # Mantener solo el parámetro v= para no descargar la playlist entera por error
            target = re.sub(r'&list=[^&]+', '', target)

        if not is_url:
            target = f"ytsearch1:{target}"

        if status_callback:
            status_callback("Buscando información en YouTube...")

        def hook(d):
            if progress_callback:
                progress_callback(d)
            if status_callback:
                status = d.get('status', '')
                if status == 'downloading':
                    percent = d.get('_percent_str', '').strip()
                    speed = d.get('_speed_str', '').strip()
                    eta = d.get('_eta_str', '').strip()
                    msg = f"Descargando: {percent}"
                    if speed:
                        msg += f" a {speed}"
                    if eta:
                        msg += f" (Restante: {eta})"
                    status_callback(msg)
                elif status == 'finished':
                    status_callback("Descarga completada. Procesando MP3...")

        def post_hook(d):
            if status_callback:
                status = d.get('status', '')
                postprocessor = d.get('postprocessor', '')
                if status == 'started':
                    if 'ExtractAudio' in postprocessor:
                        status_callback(f"Extrayendo audio a MP3 ({self.quality} kbps)...")
                    elif 'EmbedThumbnail' in postprocessor or 'ThumbnailsConvertor' in postprocessor:
                        status_callback("Incrustando carátula del álbum...")
                    elif 'Metadata' in postprocessor:
                        status_callback("Incrustando metadatos (artista, título)...")
                elif status == 'finished' and 'ExtractAudio' in postprocessor:
                    status_callback("Conversión de audio completada.")

        out_template = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        postprocessors = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            },
            {
                'key': 'EmbedThumbnail',
            }
        ]

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'ffmpeg_location': self.ffmpeg_path,
            'writethumbnail': True,
            'postprocessors': postprocessors,
            'progress_hooks': [hook],
            'postprocessor_hooks': [post_hook],
            'windowsfilenames': True,
            'restrictfilenames': False,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 10,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target, download=True)
                if 'entries' in info and info['entries']:
                    info = info['entries'][0]

                # Limpieza de imágenes sueltas
                clean_leftover_thumbnails(self.output_dir)

                if status_callback:
                    status_callback("¡Listo! MP3 guardado exitosamente.")

                return info
        except Exception as e:
            # Limpiar si quedó algo temporal
            clean_leftover_thumbnails(self.output_dir)
            raise e

    def download_playlist(
        self,
        query_or_url: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Descarga una playlist completa de YouTube en formato MP3 en una subcarpeta.
        Omite automáticamente videos no disponibles o eliminados sin detenerse.
        """
        import yt_dlp

        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg no está disponible.")

        target = query_or_url.strip()
        is_url = target.startswith(("http://", "https://"))

        # Si el usuario escribió un nombre de lista en vez de una URL, buscar la playlist
        if not is_url:
            target = f"ytsearch1:playlist {target}"

        if status_callback:
            status_callback("Analizando lista de reproducción en YouTube...")

        def hook(d):
            if progress_callback:
                progress_callback(d)
            if status_callback and d.get('status') == 'downloading':
                percent = d.get('_percent_str', '').strip()
                status_callback(f"Descargando canción: {percent}")

        out_template = os.path.join(self.output_dir, "%(playlist_title,playlist)s", "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'ffmpeg_location': self.ffmpeg_path,
            'writethumbnail': True,
            'ignoreerrors': True,  # Clave: continuar si hay videos borrados/privados
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                },
                {
                    'key': 'EmbedThumbnail',
                }
            ],
            'progress_hooks': [hook],
            'windowsfilenames': True,
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 10,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target, download=True)
            if 'entries' in info and info['entries']:
                first_entry = info['entries'][0]
                playlist_title = info.get('title') or (first_entry.get('playlist_title') if first_entry else 'Playlist')
            else:
                playlist_title = info.get('title', 'Playlist')

            # Limpieza de imágenes sueltas
            clean_leftover_thumbnails(self.output_dir)

            if status_callback:
                status_callback("¡Playlist completa descargada con éxito!")

            return info