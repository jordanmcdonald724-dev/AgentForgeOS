# AgentForge Icon Pack Generation

The following Python snippet generates a full icon pack from a 512×512 base image, including resized PNGs, an ICO, transparent and glow variants, and a splash screen. It also notes use of ReportLab for packaging images if needed downstream.

```python
# Generate full icon pack, transparent version, glow version, and a splash screen using reportlab for packaging images
from PIL import Image, ImageFilter, ImageEnhance
import os

# Replace this with the path to your 512×512 base icon image
base_path = "<your_icon_path>/agentforge_icon_512.png"
img = Image.open(base_path).convert("RGBA")

# Create output directory
out_dir = "/mnt/data/agentforge_icon_pack"
os.makedirs(out_dir, exist_ok=True)

# Sizes
sizes = [16, 32, 64, 128, 256, 512]

# Save resized icons
paths = {}
for s in sizes:
    resized = img.resize((s, s), Image.LANCZOS)
    p = f"{out_dir}/icon_{s}.png"
    resized.save(p)
    paths[f"icon_{s}"] = p

# Create ICO
ico_path = f"{out_dir}/icon.ico"
img.save(ico_path, sizes=[(s, s) for s in sizes])
paths["ico"] = ico_path

# Transparent version (remove black background via threshold)
import numpy as np
arr = np.array(img)
brightness = arr[..., :3].mean(axis=2)
mask = brightness < 10  # treat near-black as transparent
arr[..., 3] = np.where(mask, 0, 255)
transparent = Image.fromarray(arr)
trans_path = f"{out_dir}/icon_transparent.png"
transparent.save(trans_path)
paths["transparent"] = trans_path

# Glow version
glow = img.copy()
blur = glow.filter(ImageFilter.GaussianBlur(radius=15))
enhancer = ImageEnhance.Brightness(blur)
glow_effect = enhancer.enhance(1.8)

combined = Image.alpha_composite(glow_effect, img)
glow_path = f"{out_dir}/icon_glow.png"
combined.save(glow_path)
paths["glow"] = glow_path

# Splash screen (1920x1080)
splash = Image.new("RGBA", (1920,1080), (0,0,0,255))
logo = img.resize((400,400), Image.LANCZOS)
lx, ly = splash.size[0]//2 - 200, splash.size[1]//2 - 200
splash.paste(logo, (lx, ly), logo)
splash_path = f"{out_dir}/splash.png"
splash.save(splash_path)
paths["splash"] = splash_path

paths
```
