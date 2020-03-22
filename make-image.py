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
triangle_width_space = (size-triangle_width) / 2


img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.ellipse([
    size/3.5, size/3.5,
    size/3.5*2.5, size/3.5*2.5
    ], fill=main_color)
img.save(resources_path + separator + 'cursor.png')


img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.polygon([
    triangle_width_space, quarter,
    triangle_width_space, quarter*3,
    triangle_width_space+triangle_width, half
    ], fill=main_color)
img.save(resources_path + separator + 'playback_button.png')
draw.polygon([
    triangle_width_space, quarter,
    triangle_width_space, quarter*3,
    triangle_width_space+triangle_width, half
    ], fill=sub_color)
img.save(resources_path + separator + 'playback_button_down.png')


img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.rectangle([
    quarter, quarter,
    quarter*3, quarter*3
    ], fill=main_color)
img.save(resources_path + separator + 'playback_stop_button.png')
draw.rectangle([
    quarter, quarter,
    quarter*3, quarter*3
    ], fill=sub_color)
img.save(resources_path + separator + 'playback_stop_button_down.png')


img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.polygon([
    triangle_width_space, half,
    triangle_width_space+triangle_width, quarter*3,
    triangle_width_space+triangle_width, quarter
    ], fill=main_color)
draw.line([
    triangle_width_space, quarter,
    triangle_width_space, quarter*3
    ], fill=main_color, width=size//10)
img.save(resources_path + separator + 'set_zero_frame_button.png')
draw.polygon([
    triangle_width_space, half,
    triangle_width_space+triangle_width, quarter*3,
    triangle_width_space+triangle_width, quarter
    ], fill=sub_color)
draw.line([
    triangle_width_space, quarter,
    triangle_width_space, quarter*3
    ], fill=sub_color, width=size//10)
img.save(resources_path + separator + 'set_zero_frame_button_down.png')


img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.polygon([
    triangle_width_space, half,
    triangle_width_space+triangle_width, quarter*3,
    triangle_width_space+triangle_width, quarter*3-size/10,
    size-triangle_width_space-size/20*3*math.sqrt(3), half,
    triangle_width_space+triangle_width, quarter+size/10,
    triangle_width_space+triangle_width, quarter
    ], fill=main_color)
img.save(resources_path + separator + 'previous_frame_button.png')
draw.polygon([
    triangle_width_space, half,
    triangle_width_space+triangle_width, quarter*3,
    triangle_width_space+triangle_width, quarter*3-size/10,
    size-triangle_width_space-size/20*3*math.sqrt(3), half,
    triangle_width_space+triangle_width, quarter+size/10,
    triangle_width_space+triangle_width, quarter
    ], fill=sub_color)
img.save(resources_path + separator + 'previous_frame_button_down.png')


img = Image.new('RGBA', (size,size), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.polygon([
    triangle_width_space, quarter,
    triangle_width_space, quarter+size/10,
    quarter+size/20*3*math.sqrt(3), half,
    triangle_width_space, quarter*3-size/10,
    triangle_width_space, quarter*3,
    triangle_width_space+triangle_width, half
    ], fill=main_color)
img.save(resources_path + separator + 'next_frame_button.png')
draw.polygon([
    triangle_width_space, quarter,
    triangle_width_space, quarter+size/10,
    quarter+size/20*3*math.sqrt(3), half,
    triangle_width_space, quarter*3-size/10,
    triangle_width_space, quarter*3,
    triangle_width_space+triangle_width, half
    ], fill=sub_color)
img.save(resources_path + separator + 'next_frame_button_down.png')


img = Image.new('RGBA', (size,size), (0,0,0,0))
img_color = Image.new('RGBA', (size,size), main_color)
img_mask = Image.new('L', img.size, 255)
draw = ImageDraw.Draw(img_mask)
draw.rectangle([
    quarter, quarter,
    quarter*3, quarter*3
    ], fill=0)
draw.rectangle([
    quarter+size/10, quarter+size/10,
    quarter*3-size/10, quarter*3-size/10
    ], fill=255)
draw.rectangle([
    0, half-size/20,
    size, half+size/20
    ], fill=255)
draw.rectangle([
    half-size/20, 0,
    half+size/20, size
    ], fill=255)
img = Image.composite(img, img_color, img_mask)
img.save(resources_path + separator + 'fullscreen_preview_button.png')
img_color = Image.new('RGBA', (size,size), sub_color)
img = Image.composite(img, img_color, img_mask)
img.save(resources_path + separator + 'fullscreen_preview_button_down.png')