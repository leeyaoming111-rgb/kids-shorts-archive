import sys, glob
from PIL import Image, ImageDraw
fs = sorted(glob.glob('out/still_*.png')); cols = 4; rows = (len(fs) + cols - 1) // cols
sheet = Image.new('RGB', (360 * cols, 640 * rows), 'white')
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((360, 640)); x, y = (i % cols) * 360, (i // cols) * 640
    sheet.paste(im, (x, y)); ImageDraw.Draw(sheet).text((x + 8, y + 8), f[10:15], fill='black')
sheet.save(sys.argv[1] if len(sys.argv) > 1 else 'out/contact.jpg', quality=86)
