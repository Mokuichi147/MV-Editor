import os
import sys
from PIL import Image, ImageDraw

separator = '/'
if sys.platform == 'win32':
    separator = '\\'

dir_path = os.path.abspath(os.path.dirname(__file__))
resources_path = dir_path + separator + 'Resources'
if not os.path.isdir(resources_path):
    os.mkdir(resources_path)

size = 512

img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.ellipse([150,150,size-150,size-150], fill=(145,140,255, 255))

img.save(resources_path + separator + 'cursor.png')