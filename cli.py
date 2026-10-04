# -*- coding: utf-8 -*-
import os
import sys
import argparse
from typing import Optional

# Configurar encoding en Windows para evitar errores con charmap
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from downloader import WhiteTubeDownloader, get_ffmpeg_path

def print_banner():
    banner = """
============================================================
              WhiteTube - Descargador a MP3
          YouTube a Audio de Alta Calidad (MP3)
============================================================
"""
    print(banner)

def run_interactive_cli():
    print_banner()

    ffmpeg = get_ffmpeg_path()
    if not ffmpeg:
        print("[!] Advertencia: No se detectó FFmpeg en el sistema ni en imageio-ffmpeg.")
        print("    Asegúrate de ejecutar: pip install imageio-ffmpeg\n")
    else:
        print("[OK] Motor FFmpeg activo y listo.\n")

    current_dir = os.path.join(os.path.expanduser("~"), "Music", "WhiteTube")
    current_quality = "320"

    while True:
        print(f"Carpeta actual : {current_dir}")
        print(f"Calidad actual : {current_quality} kbps")
        print("\nOpciones:")
        print("  1. Descargar canción (Enlace o Nombre)")
        print("  2. Descargar playlist de YouTube")
        print("  3. Cambiar carpeta de descargas")
        print("  4. Cambiar calidad de audio (128 / 192 / 320)")
        print("  5. Abrir carpeta en el Explorador de Windows")
        print("  0. Salir")

        try:
            choice = input("\nElige una opción (0-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo de WhiteTube...")
            break

        if choice == "0":
            print("\n¡Hasta luego! Gracias por usar WhiteTube.")
            break

        elif choice == "1":
            query = input("\nIntroduce el enlace o nombre de la canción: ").strip()
            if not query:
                print("[!] Entrada vacía. Operación cancelada.")
                continue

            print("\nIniciando descarga...")
            downloader = WhiteTubeDownloader(output_dir=current_dir, quality=current_quality)
            try:
                info = downloader.download_song(query, status_callback=lambda msg: print(f"[*] {msg}"))
                print(f"\n[OK] Descarga exitosa: {info.get('title')}.mp3\n")
            except Exception as e:
                print(f"\n[X] Error: {e}\n")

        elif choice == "2":
            url = input("\nIntroduce el enlace de la playlist de YouTube: ").strip()
            if not url:
                print("[!] Entrada vacía. Operación cancelada.")
                continue

            print("\nIniciando descarga de playlist...")
            downloader = WhiteTubeDownloader(output_dir=current_dir, quality=current_quality)
            try:
                info = downloader.download_playlist(url, status_callback=lambda msg: print(f"[*] {msg}"))
                print("\n[OK] Playlist descargada completamente.\n")
            except Exception as e:
                print(f"\n[X] Error: {e}\n")

        elif choice == "3":
            new_dir = input(f"\nIntroduce la nueva ruta (Actual: {current_dir}): ").strip()
            if new_dir:
                if not os.path.exists(new_dir):
                    try:
                        os.makedirs(new_dir, exist_ok=True)
                    except Exception as e:
                        print(f"[!] No se pudo crear la carpeta: {e}")
                        continue
                current_dir = new_dir
                print("[OK] Carpeta actualizada.\n")

        elif choice == "4":
            print("\nSelecciona calidad:")
            print("  1. 128 kbps (Ligero)")
            print("  2. 192 kbps (Estándar)")
            print("  3. 320 kbps (Alta calidad / HQ)")
            q_choice = input("Opción (1/2/3): ").strip()
            if q_choice == "1":
                current_quality = "128"
            elif q_choice == "2":
                current_quality = "192"
            elif q_choice == "3":
                current_quality = "320"
            else:
                print("[!] Opción inválida.")
            print(f"[OK] Calidad establecida a {current_quality} kbps.\n")

        elif choice == "5":
            if os.path.exists(current_dir):
                os.startfile(current_dir)
                print("[OK] Carpeta abierta en el Explorador.")
            else:
                print("[!] La carpeta aún no existe.")
        else:
            print("[!] Opción no reconocida.")

def run_direct_cli(query: str, quality: str = "320", output_dir: Optional[str] = None, is_playlist: bool = False):
    print_banner()
    downloader = WhiteTubeDownloader(output_dir=output_dir, quality=quality)
    print(f"Destino : {downloader.output_dir}")
    print(f"Calidad : {quality} kbps")
    print(f"Objetivo: {query}\n")

    try:
        if is_playlist:
            downloader.download_playlist(query, status_callback=lambda msg: print(f"[*] {msg}"))
        else:
            downloader.download_song(query, status_callback=lambda msg: print(f"[*] {msg}"))
        print("\n[OK] ¡Descarga y conversión completadas con éxito!")
    except Exception as e:
        print(f"\n[X] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_interactive_cli()