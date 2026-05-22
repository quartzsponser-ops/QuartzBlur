# ⬡ QuartzBlur

**Cinematic motion blur for Minecraft videos — and any footage you throw at it.**

QuartzBlur is a desktop app that applies smooth, high-quality motion blur to your videos using frame blending powered by FFmpeg. Built with a clean dark UI, it's designed to make your Minecraft clips look silky smooth with just a few clicks.

---

## ✨ Features

- 🎬 Import any video (MP4, MKV, MOV, AVI, WebM)
- 🌀 Adjustable **Shutter Angle**, **Blur Strength**, and **Blend Frames**
- 📐 Output resolution selector: 480p → 4K or Source
- 🎞️ Custom FPS output (24 → 240 fps)
- 💾 Save & load settings as `.qbpreset` files
- 🚀 One-click export with progress bar
- 📦 Bundles FFmpeg — no separate install needed

---

## 📥 Download

Go to the **Actions** tab → latest successful run → download:
- `QuartzBlur-Installer` — recommended, installs to Program Files + desktop shortcut
- `QuartzBlur-standalone-exe` — single portable `.exe`, no install needed

---

## 🛠️ Build from Source

```bash
git clone https://github.com/YOUR_USERNAME/QuartzBlur
cd QuartzBlur
pip install -r requirements.txt
python main.py
```

You'll also need [FFmpeg](https://ffmpeg.org/download.html) in your PATH when running from source.

---

## 🎮 Tips for Minecraft

| Setting | Recommended |
|---|---|
| Shutter Angle | 180° (cinematic) — 360° (very heavy) |
| Blend Frames | 3–5 |
| Blur Strength | 5–8x |
| FPS | Match your recording FPS or go higher |

---

## 📄 License

MIT License — free to use, modify, and distribute.
