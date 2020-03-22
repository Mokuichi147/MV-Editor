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
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout


version = '0.0.1'
LabelBase.register(DEFAULT_FONT, 'Fonts/NotoSansJP-Medium.otf')
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
    frame_count = 0
    pre_frame_count = 0
    sa = 0
    frame_max = 100
    texture_size = (0,0)
    playback_event = None
    spacebar_down = False

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._key_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        Window.bind(on_dropfile=self._on_file_drop)

        self.load_movie_and_sound(dir_path+'/Movies/test.mp4')

        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.texture_size)

        self.path = dir_path+'/Movies/'
        self.ids['file_list_view'].path = self.path
        self.ids['file_icon_view'].path = self.path
    
    def load_movie_and_sound(self, movie_path):
        self.cap, self.texture_size, self.frame_max, self.fps = load_movie(movie_path)
        self.ids['video_time_slider'].max = self.frame_max -1
        self.ids['video_time_slider'].value = 0
        self.ids['video_time_label'].text = '0:00'
        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.texture_size)
        self.sound = AudioSegment.from_file(movie_path, format=movie_path.split('.')[-1])
        self.sound += ratio_to_db(0.05)
        if self.playback_event != None:
            self.playback_stop()
        self.sa = 0
        self.frame_count = 0
    
    def cursor_moved(self, value):
        if self.playback_event == None:
            self.frame = pic_frame(self.cap, int(value))
            self.frame_count = int(value)
            self.pre_frame_count = int(value)
        self.image_texture = frame2texture(self.frame, self.texture_size)
        _time_second = int(self.frame_count / self.fps)
        self.ids['video_time_label'].text = f'{_time_second//60:>2}:{_time_second%60:0>2}'
    
    def update(self, delta_time):
        self.sa += 1/self.fps - delta_time
        if self.sa > 0:
            sleep(self.sa)
        self.frame_count = self.ids['video_time_slider'].value + 1
        _play_frame = round((time()-self.play_start_time)*self.fps)
        if not _play_frame - 3 <= self.frame_count <= _play_frame + 3:
            # 表示している画像と音声が±3フレームずれたとき
            self.frame_count = _play_frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)
            self.play_start_time = time() - self.frame_count / self.fps
            self.sa = 0
        if self.pre_frame_count != self.ids['video_time_slider'].value:
            # スライダーのカーソル位置を移動したとき
            self.frame_count = self.ids['video_time_slider'].value
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)
            self.sound_play.stop()
            self.sound_play = play_sound(self.sound, self.frame_count/self.fps)
            self.sa = 0
            self.play_start_time = time() - self.ids['video_time_slider'].value/ self.fps
        if self.frame_count > self.frame_max - 1:
            # 最後まで再生したとき
            self.playback_stop()
            return
        self.ids['video_time_slider'].value = self.frame_count
        self.pre_frame_count = self.frame_count
        _, self.frame = self.cap.read()
    
    def file_selected(self, file_path):
        if len(file_path) == 1:
            self.load_movie_and_sound(file_path[0])
    
    def set_zero_frame(self):
        if self.playback_event != None:
            self.playback_stop()
        self.frame_count = 0
        self.pre_frame_count = 0
        self.ids['video_time_slider'].value = self.frame_count
        self.frame = pic_frame(self.cap, self.frame_count)
        
    def previous_frame(self):
        self.frame_count -= 1
        if self.frame_count < 0:
            self.frame_count += 1
            return
        self.ids['video_time_slider'].value = self.frame_count
        self.pre_frame_count = self.frame_count
        self.frame = pic_frame(self.cap, self.frame_count)
    
    def next_frame(self):
        self.frame_count += 1
        if self.frame_count > self.frame_max - 1:
            self.frame_count -= 1
            return
        self.ids['video_time_slider'].value = self.frame_count
        self.pre_frame_count = self.frame_count
        _, self.frame = self.cap.read()
    
    def playback_start_or_stop(self):
        if self.playback_event == None:
            self.playback_start()
        else:
            self.playback_stop()
    
    def playback_start(self, video=True, sound=True):
        self.play_start_time = time() - self.frame_count / self.fps
        if video:
            self.playback_event = Clock.schedule_interval(self.update, 1/self.fps)
            self.sa = 0
        if sound:
            self.sound_play = play_sound(self.sound, self.frame_count/self.fps)
        self.ids['playback_button'].background_normal = 'Resources/playback_stop_button.png'
        self.ids['playback_button'].background_down = 'Resources/playback_button_down.png'
    
    def playback_stop(self, video=True, sound=True):
        if video:
            self.playback_event.cancel()
            self.playback_event = None
        if sound:
            self.sound_play.stop()
        self.ids['playback_button'].background_normal = 'Resources/playback_button.png'
        self.ids['playback_button'].background_down = 'Resources/playback_stop_button_down.png'

    def _key_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar' and not self.spacebar_down:
            self.playback_start_or_stop()
            self.spacebar_down = True
    
    def _on_key_up(self, keyboard, keycode):
        if keycode[1] == 'spacebar':
            self.spacebar_down = False
    
    def _on_file_drop(self, window, file_path):
        file_path = file_path.decode('utf-8')
        if os.path.isdir(file_path):
            self.ids['file_list_view'].path = file_path
            self.ids['file_icon_view'].path = file_path
        else:
            self.load_movie_and_sound(file_path)


class MVEditorApp(App):
    title = f'MV Editor v{version}'

    def build(self):
        return RootWidget()
    
if __name__=='__main__':
    App = MVEditorApp()
    App.run()