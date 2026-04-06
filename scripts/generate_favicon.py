#!/usr/bin/env python3
"""
鸣镝项目图标生成脚本
生成简约的"镝"字图标
"""
import os
from PIL import Image, ImageDraw

def create_favicon(output_path: str = "frontend/public/favicon.png"):
    """生成鸣镝项目 favicon"""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2
    radius = int(size * 0.45)

    # 蓝色圆形背景 (#3592C4 - 鸣镝蓝)
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=(53, 146, 196, 255)
    )

    # 白色三角形箭头（象征"鸣镝"的箭头）
    arrow_color = (255, 255, 255, 255)
    arrow_size = int(size * 0.25)

    # 主箭头三角形
    points = [
        (center, center - arrow_size),  # 顶部
        (center - int(arrow_size * 0.866), center + int(arrow_size * 0.5)),
        (center + int(arrow_size * 0.866), center + int(arrow_size * 0.5)),
    ]
    draw.polygon(points, fill=arrow_color)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, format='PNG')
    print(f"Favicon 已生成: {output_path}")

if __name__ == "__main__":
    create_favicon()
