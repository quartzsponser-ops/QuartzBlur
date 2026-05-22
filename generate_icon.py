"""
Run this once locally (needs Pillow) to generate assets/icon.ico
OR just skip it — the build will work without an icon.
"""
try:
    from PIL import Image, ImageDraw
    import os

    os.makedirs("assets", exist_ok=True)
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Simple hexagon-ish shape in purple
    d.ellipse([20, 20, 236, 236], fill=(123, 94, 167, 255))
    d.ellipse([60, 60, 196, 196], fill=(13, 13, 15, 255))
    d.ellipse([90, 90, 166, 166], fill=(167, 139, 250, 255))
    img.save("assets/icon.ico", format="ICO",
             sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("icon.ico generated in assets/")
except ImportError:
    print("Pillow not installed — skipping icon generation.")
