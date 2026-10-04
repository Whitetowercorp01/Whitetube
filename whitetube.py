# -*- coding: utf-8 -*-
"""
WhiteTube - Descargador de Canciones de YouTube a MP3
"""
import sys
import argparse

# Configurar encoding en Windows para evitar errores con charmap
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(
        description="WhiteTube - Descargador de música de YouTube a MP3 de alta fidelidad."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Enlace de YouTube o nombre de la canción a descargar directamente."
    )
    parser.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Iniciar en modo consola (interactivo o directo)."
    )
    parser.add_argument(
        "--playlist", "-p",
        action="store_true",
        help="Indica que el enlace proporcionado es una playlist completa."
    )
    parser.add_argument(
        "--quality", "-q",
        choices=["128", "192", "256", "320"],
        default="320",
        help="Calidad de audio deseada en kbps (por defecto: 320)."
    )
    parser.add_argument(
        "--output", "-o",
        help="Carpeta destino donde guardar los archivos MP3."
    )

    args = parser.parse_args()

    # Si se pasó una canción/URL por línea de comandos, ejecutar directo
    if args.query:
        from cli import run_direct_cli
        run_direct_cli(
            query=args.query,
            quality=args.quality,
            output_dir=args.output,
            is_playlist=args.playlist
        )
        return

    # Si el usuario especificó la bandera --cli, abrir menú interactivo
    if args.cli:
        from cli import run_interactive_cli
        run_interactive_cli()
        return

    # Por defecto, iniciar la interfaz gráfica moderna
    try:
        from gui import launch_gui
        launch_gui()
    except Exception as e:
        print(f"[!] No se pudo iniciar la interfaz gráfica: {e}")
        print("[*] Iniciando en modo consola alternativo...\n")
        from cli import run_interactive_cli
        run_interactive_cli()

if __name__ == "__main__":
    main()