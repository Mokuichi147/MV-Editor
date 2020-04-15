import cv2
import os
import re
from time import sleep, time
from tkinter import Tk
from tkinter.filedialog import askdirectory

from pydub import AudioSegment
from pydub.utils import ratio_to_db
from utils.core import *
SETTINGS = load_json(dir_path+'/resources/settings.json')

_root = Tk()
_root.withdraw()

from kivy.config import Config
Config.set('graphics', 'width', SETTINGS['config']['width'])
Config.set('graphics', 'height', SETTINGS['config']['height'])
Config.set('graphics', 'minimum_width', SETTINGS['config']['minimum_width'])
Config.set('graphics', 'minimum_height', SETTINGS['config']['minimum_height'])
#Config.set('modules', 'ShowBorder', '')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

version = '0.0.1'
LabelBase.register(DEFAULT_FONT, dir_path+'/Fonts/NotoSansJP-Medium.otf')


class RootWidget(FloatLayout):
    # Path関連
    app_dir_path = dir_path
    # Setting関連
    setting_inputs = []
    settings = SETTINGS
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
    audio = None
    audio_event = False
    spacebar_down = False
    # Splitter関連
    mouce_down_object_type = None
    mouce_down_object_name = None

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.load_setting()

        self._keyboard = Window.request_keyboard(self._key_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        Window.bind(on_dropfile=self._on_file_drop)

        self.load_file(self.settings['pre_project']['path'])
        if self.project.video:
            self.load_video_and_audio(self.project.project_path + self.project.videos[0]['path'])

        self.visible_view('file_selection_view')
        self.hidden_view('setting_view')
        self.hidden_view('output_view')
    
    def update(self, delta_time):
        self.sa += 1/self.fps - delta_time
        if self.sa > 0:
            sleep(self.sa)
            
        self.frame_count = self.ids['video_time_slider'].value + 1
        _play_frame = round((time()-self.play_start_time)*self.fps)
        if _play_frame > self.frame_count + 10:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, _play_frame)
            self.play_start_time = time() - _play_frame / self.fps
            self.sa = 0
        else:
            for i in range(max(_play_frame - int(self.frame_count), 0)):
                _, _ = self.cap.read()
                self.sa = 0
        self.frame_count = _play_frame

        if self.pre_frame_count != self.ids['video_time_slider'].value:
            # スライダーのカーソル位置を移動したとき
            self.frame_count = self.ids['video_time_slider'].value
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)
            if self.audio != None and self.audio_event:
                self.audio_play.stop()
                self.audio_play = play_audio(self.audio, self.frame_count/self.fps)
            self.sa = 0
            self.play_start_time = time() - self.ids['video_time_slider'].value/self.fps

        if self.frame_count > self.frame_max - 1:
            # 最後まで再生したとき
            self.playback_stop()
            return
        self.ids['video_time_slider'].value = self.frame_count
        self.pre_frame_count = self.frame_count
        _, self.frame = self.cap.read()
    
    def cursor_moved(self, value):
        if self.playback_event == None:
            self.frame = pic_frame(self.cap, int(value))
            self.frame_count = int(value)
            self.pre_frame_count = int(value)
        self.image_texture = frame2texture(self.frame, self.texture_size, self.settings['play_preview']['maximum_size'])
        _time_second = int(self.frame_count / self.fps)
        self.ids['video_time_label'].text = f'{_time_second//60:>2}:{_time_second%60:0>2}'
    
    ''' ファイル読み込み '''
    def load_video_and_audio(self, video_path):
        if self.playback_event != None:
            self.playback_stop()
            self.audio_event = False
        self.audio = None
        self.cap, self.texture_size, self.frame_max, self.fps = load_video(video_path)
        self.ids['video_time_slider'].max = self.frame_max -1
        self.ids['video_time_slider'].value = 0
        self.ids['video_time_label'].text = '0:00'
        self.frame = pic_frame(self.cap, 0)
        self.image_texture = frame2texture(self.frame, self.texture_size, self.settings['play_preview']['maximum_size'])
        self.sa = 0
        self.frame_count = 0
        async_func(self.load_audio, video_path)

    def load_audio(self, path):
        try:
            self.audio = AudioSegment.from_file(path, format=path.split('.')[-1])
            self.audio += ratio_to_db(self.settings['play_preview']['audio_ratio'])
        except:
            self.audio = None
    
    def load_file(self, file_path):
        if not os.path.isdir(file_path):
            self.load_video_and_audio(file_path)
            return

        self.project = ProjectData(file_path)
        if self.project.activate:
            self.ids['project_create'].text = ''
            self.project.update()
        else:
            self.ids['project_create'].text = 'プロジェクト作成'
        
        # title等の変更
        self.project_name = path2name(self.project.project_path)
        self.ids['project_select'].text = '> ' + self.project_name
        Window.set_title(f'MV Editor v{version} - {self.project_name}')

        _files = os.listdir(self.project.project_path)
        self.project_path_listdir = [f for f in _files if os.path.isdir(os.path.join(self.project.project_path, f))]
        self.ids['project_dirs'].clear_widgets()
        for dir_count, dir_path in enumerate(self.project_path_listdir):
            btn = ToggleButton(text = dir_path,
                                group = 'listdir',
                                background_normal = 'resources/listdir.png',
                                background_down = 'resources/listdir_down.png',
                                height = 30,
                                size_hint = (1,None),
                                halign = 'left',
                                valign = 'top',
                                text_size = (180, 30-5),
                                on_press = lambda x: self.dir_selected(x, x.text, x.state))
            if dir_count == 0:
                btn.state = 'down'
            self.ids['project_dirs'].add_widget(btn)

        self.ids['project_dirs'].parent.width = 200
        if len(self.project_path_listdir) > 0:
            self.load_files(self.project.project_path + '/' + self.project_path_listdir[0])
        else:
            self.load_files(self.project.project_path)
    
    def load_setting(self):
        self.settings = load_json(self.app_dir_path+'/resources/settings.json')
        lang = load_json(self.app_dir_path+'/resources/lang_ja.json')
        _group_height = 50
        _item_height = 30
        self.setting_inputs.clear()
        for group in self.settings:
            if group == 'pre_project':
                return
            group_label = Label(text = lang['_config'][group],
                                 font_size = 25,
                                 height = _group_height,
                                 size_hint = (1, None),
                                 halign = 'left',
                                 valign = 'top',
                                 text_size = (self.ids['setting_left'].width-20, _group_height-10))
            self.ids['setting_view_left'].add_widget(group_label)
            group_label = Label(text = '',
                                 height = _group_height,
                                 size_hint = (1, None))
            self.ids['setting_view_right'].add_widget(group_label)

            for key in self.settings[group]:
                text_la = Label(text = lang[group][key],
                                 height = _item_height,
                                 size_hint = (1, None),
                                 halign = 'left',
                                 valign = 'top',
                                 text_size = (self.ids['setting_left'].width-20, _item_height-5))
                self.ids['setting_view_left'].add_widget(text_la)
                text_in = TextInput(text = str(self.settings[group][key]),
                                     height = _item_height,
                                     size_hint = (1, None),
                                     background_normal = self.app_dir_path+'/resources/alpha.png',
                                     background_color = (0.15, 0.15, 0.15, 1),
                                     foreground_color = (1, 1, 1, 1),
                                     cursor_color = (0.50, 0.50, 0.50, 1))
                self.setting_inputs.append(text_in)
                self.ids['setting_view_right'].add_widget(text_in)
            
            space_label = Label(text = '',
                                 height = _item_height,
                                 size_hint = (1, None))
            self.ids['setting_view_left'].add_widget(space_label)
            space_label = Label(text = '',
                                 height = _item_height,
                                 size_hint = (1, None))
            self.ids['setting_view_right'].add_widget(space_label)

    def write_setting(self):
        _path = self.app_dir_path+'/resources/settings.json'
        self.settings = load_json(_path)
        _count = 0
        for group in self.settings:
            if group == 'pre_project':
                continue
            for key in self.settings[group]:
                if key == 'audio_ratio' or key == 'maximum_fps':
                    self.settings[group][key] = float(self.setting_inputs[_count].text)
                else:
                    self.settings[group][key] = int(self.setting_inputs[_count].text)
                _count += 1
        write_json(_path, self.settings)
        self._keyboard = Window.request_keyboard(self._key_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
    
    ''' モード切替 '''
    def project_button(self, button_state):
        if button_state == 'down':
            self.visible_view('file_selection_view')
            self.hidden_view('setting_view')
            self.hidden_view('output_view')
            return
        self.ids['project_button'].state = 'down'
        _width = self.ids['project_scrollview'].width
        self.ids['project_scrollview'].width = 200 if _width == 0 else 0
        self.ids['project_select'].text = '> ' + self.project_name if _width == 0 else ''
    
    def project_create_button(self):
        self.project.create()
        self.load_file(self.project.project_path)
    
    def setting_button(self, button_state):
        if button_state == 'down':
            self.visible_view('setting_view')
            self.hidden_view('file_selection_view')
            self.hidden_view('output_view')
            return
        self.ids['setting_button'].state = 'down'
    
    def setting_state(self, button_state):
        if button_state == 'down':
            return
        self.write_setting()
    
    def output_button(self, button_state):
        if button_state == 'down':
            self.visible_view('output_view')
            self.hidden_view('file_selection_view')
            self.hidden_view('setting_view')
            return
        self.ids['output_button'].state = 'down'
    
    ''' Project View関連 '''
    def project_selected(self):
        _project_path = askdirectory()
        if _project_path == '':
            return
        self.load_file(_project_path)

    def dir_selected(self, button, text, state):
        if state == 'normal':
            button.state = 'down'
            return
        _num = self.project_path_listdir.index(text)
        self.load_files(self.project.project_path + '/' + self.project_path_listdir[_num])
    
    def file_selected(self, abs_file_path):
        if len(abs_file_path) != 1:
            return
        abs_file_path = slash_path(abs_file_path[0])
        if check_type(abs_file_path) == 'video':
            file_path = self.project.relative_path(abs_file_path)
            _, size, max_frame, _ = load_video(abs_file_path)
            self.project.add_video(file_path, audio=False, frame=(0,max_frame))
            self.project.save()
            #self.load_video_and_audio(file_path[0])
    
    ''' frame関連 '''
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
    
    ''' プレビュー画面の再生 '''
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
        if self.audio != None and not self.audio_event:
            self.audio_play = play_audio(self.audio, self.frame_count/self.fps)
            self.audio_event = True
        self.ids['playback_button'].background_normal = 'resources/playback_stop_button.png'
        self.ids['playback_button'].background_down = 'resources/playback_button_down.png'
    
    def playback_stop(self, video=True):
        if video:
            self.playback_event.cancel()
            self.playback_event = None
        if self.audio != None and self.audio_event:
            self.audio_play.stop()
            self.audio_event = False
        self.ids['playback_button'].background_normal = 'resources/playback_button.png'
        self.ids['playback_button'].background_down = 'resources/playback_stop_button_down.png'
    
    ''' SplitterをButtonで代用 '''
    def object_moved(self, object_type, object_name=None):
        self.mouce_down_object_type = object_type
        self.mouce_down_object_name = object_name
    
    def resize_view(self, touch, parent_view, view, min_s, min_p, mode='width'):
        _mode = 0 if mode == 'width' else 1
        view_size = self.ids[parent_view].size[_mode] - sum(self.ids[parent_view].padding[_mode::2])
        self.ids[view].size_hint = [1, None] if _mode else [None, 1]
        if view_size - touch.pos[_mode] < min_s:
            if view_size - touch.pos[_mode] < min_s - 150:
                self.ids[view].size[_mode] = 0
            else:
                self.ids[view].size[_mode] = min_s
            return
        elif touch.pos[_mode] < min_p:
            if touch.pos[_mode] < min_p - 50:
                self.ids[view].size[_mode] = view_size - 8
            else:
                self.ids[view].size[_mode] = view_size - min_p
            return
        self.ids[view].size[_mode] = view_size - touch.pos[_mode]
    
    def on_touch_move(self, touch):
        if not 'pos' in touch.profile:
            return
        elif self.mouce_down_object_type == 'vertical_splitter':
            self.resize_view(touch, 'root_view', 'vertical_splitter_upper', 205, 100, mode='height')
        elif self.mouce_down_object_type == 'horizontal_splitter':
            self.resize_view(touch, 'vertical_splitter_upper', 'horizontal_splitter_right', 300, 200, mode='width')
        elif self.mouce_down_object_type == 'file':
            pass
    
    def on_touch_up(self, touch):
        if self.mouce_down_object_type == 'file':
            print(slash_path(self.mouce_down_object_name[0]))
        if self.mouce_down_object_type != None:
            self.mouce_down_object_type = None
            self.mouce_down_object_name = None

    ''' FileChooserIconViewを置き換える '''
    def load_files(self, path):
        self.project.load_dir(path)
        self.project.save()
        _files = os.listdir(path)
        self.file_listdir = [f for f in _files if os.path.isfile(os.path.join(path, f))]
        self.ids['file_stack'].clear_widgets()
        for _count, _name in enumerate(self.file_listdir):
            _path = self.project.relative_path(path + '/' + _name)
            _audio = self.project.dirs[_path]['audio']
            _video = self.project.dirs[_path]['video']
            _type  = self.project.dirs[_path]['type']
            image_path = get_content_image_path(self.project.project_path, _path)
            btn = ToggleButton(text = _name,
                                group = 'stack_file',
                                height = 128,
                                width = 128,
                                background_normal = image_path,
                                border = (0,0,0,0),
                                size_hint = (None, None),
                                halign = 'center',
                                valign = 'bottom',
                                text_size = (128, 128),
                                on_press = lambda x: print(x, x.text, x.state))
            self.ids['file_stack'].add_widget(btn)
    
    ''' モード切替時のviewの表示・非表示 '''
    def hidden_view(self, view_id):
        self.ids[view_id].size_hint = (None, None)
        self.ids[view_id].size = (0, 0)
    
    def visible_view(self, view_id):
        self.ids[view_id].size_hint = (1, 1)

    ''' キーボード '''
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
    
    ''' ドラッグ&ドロップ '''
    def _on_file_drop(self, window, file_path):
        file_path = file_path.decode('utf-8')
        file_path = slash_path(file_path)
        self.load_file(file_path)

class MVEditorApp(App):
    title = f"MV Editor v{version} - {path2name(SETTINGS['pre_project']['path'])}"
    app_dir_path = dir_path
    resources_path = app_dir_path + '/resources/'

    def build(self):
        return RootWidget()
    
if __name__=='__main__':
    App = MVEditorApp()
    App.run()