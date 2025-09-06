#!/usr/bin/env python3

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Your GitHub Pages URL
url = "https://tuzahu.github.io/cad-viewer-demo/"

# Create QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data
qr.add_data(url)
qr.make(fit=True)

# Create image
img = qr.make_image(fill_color="black", back_color="white")

# Resize for better visibility
img = img.resize((400, 400), Image.Resampling.NEAREST)

# Add text below the QR code
# Create a new image with space for text
final_img = Image.new('RGB', (400, 450), color='white')
final_img.paste(img, (0, 0))

# Add text
draw = ImageDraw.Draw(final_img)
try:
    # Try to use a system font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except:
    try:
        # Fallback to default font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        # Use default font
        font = ImageFont.load_default()

# Add title
draw.text((10, 410), "CAD Viewer Demo", fill="black", font=font)
draw.text((10, 430), url, fill="blue", font=font)

# Save the QR code
output_file = "cad-viewer-qr-code.png"
final_img.save(output_file)

print(f"✅ QR code generated successfully!")
print(f"📱 File saved as: {output_file}")
print(f"🔗 URL: {url}")
print(f"📏 Size: 400x450 pixels")
print(f"💾 Location: {os.path.abspath(output_file)}")

# Also create a simple version without text
simple_img = qr.make_image(fill_color="black", back_color="white")
simple_img = simple_img.resize((300, 300), Image.Resampling.NEAREST)
simple_img.save("cad-viewer-qr-simple.png")
print(f"📱 Simple version saved as: cad-viewer-qr-simple.png")

