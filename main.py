import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import json
import os
import sys

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT   = "#7B5EA7"
ACCENT2  = "#A78BFA"
BG_DARK  = "#0D0D0F"
BG_MID   = "#141418"
BG_CARD  = "#1A1A22"
BORDER   = "#2A2A38"
TEXT     = "#E8E8F0"
SUBTEXT  = "#6B6B80"

# ── Helpers ────────────────────────────────────────────────────────────────────
def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

def ffmpeg_path():
    if getattr(sys, "frozen", False):
        return resource_path("ffmpeg.exe")
    return "ffmpeg"

def ffprobe_path():
    if getattr(sys, "frozen", False):
        return resource_path("ffprobe.exe")
    return "ffprobe"

def get_video_fps(path):
    try:
        cmd = [ffprobe_path(), "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=r_frame_rate",
               "-of", "default=noprint_wrappers=1:nokey=1", path]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        num, den = out.split("/")
        return round(float(num) / float(den), 3)
    except Exception:
        return 30.0

# ── Main App ───────────────────────────────────────────────────────────────────
class QuartzBlur(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuartzBlur")
        self.geometry("900x680")
        self.minsize(800, 600)
        self.configure(fg_color=BG_DARK)
        self.resizable(True, True)

        self.input_path  = tk.StringVar()
        self.output_path = tk.StringVar()
        self.blur_amount = tk.DoubleVar(value=5.0)
        self.fps_value   = tk.DoubleVar(value=60.0)
        self.resolution  = tk.StringVar(value="1080p")
        self.shutter_angle = tk.DoubleVar(value=180.0)
        self.blend_frames  = tk.IntVar(value=3)
        self.progress_var  = tk.DoubleVar(value=0.0)

        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=BG_MID, corner_radius=0, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⬡  QuartzBlur", font=("Segoe UI", 22, "bold"),
                     text_color=ACCENT2).pack(side="left", padx=24, pady=14)
        ctk.CTkLabel(hdr, text="Cinematic Motion Blur for Minecraft & Beyond",
                     font=("Segoe UI", 11), text_color=SUBTEXT).pack(side="left", pady=14)

        # Body scroll
        body = ctk.CTkScrollableFrame(self, fg_color=BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        pad = {"padx": 24, "pady": 8}

        # ── I/O ──
        self._section(body, "📂  File Input / Output")
        io = self._card(body)

        self._row_browse(io, "Input Video", self.input_path,  self._browse_input,  pad)
        self._row_browse(io, "Output File", self.output_path, self._browse_output, pad)

        # ── Video Settings ──
        self._section(body, "🎬  Video Settings")
        vs = self._card(body)

        self._labeled_slider(vs, "Output FPS", self.fps_value, 24, 240, 216,
                             lambda v: f"{v:.0f} fps")
        self._labeled_option(vs, "Resolution", self.resolution,
                             ["480p", "720p", "1080p", "1440p", "4K", "Source"])

        # ── Blur Settings ──
        self._section(body, "🌀  Motion Blur Settings")
        bs = self._card(body)

        self._labeled_slider(bs, "Shutter Angle", self.shutter_angle, 45, 360, 315,
                             lambda v: f"{v:.0f}°",
                             tip="180° = cinematic  •  360° = very heavy")
        self._labeled_slider(bs, "Blur Strength", self.blur_amount, 1, 15, 14,
                             lambda v: f"{v:.1f}x")
        self._labeled_slider(bs, "Blend Frames",  self.blend_frames, 1, 8, 7,
                             lambda v: f"{int(v)} frames",
                             tip="Higher = smoother but slower export")

        # ── Presets ──
        self._section(body, "💾  Settings Presets")
        pc = self._card(body)
        prow = ctk.CTkFrame(pc, fg_color="transparent")
        prow.pack(fill="x", padx=16, pady=10)
        for txt, cmd in [("💾 Save Preset", self._save_preset),
                         ("📂 Load Preset", self._load_preset),
                         ("🔄 Reset",        self._reset_settings)]:
            ctk.CTkButton(prow, text=txt, command=cmd, width=140,
                          fg_color=BG_MID, hover_color=BORDER,
                          border_color=BORDER, border_width=1,
                          text_color=TEXT, corner_radius=8).pack(side="left", padx=6)

        # ── Progress & Export ──
        self._section(body, "🚀  Export")
        ec = self._card(body)

        self.progress_bar = ctk.CTkProgressBar(ec, variable=self.progress_var,
                                               height=10, corner_radius=5,
                                               fg_color=BORDER, progress_color=ACCENT)
        self.progress_bar.pack(fill="x", padx=16, pady=(10, 4))

        self.status_label = ctk.CTkLabel(ec, text="Ready to render",
                                         font=("Segoe UI", 11), text_color=SUBTEXT)
        self.status_label.pack(anchor="w", padx=16, pady=(0, 10))

        ctk.CTkButton(ec, text="✨  Apply Motion Blur  →  Export",
                      command=self._start_export,
                      height=46, corner_radius=10,
                      font=("Segoe UI", 14, "bold"),
                      fg_color=ACCENT, hover_color="#6348A0",
                      text_color="white").pack(fill="x", padx=16, pady=(4, 16))

    # ── Widget helpers ──────────────────────────────────────────────────────────
    def _section(self, parent, title):
        ctk.CTkLabel(parent, text=title, font=("Segoe UI", 13, "bold"),
                     text_color=ACCENT2).pack(anchor="w", padx=24, pady=(18, 2))

    def _card(self, parent):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                         border_color=BORDER, border_width=1)
        f.pack(fill="x", padx=20, pady=4)
        return f

    def _row_browse(self, parent, label, var, cmd, pad):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", **pad)
        ctk.CTkLabel(row, text=label, width=110, anchor="w",
                     font=("Segoe UI", 12), text_color=TEXT).pack(side="left")
        ctk.CTkEntry(row, textvariable=var, fg_color=BG_MID,
                     border_color=BORDER, text_color=TEXT,
                     placeholder_text="Click Browse…").pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(row, text="Browse", width=80, command=cmd,
                      fg_color=ACCENT, hover_color="#6348A0",
                      corner_radius=6).pack(side="left")

    def _labeled_slider(self, parent, label, var, mn, mx, steps, fmt, tip=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(row, text=label, width=130, anchor="w",
                     font=("Segoe UI", 12), text_color=TEXT).pack(side="left")
        val_lbl = ctk.CTkLabel(row, text=fmt(var.get()), width=90, anchor="e",
                               font=("Segoe UI", 12, "bold"), text_color=ACCENT2)
        val_lbl.pack(side="right")

        def _upd(v):
            val_lbl.configure(text=fmt(float(v)))

        ctk.CTkSlider(row, variable=var, from_=mn, to=mx, number_of_steps=steps,
                      command=_upd, button_color=ACCENT, button_hover_color=ACCENT2,
                      progress_color=ACCENT, fg_color=BORDER).pack(side="left", fill="x", expand=True, padx=8)

        if tip:
            ctk.CTkLabel(parent, text=tip, font=("Segoe UI", 10),
                         text_color=SUBTEXT).pack(anchor="w", padx=16, pady=(0, 4))

    def _labeled_option(self, parent, label, var, values):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(row, text=label, width=130, anchor="w",
                     font=("Segoe UI", 12), text_color=TEXT).pack(side="left")
        ctk.CTkOptionMenu(row, variable=var, values=values,
                          fg_color=BG_MID, button_color=ACCENT,
                          button_hover_color="#6348A0",
                          dropdown_fg_color=BG_MID,
                          text_color=TEXT).pack(side="left", padx=8)

    # ── Browse ──────────────────────────────────────────────────────────────────
    def _browse_input(self):
        p = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi *.webm"), ("All", "*.*")])
        if p:
            self.input_path.set(p)
            base, ext = os.path.splitext(p)
            self.output_path.set(base + "_quartzblur" + ext)
            detected = get_video_fps(p)
            self.fps_value.set(detected)

    def _browse_output(self):
        p = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4"), ("MKV", "*.mkv"), ("MOV", "*.mov")])
        if p:
            self.output_path.set(p)

    # ── Presets ─────────────────────────────────────────────────────────────────
    def _get_settings(self):
        return {
            "fps": self.fps_value.get(),
            "resolution": self.resolution.get(),
            "shutter_angle": self.shutter_angle.get(),
            "blur_amount": self.blur_amount.get(),
            "blend_frames": self.blend_frames.get(),
        }

    def _apply_settings(self, d):
        self.fps_value.set(d.get("fps", 60))
        self.resolution.set(d.get("resolution", "1080p"))
        self.shutter_angle.set(d.get("shutter_angle", 180))
        self.blur_amount.set(d.get("blur_amount", 5))
        self.blend_frames.set(d.get("blend_frames", 3))

    def _save_preset(self):
        p = filedialog.asksaveasfilename(defaultextension=".qbpreset",
                                         filetypes=[("QuartzBlur Preset", "*.qbpreset")])
        if p:
            with open(p, "w") as f:
                json.dump(self._get_settings(), f, indent=2)
            messagebox.showinfo("QuartzBlur", "Preset saved!")

    def _load_preset(self):
        p = filedialog.askopenfilename(filetypes=[("QuartzBlur Preset", "*.qbpreset")])
        if p:
            with open(p) as f:
                self._apply_settings(json.load(f))
            messagebox.showinfo("QuartzBlur", "Preset loaded!")

    def _reset_settings(self):
        self._apply_settings({"fps": 60, "resolution": "1080p", "shutter_angle": 180,
                               "blur_amount": 5, "blend_frames": 3})

    # ── Export ──────────────────────────────────────────────────────────────────
    def _start_export(self):
        if not self.input_path.get():
            messagebox.showerror("QuartzBlur", "Please select an input video first.")
            return
        if not self.output_path.get():
            messagebox.showerror("QuartzBlur", "Please select an output path first.")
            return
        threading.Thread(target=self._run_export, daemon=True).start()

    def _run_export(self):
        self.progress_var.set(0.0)
        self._set_status("⏳ Building FFmpeg command…")

        inp   = self.input_path.get()
        out   = self.output_path.get()
        fps   = int(self.fps_value.get())
        res   = self.resolution.get()
        angle = self.shutter_angle.get()
        amt   = self.blur_amount.get()
        blen  = self.blend_frames.get()

        # Resolution scale filter
        scale_map = {"480p": "854:480", "720p": "1280:720",
                     "1080p": "1920:1080", "1440p": "2560:1440",
                     "4K": "3840:2160", "Source": "-1:-1"}
        scale = scale_map.get(res, "1920:1080")

        # Motion blur via minterpolate + tmix (smooth frame blending)
        # shutter_angle / 360 * (1/fps) = exposure time per frame
        blend_expr = ":".join(["1"] * blen)
        weights    = " ".join(["1"] * blen)

        vf_parts = []
        if scale != "-1:-1":
            vf_parts.append(f"scale={scale}:flags=lanczos")
        vf_parts.append(f"fps={fps}")
        # tmix blends N consecutive frames — core of the motion blur
        vf_parts.append(f"tmix=frames={blen}:weights='{weights}'")
        # unsharp to recover slight softness from blending
        vf_parts.append("unsharp=5:5:0.3:5:5:0.0")

        vf = ",".join(vf_parts)

        cmd = [
            ffmpeg_path(), "-y", "-i", inp,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "slow",
            "-crf", str(max(14, 28 - int(amt))),
            "-c:a", "copy",
            "-movflags", "+faststart",
            out
        ]

        self._set_status("🚀 Rendering… (this may take a while)")

        try:
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                                    stdout=subprocess.DEVNULL,
                                    universal_newlines=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                    if sys.platform == "win32" else 0)
            for line in proc.stderr:
                if "time=" in line:
                    # crude progress pulse
                    cur = self.progress_var.get()
                    self.progress_var.set(min(cur + 0.005, 0.95))

            proc.wait()
            if proc.returncode == 0:
                self.progress_var.set(1.0)
                self._set_status("✅ Export complete!")
                messagebox.showinfo("QuartzBlur", f"Done!\nSaved to:\n{out}")
            else:
                self._set_status("❌ FFmpeg error — check your input file.")
                messagebox.showerror("QuartzBlur",
                                     "FFmpeg failed. Make sure your video file is valid.")
        except FileNotFoundError:
            self._set_status("❌ FFmpeg not found.")
            messagebox.showerror("QuartzBlur",
                                 "FFmpeg was not found.\n\n"
                                 "If running from source, install FFmpeg and add it to PATH.\n"
                                 "The .exe installer bundles FFmpeg automatically.")

    def _set_status(self, msg):
        self.after(0, lambda: self.status_label.configure(text=msg))


if __name__ == "__main__":
    app = QuartzBlur()
    app.mainloop()
