import cv2
import os
from time import sleep, time

from pydub import AudioSegment
from pydub.utils import ratio_to_db
from simpleaudio import play_buffer

from kivy.config import Config
Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)
Config.set('graphics', 'minimum_width', 640)
Config.set('graphics', 'minimum_height', 480)
#Config.set('modules', 'ShowBorder', '')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout


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
    return frame

def frame2texture(frame, size):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 0)
    texture = Texture.create(size=size)
    texture.blit_buffer(frame.tostring())
    return texture

def play_sound(audio_segment, audio_time):
    return play_buffer(
        audio_segment[audio_time*1000:].raw_data,
        num_channels = audio_segment.channels,
        bytes_per_sample = audio_segment.sample_width,
        sample_rate = audio_segment.frame_rate
        )


class RootWidget(FloatLayout):
    image_texture = ObjectProperty(None)
    path = ''
    image_src = StringProperty('')
    frame_count = 0
    pre_frame_count = 0
    sa = 0
    frame_max = 100
    tex_size = (0,0)
    event = None

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._key_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        Window.bind(on_dropfile=self._on_file_drop)

        self.load_movie_and_sound(dir_path+'/movies/test.mp4')

        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.tex_size)

        self.path = dir_path+'/movies/'
        self.ids['file_list_view'].path = self.path
        self.ids['file_icon_view'].path = self.path
    
    def load_movie_and_sound(self, movie_path):
        self.cap, self.tex_size, self.frame_max, self.fps = load_movie(movie_path)
        self.ids['slider'].max = self.frame_max -1
        self.ids['slider'].value = 0
        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.tex_size)
        self.sound = AudioSegment.from_file(movie_path, format=movie_path.split('.')[-1])
        self.sound += ratio_to_db(0.05)
        if self.event != None:
            self.event.cancel()
            self.event = None
            self.sound_play.stop()
        self.sa = 0
        self.frame_count = 0
    
    def cursor_moved(self, value):
        if self.event == None:
            self.frame = pic_frame(self.cap, int(value))
            self.frame_count = int(value)
            self.pre_frame_count = int(value)
        self.image_texture = frame2texture(self.frame, self.tex_size)
    
    def update(self, delta_time):
        self.sa += 1/self.fps - delta_time
        if self.sa > 0:
            sleep(self.sa)
        self.frame_count = self.ids['slider'].value + 1
        _play_frame = int((time()-self.play_start_time)*self.fps)
        if not _play_frame - 3 <= self.frame_count <= _play_frame + 3:
            # 表示している画像と音声が±3フレームずれたとき
            self.frame_count = _play_frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)
            self.play_start_time = time() - self.frame_count / self.fps
            self.sa = 0
        if self.pre_frame_count != self.ids['slider'].value:
            # スライダーのカーソル位置を移動したとき
            self.frame_count = self.ids['slider'].value
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)
            self.sound_play.stop()
            self.sound_play = play_sound(self.sound, self.frame_count/self.fps)
            self.sa = 0
            self.play_start_time = time() - self.ids['slider'].value/ self.fps
        if self.frame_count > self.frame_max - 1:
            # 最後まで再生したとき
            self.event.cancel()
            self.event = None
            return
        self.ids['slider'].value = self.frame_count
        self.pre_frame_count = self.frame_count
        _, self.frame = self.cap.read()
    
    def selected(self, file_path):
        if len(file_path) == 1:
            self.load_movie_and_sound(file_path[0])

    def _key_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if self.event == None and keycode[1] == 'spacebar':
            self.play_start_time = time() - self.frame_count / self.fps
            self.event = Clock.schedule_interval(self.update, 1/self.fps)
            self.sa = 0
            self.sound_play = play_sound(self.sound, self.frame_count/self.fps)
        elif  keycode[1] == 'spacebar':
            self.event.cancel()
            self.event = None
            self.sound_play.stop()
    
    def _on_file_drop(self, window, file_path):
        file_path = file_path.decode('utf-8')
        if os.path.isdir(file_path):
            print('ディレクトリ')
        else:
            self.load_movie_and_sound(file_path)


class MVEditorApp(App):
    title = f'MV Editor v{version}'

    def build(self):
        return RootWidget()
    
if __name__=='__main__':
    App = MVEditorApp()
    App.run()