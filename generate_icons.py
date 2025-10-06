#!/usr/bin/env python3
"""
Script to generate all PWA icons and splash screens from a single source image
Requires: pip install pillow
Usage: python generate_icons.py source_image.png
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_icon(source_image, size, output_path, has_padding=False):
    """Create an icon of specified size"""
    img = Image.open(source_image)
    img = img.convert('RGBA')

    if has_padding:
        # Для maskable иконок добавляем padding
        padding = int(size * 0.1)
        icon_size = size - (padding * 2)
        img = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

        # Создаем новое изображение с padding
        new_img = Image.new('RGBA', (size, size), (254, 215, 40, 255))  # coffee-yellow
        new_img.paste(img, (padding, padding), img)
        img = new_img
    else:
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    img.save(output_path, 'PNG', optimize=True)
    print(f"✅ Created: {output_path}")

def create_splash_screen(size, output_path, app_name="Coffetime"):
    """Create iOS splash screen"""
    width, height = size

    # Создаем фон с градиентом (coffee-yellow to coffee-purple)
    img = Image.new('RGB', (width, height), (254, 215, 40))
    draw = ImageDraw.Draw(img)

    # Рисуем простой градиент
    for y in range(height):
        r = int(254 - (254 - 122) * y / height)
        g = int(215 - (215 - 90) * y / height)
        b = int(40 - (40 - 248) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Добавляем иконку в центр
    icon_size = min(width, height) // 4
    try:
        icon = Image.open('app/coffeeshop/static/images/icon-512.png')
        icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        icon_x = (width - icon_size) // 2
        icon_y = (height - icon_size) // 2
        img.paste(icon, (icon_x, icon_y), icon)
    except:
        # Если иконка не найдена, рисуем простой круг
        circle_radius = icon_size // 2
        circle_x = width // 2
        circle_y = height // 2
        draw.ellipse(
            [circle_x - circle_radius, circle_y - circle_radius,
             circle_x + circle_radius, circle_y + circle_radius],
            fill=(13, 18, 28)
        )

    # Добавляем название приложения
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), app_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    text_y = height - 150
    draw.text((text_x, text_y), app_name, fill=(255, 255, 255), font=font)

    img.save(output_path, 'PNG', optimize=True)
    print(f"✅ Created splash: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_icons.py source_image.png")
        sys.exit(1)

    source_image = sys.argv[1]

    if not os.path.exists(source_image):
        print(f"❌ Error: Source image '{source_image}' not found!")
        sys.exit(1)

    output_dir = "app/coffeeshop/static/images"
    os.makedirs(output_dir, exist_ok=True)

    print("🎨 Generating PWA icons and splash screens...")
    print("=" * 60)

    # Standard PWA icons
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    for size in icon_sizes:
        output_path = os.path.join(output_dir, f"icon-{size}.png")
        create_icon(source_image, size, output_path, has_padding=(size >= 192))

    # Apple Touch Icons
    apple_sizes = [57, 60, 72, 76, 114, 120, 144, 152, 180]
    for size in apple_sizes:
        output_path = os.path.join(output_dir, f"apple-touch-icon-{size}x{size}.png")
        create_icon(source_image, size, output_path)

    # Main Apple Touch Icon
    create_icon(source_image, 180, os.path.join(output_dir, "apple-touch-icon.png"))

    # Favicons
    create_icon(source_image, 32, os.path.join(output_dir, "favicon-32x32.png"))
    create_icon(source_image, 16, os.path.join(output_dir, "favicon-16x16.png"))

    # iOS Splash Screens
    splash_sizes = [
        (2048, 2732, "splash-2048x2732.png"),  # iPad Pro 12.9"
        (1668, 2388, "splash-1668x2388.png"),  # iPad Pro 11"
        (1536, 2048, "splash-1536x2048.png"),  # iPad
        (1242, 2688, "splash-1242x2688.png"),  # iPhone XS Max
        (1125, 2436, "splash-1125x2436.png"),  # iPhone X/XS/11 Pro
        (828, 1792, "splash-828x1792.png"),    # iPhone XR/11
        (750, 1334, "splash-750x1334.png"),    # iPhone 8/7/6
        (640, 1136, "splash-640x1136.png"),    # iPhone SE
    ]

    for width, height, filename in splash_sizes:
        output_path = os.path.join(output_dir, filename)
        create_splash_screen((width, height), output_path)

    # OG Image для социальных сетей
    create_splash_screen((1200, 630), os.path.join(output_dir, "og-image.png"))

    # Screenshot placeholders (можно заменить на реальные скриншоты)
    create_splash_screen((390, 844), os.path.join(output_dir, "screenshot-mobile.png"))
    create_splash_screen((1920, 1080), os.path.join(output_dir, "screenshot-desktop.png"))

    print("=" * 60)
    print("✅ All icons and splash screens generated successfully!")
    print(f"📁 Output directory: {output_dir}")

if __name__ == "__main__":
    main()
