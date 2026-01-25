from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# Image paths
IMAGE_DIR = "data/images"
IMAGES = {
    "welcome": f"{IMAGE_DIR}/welcome.png",
    "catalog": f"{IMAGE_DIR}/catalog.png",
    "cart": f"{IMAGE_DIR}/cart.png",
    "checkout": f"{IMAGE_DIR}/checkout.png",
    "profile": f"{IMAGE_DIR}/profile.png",
    "topup": f"{IMAGE_DIR}/topup.png",
    "admin": f"{IMAGE_DIR}/admin.png",
    "order_success": f"{IMAGE_DIR}/order_success.png",
}

def init_images():
    """Initialize image directory"""
    os.makedirs(IMAGE_DIR, exist_ok=True)

def generate_image(name: str, text: str = None, width: int = 800, height: int = 400) -> str:
    """Generate a white background image with text"""
    init_images()
    
    if text is None:
        text = name.replace("_", " ").title()
    
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    image_path = IMAGES.get(name, f"{IMAGE_DIR}/{name}.png")
    img.save(image_path)
    
    return image_path

def get_image(name: str) -> str:
    """Get image path, generate if doesn't exist"""
    init_images()
    image_path = IMAGES.get(name)
    
    if not image_path:
        return None
    
    if not os.path.exists(image_path):
        generate_image(name)
    
    return image_path if os.path.exists(image_path) else None

def image_exists(name: str) -> bool:
    """Check if image exists"""
    path = get_image(name)
    return path is not None
