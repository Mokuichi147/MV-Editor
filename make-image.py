import os
import sys
import math
from PIL import Image, ImageDraw

separator = '/'
if sys.platform == 'win32':
    separator = '\\'

dir_path = os.path.abspath(os.path.dirname(__file__))
resources_path = dir_path + separator + 'Resources'
if not os.path.isdir(resources_path):
    os.mkdir(resources_path)

size = 256
main_color = (145,140,255, 255)
sub_color  = ( 90, 90,255, 255)

half = size / 2
quarter = size / 4
triangle_width = size / 4 * math.sqrt(3)

img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.ellipse(((size/3.5,size/3.5) ,(size/3.5*2.5,size/3.5*2.5)), fill=main_color)
img.save(resources_path + separator + 'cursor.png')

img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.polygon((((size-triangle_width)/2,quarter), ((size-triangle_width)/2,quarter*3), ((triangle_width)+quarter,half)), fill=main_color)
img.save(resources_path + separator + 'playback_button.png')
draw.polygon((((size-triangle_width)/2,quarter), ((size-triangle_width)/2,quarter*3), ((triangle_width)+quarter,half)), fill=sub_color)
img.save(resources_path + separator + 'playback_button_down.png')

img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.rectangle(((quarter,quarter), (quarter*3,quarter*3)), fill=main_color)
img.save(resources_path + separator + 'playback_stop_button.png')
draw.rectangle(((quarter,quarter), (quarter*3,quarter*3)), fill=sub_color)
img.save(resources_path + separator + 'playback_stop_button_down.png')