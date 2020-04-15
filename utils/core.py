import json
import os
import re
import sys
from tempfile import gettempdir
from time import time as T
from threading import Thread

import cv2
import ffmpeg
import numpy as np
from PIL import Image
from simpleaudio import play_buffer
from kivy.graphics.texture import Texture


def slash_path(path):
    '''
    \が入っているパスを/にする
    '''
    if '\\' in path:
        return '/'.join(path.split('\\'))
    return path


if not os.path.exists(gettempdir()+'/mv-editor'):
    os.mkdir(gettempdir()+'/mv-editor')
temp_dir_path = slash_path(gettempdir()) + '/mv-editor'

dir_path = os.path.abspath(os.path.dirname(__file__))
dir_path = slash_path(dir_path)
dir_path = dir_path.split('/')[:-1]
dir_path = '/'.join(dir_path)
resources_path = dir_path + '/' + 'resources'


class ProjectData:
    def __init__(self, path):
        self.project_path = path
        self.project_json = self.project_path + '/project.json'
        
        if os.path.isfile(self.project_json):
            self.activate = True
        else:
            self.activate = False
    
    def create(self):
        '''
        プロジェクトのデータを保存するためのjsonとディレクトリを作成する
        '''
        self.activate = True
        self.__set_data(resources_path + '/project.json')
        self.save()
        os.makedirs(self.project_path+'/Font', exist_ok=True)
        os.makedirs(self.project_path+'/Image', exist_ok=True)
        os.makedirs(self.project_path+'/Audio', exist_ok=True)
        os.makedirs(self.project_path+'/Video', exist_ok=True)
    
    def save(self):
        '''
        project.jsonを上書き保存する
        '''
        _data = self.__create_data()
        write_json(self.project_json, _data)
    
    def update(self):
        '''
        project.jsonを読み込む
        '''
        self.__set_data(self.project_json)
    
    def relative_path(self, path):
        '''
        プロジェクトディレクトリに対する相対パスを返す
        '''
        if re.match(self.project_path, path):
            return path[len(self.project_path):]
        return path
    
    def load_dir(self, path):
        '''
        ディレクトリ内のファイルを読み込む時に高速化するためのデータを作成する
        '''
        _files = os.listdir(path)
        _file_listdir = [f for f in _files if os.path.isfile(os.path.join(path, f))]
        for _name in _file_listdir:
            _name = self.relative_path(path + '/' + _name)
            if _name in self.dirs:
                continue
            self.dirs[_name] = {}
            self.dirs[_name]['type']  = check_type(path + '/' + _name)
            _audio, _video = check_video(path)
            self.dirs[_name]['video'] = _video
            self.dirs[_name]['audio'] = _audio
        
    def __create_data(self):
        _data = {}
        _data['video'] = self.video
        _data['audio'] = self.audio
        _data['fps'] = self.fps
        _data['maximum_frame'] = self.maximum_frame
        _data['width'] = self.width
        _data['height'] = self.height
        _data['output_fmt'] = self.output_fmt
        _data['content'] = self.__create_list_data(self.content)
        _data['dirs'] = self.dirs
        return _data
    
    def __create_list_data(self, list_data):
        _list = []
        for _count, _content in enumerate(list_data):
            if type(_content) is list:
                _list.append(self.__create_list_data(_content))
            elif type(_content) is int:
                return list_data
            else:
                _list.append({})
                for _key in _content.keys():
                    if type(_content[_key]) is list:
                        _list[_count][_key] = self.__create_list_data(_content[_key])
                    else:
                        _list[_count][_key] = _content[_key]
        return _list
    
    def __set_data(self, path):
        _data = load_json(path)
        self.video = _data['video']
        self.audio = _data['audio']
        self.fps = _data['fps']
        self.maximum_frame = _data['maximum_frame']
        self.width = _data['width']
        self.height = _data['height']
        self.output_fmt = _data['output_fmt']
        self.content = _data['content']
        self.dirs = _data['dirs']
        self.fonts  = []
        self.images = []
        self.audios = []
        self.videos = []
        for _content in self.content:
            self.fonts  += [i for i in _content if i['type'] == 'font']
            self.images += [i for i in _content if i['type'] == 'image']
            self.audios += [i for i in _content if i['type'] == 'audio']
            self.videos += [i for i in _content if i['type'] == 'video']
    
    def __se_frame(self, content):
        _start_frame = content['start_frame']
        _end_frame = _start_frame + content['frame'][1] - content['frame'][0]
        return _start_frame, _end_frame
    
    def __check_content_index(self, frame_count):
        _content_index = []
        for i, _content_list in enumerate(self.content):
            for j, _content in enumerate(_content_list):
                _sf, _ef = self.__se_frame(_content)
                if _sf < frame_count < _ef:
                    _content_index.append([i, j])
        return _content_index
    
    def __check_content_block(self, contents, frame=(0,0)):
        for _content in contents:
            _sf, _ef = self.__se_frame(_content)
            if not (_ef < frame[0] or frame[1] < _sf):
                return False
        return True
    
    def __content_index(self, data):
        _frame = self.__se_frame(data)
        for i, contents in enumerate(self.content):
            if self.__check_content_block(contents, _frame):
                return i
        return len(self.content)
    
    def add_image(self, path, animation_val=None, start_frame=0, frame=(0,0), size=None, pos=(0,0), angle=0):
        '''
        コンテンツに画像を追加する
        '''
        _data = {'type': 'image', 'path': path}
        _data['animation'] = False if animation_val==None else True
        _data['animation_val'] = animation_val
        _data['start_frame'] = start_frame
        _data['frame'] = frame
        _data['full_size'] = True if size==None else False
        _data['size'] = size
        _data['pos_x'] = pos[0]
        _data['pos_y'] = pos[1]
        _data['angle'] = angle
        if len(self.content) == 0:
            self.content.append([_data])
        num = self.__content_index(_data)
        if len(self.content) == num:
            self.content.append([_data])
        else:
            self.content[num].append(_data)
    
    def add_video(self, path, video=True, audio=True, animation_val=None, start_frame=0, frame=(0,0), size=None, pos=(0,0), angle=0):
        '''
        コンテンツに動画を追加する
        '''
        _data = {'type': 'video', 'path': path}
        _data['video_iamge'] = video
        _data['video_audio'] = audio
        _data['animation'] = False if animation_val==None else True
        _data['animation_val'] = animation_val
        _data['start_frame'] = start_frame
        _data['frame'] = frame
        _data['full_size'] = True if size==None else False
        _data['size'] = size
        _data['pos_x'] = pos[0]
        _data['pos_y'] = pos[1]
        _data['angle'] = angle
        if len(self.content) == 0:
            self.content.append([_data])
        num = self.__content_index(_data)
        if len(self.content) == num:
            self.content.append([_data])
        else:
            self.content[num].append(_data)

