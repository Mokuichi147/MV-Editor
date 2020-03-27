import cv2
import os
from time import sleep, time
from tkinter import Tk
from tkinter.filedialog import askdirectory

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
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.floatlayout import FloatLayout

from utils.core import *

version = '0.0.1'
LabelBase.register(DEFAULT_FONT, 'Fonts/NotoSansJP-Medium.otf')
dir_path = os.path.abspath(os.path.dirname(__file__))


class RootWidget(FloatLayout):
    # Project関連
    project_name = ''
    project_path = ''
    project_path_listdir = []
    # Video Preview関連
    image_texture = ObjectProperty(None)
    frame_count = 0
    pre_frame_count = 0
    sa = 0
    frame_max = 100
    texture_size = (0,0)
    playback_event = None
    sound = None
    spacebar_down = False
    # Splitter関連
    button_move = None

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._key_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        Window.bind(on_dropfile=self._on_file_drop)

        self.load_file(dir_path + '/TestProject')
        self.load_movie_and_sound(self.project_path+'/Video/test.mp4')
    
    def load_movie_and_sound(self, movie_path):
        if self.playback_event != None:
            self.playback_stop()
        self.cap, self.texture_size, self.frame_max, self.fps = load_movie(movie_path)
        self.ids['video_time_slider'].max = self.frame_max -1
        self.ids['video_time_slider'].value = 0
        self.ids['video_time_label'].text = '0:00'
        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.texture_size)
        try:
            self.sound = AudioSegment.from_file(movie_path, format=movie_path.split('.')[-1])
            self.sound += ratio_to_db(0.05)
        except:
            self.sound = None
        self.sa = 0
        self.frame_count = 0
    
    def load_file(self, file_path):
        if not os.path.isdir(file_path):
            self.load_movie_and_sound(file_path)
            return
        self.project_path = file_path
        # title等の変更
        self.project_name = self.project_path.split('/')[-1]
        if self.project_name == '':
            self.project_name = self.project_path
        self.ids['project_select'].text = '> ' + self.project_name
        Window.set_title(f'MV Editor v{version} - {self.project_name}')

        _files = os.listdir(self.project_path)
        self.project_path_listdir = [f for f in _files if os.path.isdir(os.path.join(self.project_path, f))]
        self.ids['project_dirs'].clear_widgets()
        for dir_count in range(len(self.project_path_listdir)):
            btn = ToggleButton(
                text = self.project_path_listdir[dir_count],
                group = 'listdir',
                background_normal = 'resources/listdir.png',
                background_down = 'resources/listdir_down.png',
                height = 30,
                size_hint = (1,None),
                halign = 'left',
                valign = 'top',
                text_size = (130, 30-5),
                on_press = lambda x: self.dir_selected(x.text))
            if dir_count == 0:
                btn.state = 'down'
            self.ids['project_dirs'].add_widget(btn)
        if len(self.project_path_listdir) > 0:
            self.ids['project_dirs'].parent.width = 150
            self.ids['file_icon_view'].rootpath = self.project_path + '/' + self.project_path_listdir[0]
        else:
            self.ids['file_icon_view'].rootpath = self.project_path
            self.ids['project_dirs'].parent.width = 0
            self.ids['project_select'].text = ''
    
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
            if self.sound != None:
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
    
    def project_button(self, button_state):
        if button_state == 'down':
            return
        self.ids['project_button'].state = 'down'
        _width = self.ids['project_scrollview'].width
        self.ids['project_scrollview'].width = 150 if _width == 0 else 0
        self.ids['project_select'].text = '> ' + self.project_name if _width == 0 else ''
    
    def project_selected(self):
        _root = Tk()
        _root.withdraw()
        _project_path = askdirectory()
        _root.destroy()
        if _project_path == '':
            return
        self.load_file(_project_path)
    
    def file_selected(self, file_path):
        if len(file_path) != 1:
            return
        if file_path[0].split('.')[-1].lower() in ['mp4', 'mov']:
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
    
    def playback_start(self, video=True):
        self.play_start_time = time() - self.frame_count / self.fps
        if video:
            self.playback_event = Clock.schedule_interval(self.update, 1/self.fps)
            self.sa = 0
        if self.sound != None:
            self.sound_play = play_sound(self.sound, self.frame_count/self.fps)
        self.ids['playback_button'].background_normal = 'resources/playback_stop_button.png'
        self.ids['playback_button'].background_down = 'resources/playback_button_down.png'
    
    def playback_stop(self, video=True):
        if video:
            self.playback_event.cancel()
            self.playback_event = None
        if self.sound != None:
            self.sound_play.stop()
        self.ids['playback_button'].background_normal = 'resources/playback_button.png'
        self.ids['playback_button'].background_down = 'resources/playback_stop_button_down.png'
    
    def button_moved(self, button_id):
        self.button_move = button_id
    
    def on_touch_move(self, touch):
        if not 'pos' in touch.profile:
            return
        elif self.button_move == 'vertical_splitter':
            height = self.ids['vertical_splitter_lower'].size[1] + self.ids['vertical_splitter_upper'].size[1] + self.ids[self.button_move].size[1]
            if height - touch.pos[1] < 205 or touch.pos[1] < 100:
                return
            width = self.ids['vertical_splitter_upper'].size[0]
            pos_height = height - touch.pos[1]
            self.ids[self.button_move].pos[1] = pos_height
            self.ids['vertical_splitter_upper'].size = [width, pos_height]
            self.ids['vertical_splitter_upper'].size_hint = [1, None]
        elif self.button_move == 'horizontal_splitter':
            width = self.ids['horizontal_splitter_left'].size[0] + self.ids['horizontal_splitter_right'].size[0] + self.ids[self.button_move].size[0]
            if width - touch.pos[0] < 300 or touch.pos[0] < 5:
                return
            height = self.ids['horizontal_splitter_right'].size[1]
            pos_width = width - touch.pos[0]
            self.ids[self.button_move].pos[0] = pos_width
            self.ids['horizontal_splitter_right'].size = [pos_width, height]
            self.ids['horizontal_splitter_right'].size_hint = [None, 1]
    
    def on_touch_up(self, touch):
        if self.button_move != None:
            self.button_move = None

    def dir_selected(self, text):
        _num = self.project_path_listdir.index(text)
        self.ids['file_icon_view'].rootpath = self.project_path + '/' + self.project_path_listdir[_num]

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
        elif keycode[1] == 'left' and self.playback_event == None:
            self.previous_frame()
        elif keycode[1] == 'right' and self.playback_event == None:
            self.next_frame()
    
    def _on_file_drop(self, window, file_path):
        file_path = file_path.decode('utf-8')
        self.load_file(file_path)

class MVEditorApp(App):
    title = f'MV Editor v{version}'

    def build(self):
        return RootWidget()
    
if __name__=='__main__':
    App = MVEditorApp()
    App.run()