# branding.py
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def watermark_bytes(file_bytes, text="Powered by Bot"):
    im = Image.open(BytesIO(file_bytes)).convert("RGBA")
    txt = Image.new("RGBA", im.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    margin = 10
    x = margin
    y = im.size[1] - 30
    draw.text((x,y), text, font=font, fill=(255,255,255,180))
    watermarked = Image.alpha_composite(im, txt)
    out = BytesIO()
    watermarked.convert("RGB").save(out, format="JPEG")
    out.seek(0)
    return out