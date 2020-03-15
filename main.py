import numpy as np
import cv2
import os

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.slider import Slider


version = '0.0.1'

dir_path = os.path.abspath(os.path.dirname(__file__))


def load_movie(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    max_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return cap, (width,height), max_count, fps

def pic_frame(cap, frame_count):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
    ret, frame = cap.read()
    if not ret:
        return
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 0)
    return frame

def frame2texture(frame, size):
    texture = Texture.create(size=size)
    texture.blit_buffer(frame.tostring())
    return texture

class FrameWidget(FloatLayout):
    image_texture = ObjectProperty(None)
    image_src = StringProperty('')
    frame_count = 0
    frame_max = 100
    tex_size = (0,0)

    def __init__(self, **kwargs):
        super(FrameWidget, self).__init__(**kwargs)
        self.cap, self.tex_size, self.frame_max, self.fps = load_movie(dir_path+'/movies/test.mp4')
        self.ids['slider'].max = self.frame_max - 1
        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.tex_size)
    
    def cursor_moved(self, value):
        self.frame = pic_frame(self.cap, int(value))
        self.image_texture = frame2texture(self.frame, self.tex_size)


class MVEditorApp(App):
    title = f'MV Editor v{version}'

    def build(self):
        return FrameWidget()
    
if __name__=='__main__':
    App = MVEditorApp()
    App.run()