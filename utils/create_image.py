import os
import sys
import math
from PIL import Image, ImageDraw

separator = '/'
if sys.platform == 'win32':
    separator = '\\'

dir_path = os.path.abspath(os.path.dirname(__file__))
dir_path = dir_path.split(separator)[:-1]
dir_path = separator.join(dir_path)
resources_path = dir_path + separator + 'resources'
if not os.path.isdir(resources_path):
    os.mkdir(resources_path)
resources_path += separator

size = 256
main_color   = (145,140,255, 255)
sub_color    = ( 90, 90,255, 255)
accent_color = ( 50,180,200, 255)
background_accent_color     = ( 76, 76,102, 255)
background_accent_sub_color = ( 51, 51, 63, 255)
background_main_color = ( 28, 28, 28, 255)
background_sub_color  = ( 38, 38, 38, 255)


def cursor(size2d=(size,size), color=main_color, path=resources_path, name='cursor.png'):
    size = size2d[0]
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([
        size/3.5, size/3.5,
        size/3.5*2.5, size/3.5*2.5
        ], fill = color)
    img.save(path + name)

def playback(size2d=(size,size), color=main_color, path=resources_path, name='playback_button.png'):
    size = size2d[0]
    half = size / 2
    quarter = size / 4
    triangle_width = quarter * math.sqrt(3)
    triangle_width_space = (size-triangle_width) / 2
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        triangle_width_space, quarter,
        triangle_width_space, quarter*3,
        triangle_width_space+triangle_width, half
        ], fill = color)
    img.save(path + name)

def playback_stop(size2d=(size,size), color=main_color, path=resources_path, name='playback_stop_button.png'):
    size = size2d[0]
    quarter = size / 4
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([
        quarter, quarter,
        quarter*3, quarter*3
        ], fill = color)
    img.save(path + name)

def set_zero_frame(size2d=(size,size), color=main_color, path=resources_path, name='set_zero_frame_button.png'):
    size = size2d[0]
    half = size / 2
    quarter = size / 4
    triangle_width = quarter * math.sqrt(3)
    triangle_width_space = (size-triangle_width) / 2
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        triangle_width_space, half,
        triangle_width_space+triangle_width, quarter*3,
        triangle_width_space+triangle_width, quarter
        ], fill = color)
    draw.line([
        triangle_width_space, quarter,
        triangle_width_space, quarter*3
        ], fill = color, width = size//10)
    img.save(path + name)

def previous_frame(size2d=(size,size), color=main_color, path=resources_path, name='previous_frame_button.png'):
    size = size2d[0]
    half = size / 2
    quarter = size / 4
    triangle_width = quarter * math.sqrt(3)
    triangle_width_space = (size-triangle_width) / 2
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        triangle_width_space, half,
        triangle_width_space+triangle_width, quarter*3,
        triangle_width_space+triangle_width, quarter*3-size/10,
        size-triangle_width_space-size/20*3*math.sqrt(3), half,
        triangle_width_space+triangle_width, quarter+size/10,
        triangle_width_space+triangle_width, quarter
        ], fill = color)
    img.save(path + name)

def next_frame(size2d=(size,size), color=main_color, path=resources_path, name='next_frame_button.png'):
    size = size2d[0]
    half = size / 2
    quarter = size / 4
    triangle_width = quarter * math.sqrt(3)
    triangle_width_space = (size-triangle_width) / 2
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        triangle_width_space, quarter,
        triangle_width_space, quarter+size/10,
        triangle_width_space+size/20*3*math.sqrt(3), half,
        triangle_width_space, quarter*3-size/10,
        triangle_width_space, quarter*3,
        triangle_width_space+triangle_width, half
        ], fill = color)
    img.save(path + name)

def fullscreen_preview(size2d=(size,size), color=main_color, path=resources_path, name='fullscreen_preview_button.png'):
    size = size2d[0]
    half = size / 2
    quarter = size / 4
    img = Image.new('RGBA', size2d, (0,0,0,0))
    img_color = Image.new('RGBA', size2d, color)
    img_mask = Image.new('L', size2d, 255)
    draw = ImageDraw.Draw(img_mask)
    draw.rectangle([
        quarter, quarter,
        quarter*3, quarter*3
        ], fill = 0)
    draw.rectangle([
        quarter+size/10, quarter+size/10,
        quarter*3-size/10, quarter*3-size/10
        ], fill = 255)
    draw.rectangle([
        0, half-size/20,
        size, half+size/20
        ], fill = 255)
    draw.rectangle([
        half-size/20, 0,
        half+size/20, size
        ], fill = 255)
    img = Image.composite(img, img_color, img_mask)
    img.save(path + name)

def splitter(size2d=(size,size), color=background_main_color, path=resources_path, name='splitter.png'):
    img = Image.new('RGBA', size2d, color)
    img.save(path + name)

def listdir(size2d=(size,size), color=main_color, bg_color=background_main_color, line_width=5, path=resources_path, name='listdir.png'):
    size = size2d[0]
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.line([
        0, 0,
        0, size
        ], fill = color, width = line_width)
    draw.line([
        0, size,
        size, size
        ], fill = bg_color, width = 3)
    img.save(path + name)

def mode(size2d=(size,size), color=main_color, bg_color=background_sub_color, line_width=50, path=resources_path, name='mode.png'):
    size = size2d[0]
    img = Image.new('RGBA', size2d, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.line([
        0, 0,
        size, 0
        ], fill = color, width = line_width)
    draw.line([
        size, 0,
        size, size
        ], fill = bg_color, width = 5)
    img.save(path + name)

def project_button(size2d=(size,size), color=main_color, bg_color=background_main_color, path=resources_path, name='project_select.png'):
    size = size2d[0]
    img = Image.new('RGBA', size2d, color)
    draw = ImageDraw.Draw(img)
    draw.line([
        0, size,
        size, size
        ], fill = bg_color, width = 3)
    img.save(path + name)

def project_button_clear(size2d=(size,size), color=(0,0,0,0), path=resources_path, name='project_select_clear.png'):
    img = Image.new('RGBA', size2d, color)
    img.save(path + name)


def create_all():
    cursor()

    playback()
    playback(color=sub_color, name='playback_button_down.png')

    playback_stop()
    playback_stop(color=sub_color, name='playback_stop_button_down.png')

    set_zero_frame()
    set_zero_frame(color=sub_color, name='set_zero_frame_button_down.png')

    previous_frame()
    previous_frame(color=sub_color, name='previous_frame_button_down.png')

    next_frame()
    next_frame(color=sub_color, name='next_frame_button_down.png')

    fullscreen_preview()
    fullscreen_preview(color=sub_color, name='fullscreen_preview_button_down.png')

    splitter()
    splitter(color=sub_color, name='splitter_down.png')

    listdir()
    listdir(color=sub_color, line_width=11, name='listdir_down.png')

    mode()
    mode(color=main_color, line_width=size*2, name='mode_down.png')

    project_button()
    project_button_clear()
    project_button(color=accent_color, name='project_create.png')
    project_button_clear(name='project_create_clear.png')

    project_button_clear(name='alpha.png')


if __name__=='__main__':
    create_all()