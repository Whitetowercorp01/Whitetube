# -*- coding: utf-8 -*-
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

# Configurar encoding en Windows
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from downloader import WhiteTubeDownloader, get_ffmpeg_path

def get_friendly_error(err_msg: str) -> str:
    """Traduce errores crudos de yt-dlp a mensajes claros y amigables."""
    lowered = err_msg.lower()
    if "video unavailable" in lowered:
        return "El video no está disponible o ha sido eliminado de YouTube."
    if "private video" in lowered:
        return "El video es privado en YouTube y no se puede descargar."
    if "sign in to confirm your age" in lowered:
        return "El video tiene restricción de edad en YouTube."
    if "not a valid url" in lowered:
        return "El enlace ingresado no es válido. Ingresa un enlace correcto o escribe el nombre de la canción."
    if "unable to download webpage" in lowered or "no internet" in lowered:
        return "Error de conexión. Comprueba tu conexión a Internet e inténtalo de nuevo."
    if "members-only" in lowered:
        return "Este contenido es exclusivo para miembros del canal de YouTube."
    
    # Extraer la última línea significativa
    lines = [line.strip() for line in err_msg.strip().split("\n") if line.strip()]
    if lines:
        last_line = lines[-1]
        if last_line.startswith("ERROR:"):
            last_line = last_line.replace("ERROR:", "").strip()
        return last_line
    return err_msg

class WhiteTubeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("WhiteTube - Descargador de Música a MP3")
        self.root.geometry("800x650")
        self.root.minsize(720, 600)
        self.root.configure(bg="#F4F6F9")

        # Configuración de ruta por defecto
        default_dir = os.path.join(os.path.expanduser("~"), "Music", "WhiteTube")
        os.makedirs(default_dir, exist_ok=True)
        self.download_dir_var = tk.StringVar(value=default_dir)
        self.quality_var = tk.StringVar(value="320")
        self.is_downloading = False

        self._configure_styles()
        self._build_ui()
        self._check_environment()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        bg_card = "#FFFFFF"
        text_primary = "#1E293B"
        accent_red = "#E11D48"

        style.configure("TFrame", background="#F4F6F9")
        style.configure("Card.TFrame", background=bg_card, relief="flat")
        style.configure("Title.TLabel", background="#F4F6F9", foreground=text_primary, font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background="#F4F6F9", foreground="#64748B", font=("Segoe UI", 10))
        style.configure("CardLabel.TLabel", background=bg_card, foreground=text_primary, font=("Segoe UI", 10, "bold"))
        style.configure("CardText.TLabel", background=bg_card, foreground="#475569", font=("Segoe UI", 9))
        style.configure("Status.TLabel", background=bg_card, foreground="#2563EB", font=("Segoe UI", 9, "bold"))
        
        style.configure(
            "Accent.TButton",
            background=accent_red,
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#BE123C"), ("disabled", "#CBD5E1")],
            foreground=[("disabled", "#94A3B8")]
        )
        
        style.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground=text_primary,
            font=("Segoe UI", 9),
            borderwidth=0,
            padding=6
        )
        style.map("Secondary.TButton", background=[("active", "#CBD5E1")])
        
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#E2E8F0",
            background=accent_red,
            thickness=12
        )

    def _build_ui(self):
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Encabezado
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_lbl = ttk.Label(header_frame, text="⚪ WhiteTube", style="Title.TLabel")
        title_lbl.pack(anchor="w")

        sub_frame = ttk.Frame(header_frame)
        sub_frame.pack(fill=tk.X, pady=(2, 0))

        sub_lbl = ttk.Label(
            sub_frame,
            text="Descarga canciones y playlists completas de YouTube en MP3 de alta fidelidad",
            style="Subtitle.TLabel"
        )
        sub_lbl.pack(side=tk.LEFT)

        self.ffmpeg_badge = ttk.Label(
            sub_frame,
            text="Verificando motor...",
            font=("Segoe UI", 9, "bold"),
            background="#F4F6F9",
            foreground="#64748B"
        )
        self.ffmpeg_badge.pack(side=tk.RIGHT)

        # Tarjeta 1: Entrada y Parámetros
        input_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        input_card.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            input_card,
            text="Enlace de YouTube o Nombre de la Canción:",
            style="CardLabel.TLabel"
        ).pack(anchor="w", pady=(0, 6))

        entry_row = ttk.Frame(input_card, style="Card.TFrame")
        entry_row.pack(fill=tk.X, pady=(0, 10))

        self.url_entry = tk.Entry(
            entry_row,
            font=("Segoe UI", 11),
            bg="#F8FAFC",
            fg="#0F172A",
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self.start_download(is_playlist=False))

        paste_btn = ttk.Button(
            entry_row,
            text="📋 Pegar",
            style="Secondary.TButton",
            command=self._paste_clipboard
        )
        paste_btn.pack(side=tk.RIGHT)

        # Fila de Configuración (Calidad + Destino)
        config_row = ttk.Frame(input_card, style="Card.TFrame")
        config_row.pack(fill=tk.X, pady=(0, 10))

        qual_frame = ttk.Frame(config_row, style="Card.TFrame")
        qual_frame.pack(side=tk.LEFT)
        ttk.Label(qual_frame, text="Calidad de audio:", style="CardText.TLabel").pack(side=tk.LEFT, padx=(0, 6))
        qual_combo = ttk.Combobox(
            qual_frame,
            textvariable=self.quality_var,
            values=["320", "192", "128"],
            width=6,
            state="readonly"
        )
        qual_combo.pack(side=tk.LEFT)
        ttk.Label(qual_frame, text="kbps (MP3)", style="CardText.TLabel").pack(side=tk.LEFT, padx=(4, 15))

        dir_frame = ttk.Frame(config_row, style="Card.TFrame")
        dir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(dir_frame, text="Destino:", style="CardText.TLabel").pack(side=tk.LEFT, padx=(0, 6))

        self.dir_label = ttk.Label(
            dir_frame,
            text=self.download_dir_var.get(),
            style="CardText.TLabel",
            font=("Segoe UI", 8)
        )
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(
            dir_frame,
            text="Cambiar...",
            style="Secondary.TButton",
            command=self._choose_directory
        )
        browse_btn.pack(side=tk.RIGHT, padx=(6, 0))

        open_folder_btn = ttk.Button(
            dir_frame,
            text="📂 Abrir",
            style="Secondary.TButton",
            command=self._open_downloads_folder
        )
        open_folder_btn.pack(side=tk.RIGHT)

        # Botones de Acción
        actions_row = ttk.Frame(input_card, style="Card.TFrame")
        actions_row.pack(fill=tk.X, pady=(5, 0))

        self.download_btn = ttk.Button(
            actions_row,
            text="⬇️  Descargar Canción a MP3",
            style="Accent.TButton",
            command=lambda: self.start_download(is_playlist=False)
        )
        self.download_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.playlist_btn = ttk.Button(
            actions_row,
            text="📑 Descargar Playlist Completa",
            style="Secondary.TButton",
            command=lambda: self.start_download(is_playlist=True)
        )
        self.playlist_btn.pack(side=tk.RIGHT)

        # Tarjeta 2: Progreso
        progress_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        progress_card.pack(fill=tk.X, pady=(0, 12))

        prog_header = ttk.Frame(progress_card, style="Card.TFrame")
        prog_header.pack(fill=tk.X, pady=(0, 6))

        self.status_label = ttk.Label(
            prog_header,
            text="Listo para descargar canciones o playlists.",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)

        self.percent_label = ttk.Label(
            prog_header,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            background="#FFFFFF",
            foreground="#1E293B"
        )
        self.percent_label.pack(side=tk.RIGHT)

        self.progress_bar = ttk.Progressbar(
            progress_card,
            orient="horizontal",
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))

        self.detail_label = ttk.Label(
            progress_card,
            text="",
            style="CardText.TLabel",
            font=("Segoe UI", 8)
        )
        self.detail_label.pack(anchor="w")

        # Tarjeta 3: Historial
        history_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        history_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            history_card,
            text="Descargas realizadas en esta sesión:",
            style="CardLabel.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        columns = ("title", "status", "quality")
        self.tree = ttk.Treeview(
            history_card,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=6
        )
        self.tree.heading("title", text="Título / Canción")
        self.tree.heading("status", text="Estado")
        self.tree.heading("quality", text="Calidad")

        self.tree.column("title", width=440, anchor="w")
        self.tree.column("status", width=130, anchor="center")
        self.tree.column("quality", width=90, anchor="center")

        tree_scroll = ttk.Scrollbar(history_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", lambda e: self._open_downloads_folder())

    def _check_environment(self):
        ffmpeg = get_ffmpeg_path()
        if ffmpeg:
            self.ffmpeg_badge.configure(text="● Motor FFmpeg Activo", foreground="#16A34A")
        else:
            self.ffmpeg_badge.configure(text="▲ FFmpeg no detectado", foreground="#DC2626")

    def _paste_clipboard(self):
        try:
            content = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, content.strip())
        except Exception:
            pass

    def _choose_directory(self):
        chosen = filedialog.askdirectory(initialdir=self.download_dir_var.get())
        if chosen:
            self.download_dir_var.set(chosen)
            display = chosen if len(chosen) < 45 else "..." + chosen[-42:]
            self.dir_label.configure(text=display)

    def _open_downloads_folder(self):
        folder = self.download_dir_var.get()
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showinfo("WhiteTube", f"La carpeta de descargas aún no existe:\n{folder}")

    def _set_ui_state(self, downloading: bool):
        self.is_downloading = downloading
        state = tk.DISABLED if downloading else tk.NORMAL
        self.download_btn.configure(state=state)
        self.playlist_btn.configure(state=state)
        self.url_entry.configure(state=state)

    def start_download(self, is_playlist: bool = False):
        if self.is_downloading:
            return

        query = self.url_entry.get().strip()
        if not query:
            messagebox.showwarning(
                "WhiteTube",
                "Por favor escribe el nombre de una canción o pega un enlace de YouTube."
            )
            return

        # Detección inteligente: si es un enlace de playlist explícito y se presionó "Canción"
        if not is_playlist and ("playlist?list=" in query.lower()):
            resp = messagebox.askyesno(
                "Detectada Playlist",
                "El enlace ingresado corresponde a una lista de reproducción completa.\n\n¿Deseas descargar toda la playlist?"
            )
            if resp:
                is_playlist = True

        self._set_ui_state(True)
        self.progress_bar["value"] = 0
        self.percent_label.configure(text="0%")
        self.status_label.configure(text="Iniciando descarga...", foreground="#2563EB")
        self.detail_label.configure(text="")

        threading.Thread(
            target=self._download_worker,
            args=(query, is_playlist),
            daemon=True
        ).start()

    def _download_worker(self, query: str, is_playlist: bool):
        try:
            downloader = WhiteTubeDownloader(
                output_dir=self.download_dir_var.get(),
                quality=self.quality_var.get()
            )

            def on_progress(d):
                self.root.after(0, self._handle_progress, d)

            def on_status(msg):
                self.root.after(0, self._handle_status, msg)

            if is_playlist:
                info = downloader.download_playlist(
                    query,
                    progress_callback=on_progress,
                    status_callback=on_status
                )
                title = info.get("title") or "Playlist de YouTube"
            else:
                info = downloader.download_song(
                    query,
                    progress_callback=on_progress,
                    status_callback=on_status
                )
                title = info.get("title", query)

            self.root.after(0, self._on_download_success, title)

        except Exception as e:
            self.root.after(0, self._on_download_error, str(e))

    def _handle_progress(self, d):
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total and total > 0:
                percent = int((downloaded / total) * 100)
                self.progress_bar["value"] = percent
                self.percent_label.configure(text=f"{percent}%")

            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            detail = f"Velocidad: {speed}" if speed else ""
            if eta:
                detail += f" | Tiempo restante: {eta}"
            self.detail_label.configure(text=detail)

        elif status == "finished":
            self.progress_bar["value"] = 100
            self.percent_label.configure(text="100%")

    def _handle_status(self, msg: str):
        self.status_label.configure(text=msg)

    def _on_download_success(self, title: str):
        self._set_ui_state(False)
        self.status_label.configure(text="¡Descarga y conversión completadas!", foreground="#16A34A")
        self.percent_label.configure(text="100%")
        self.progress_bar["value"] = 100
        self.detail_label.configure(text=f"Guardado en {self.download_dir_var.get()}")

        # Agregar al historial
        self.tree.insert("", 0, values=(title, "Completado", f"{self.quality_var.get()} kbps"))
        self.url_entry.delete(0, tk.END)

    def _on_download_error(self, err_msg: str):
        self._set_ui_state(False)
        friendly = get_friendly_error(err_msg)
        self.status_label.configure(text="Error en la descarga", foreground="#DC2626")
        self.detail_label.configure(text=friendly)
        messagebox.showerror(
            "Error en WhiteTube",
            f"No se pudo completar la descarga:\n\n{friendly}"
        )


def launch_gui():
    root = tk.Tk()
    app = WhiteTubeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()