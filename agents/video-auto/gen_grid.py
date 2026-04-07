from PIL import Image
import os

slides_dir = "/workspace/agents/video-auto/slides"
output_dir = "/workspace/agents/video-auto/video"
os.makedirs(output_dir, exist_ok=True)

images = sorted([f for f in os.listdir(slides_dir) if f.endswith('.png')])
print(f"Found {len(images)} slides: {images}")

w, h = 1920, 1080
cols = 3
rows = (len(images) + cols - 1) // cols

canvas = Image.new('RGB', (w * cols, h * rows), (10, 10, 26))

for i, img_name in enumerate(images):
    img_path = f"{slides_dir}/{img_name}"
    try:
        img = Image.open(img_path).convert('RGB')
        img_ratio = img.width / img.height
        cell_ratio = w / h
        if img_ratio > cell_ratio:
            new_w, new_h = w, int(w / img_ratio)
        else:
            new_w, new_h = int(h * img_ratio), h
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x = (w - new_w) // 2
        y = (h - new_h) // 2
        row, col = i // cols, i % cols
        canvas.paste(img, (col * w + x, row * h + y))
        print(f"  Added {i+1}: {img_name}")
    except Exception as e:
        print(f"  Error {img_name}: {e}")

grid_path = f"{slides_dir}/slides_grid.png"
canvas.save(grid_path, "PNG")
print(f"Grid saved: {grid_path} ({canvas.width}x{canvas.height})")

video_grid_path = f"{output_dir}/slides_grid.png"
canvas.save(video_grid_path, "PNG")
print(f"Copied to: {video_grid_path}")