def async_func(function, *args):
    '''
    関数を別スレッドで実行する
    '''
    _th = Thread(target=function, args=args)
    _th.daemon = True
    _th.start()

def load_json(path):
    '''
    jsonを読み込む
    '''
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    '''
    jsonを書き込む
    '''
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def check_type(path):
    '''
    拡張子からコンテンツのタイプを返す
    '''
    try:
        file_format = path.split('.')[-1].lower()
    except:
        return
    if file_format in ['mp4', 'mov', 'avi', 'mkv', 'flv', 'mpeg', 'mpg']:
        return 'video'
    elif file_format in ['mp3', 'wav', 'aac', 'flac', 'm4a']:
        return 'audio'
    elif file_format in ['jpg', 'jpeg', 'png']:
        return 'image'
    elif file_format in ['ttf', 'otf']:
        return 'font'
    else:
        return

def check_video(path):
    '''
    動画と音声のデータがあるかを返す
    '''
    _audio = False
    _video = False
    try:
        _video_data = ffmpeg.probe(path)
    except:
        return _audio, _video
    for stream in _video_data['streams']:
        if stream['codec_type'] == 'audio':
            _audio = True
        elif stream['codec_type'] == 'video':
            _video = True
    return _audio, _video

def load_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    max_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return cap, (width,height), max_count, fps

def path2name(path):
    _name = path.split('/')[-1]
    if _name == '':
        _name = path
    return _name

def pic_frame(cap, frame_count):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
    ret, frame = cap.read()
    if not ret:
        return
    return frame

def pil_image2image(pil_image):
    np_array = np.array(pil_image, dtype=np.uint8)
    if np_array.ndim == 2:
        return np_array
    elif np_array.shape[2] == 3:
        return np_array[:, :, ::-1]
    elif np_array.shape[2] == 4:
        return np_array[:, :, [2,1,0,3]]

def frame2pil_image(frame, alpha=False):
    # time: 0.001s
    if alpha:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # time: 0.003s
    pil_image = Image.fromarray(frame)
    return pil_image

def pil_image2texture(pil_image):
    # time: 0s
    texture = Texture.create(size=pil_image.size)
    # time: 0.004s
    byte_data = pil_image.tobytes()
    # time: 0.004~0.009s
    texture.blit_buffer(byte_data)
    # time: 0s
    texture.flip_vertical()
    return texture

''' time: 0.012~0.017s '''
def frame2texture_pil(frame):
    pil_image = frame2pil_image(frame)
    return pil_image2texture(pil_image)

''' time: 0.007~0.013s '''
def frame2texture(frame, size, max_size):
    # time: 0.001s or 0.002s
    if size[0] > max_size or size[1] > max_size:
        scale = max_size / size[0] if size[0] > size[1] else max_size / size[1]
        size = (int(size[0]*scale), int(size[1]*scale))
        frame = cv2.resize(frame, size)
    # time: 0.001s
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # time: 0s
    texture = Texture.create(size=size)
    # time: 0.002~0.003s
    str_data = frame.tostring()
    # time: 0.004~0.009s
    texture.blit_buffer(str_data)
    # time: 0s
    texture.flip_vertical()
    return texture

def play_audio(audio_segment, audio_time):
    return play_buffer(
        audio_segment[audio_time*1000:].raw_data,
        num_channels = audio_segment.channels,
        bytes_per_sample = audio_segment.sample_width,
        sample_rate = audio_segment.frame_rate
        )

def get_content_image_path(project_path, relative_path, size2d=(256,256), color=(0,0,0,0)):
    content_type = check_type(project_path + '/' + relative_path)
    if content_type == 'font':
        return resources_path + '/font.png'
    elif content_type == 'audio':
        return resources_path + '/audio.png'
    elif content_type == 'video':
        cap = cv2.VideoCapture(project_path + '/' + relative_path)
        _, frame = cap.read()
        pil_image = frame2pil_image(frame, alpha=True)
    else:
        pil_image = Image.open(project_path + '/' + relative_path).convert('RGBA')
    img = Image.new('RGBA', size2d, color)
    pil_image.thumbnail(size2d)
    img.paste(pil_image)
    if '/' in relative_path:
        relative_path = '_'.join(relative_path.split('/'))
    if '.' in relative_path:
        relative_path = '_'.join(relative_path.split('.'))
    img.save(temp_dir_path + '/' + relative_path + '.png')
    return temp_dir_path + '/' + relative_path + '.png'