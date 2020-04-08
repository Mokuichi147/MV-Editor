import json
import os
import sys
from time import time as T
from threading import Thread

import cv2
import numpy as np
from PIL import Image
from simpleaudio import play_buffer
from kivy.graphics.texture import Texture


separator = '/'
if sys.platform == 'win32':
    separator = '\\'

dir_path = os.path.abspath(os.path.dirname(__file__))
dir_path = dir_path.split(separator)[:-1]
dir_path = separator.join(dir_path)
resources_path = dir_path + separator + 'resources'


class ProjectData:
    def __init__(self, path):
        self.project_path = path
        self.project_json = self.project_path + '/project.json'
        self.activate()

    def activate(self):
        if os.path.isfile(self.project_json):
            self.activate = True
            return True
        else:
            self.activate = False
            return False

    def update(self):
        self.set_data(self.project_json)
    
    def create(self):
        self.activate = True
        self.set_data(resources_path + '/project.json')
        _data = self.__create_data()
        write_json(self.project_json, _data)
        os.makedirs(self.project_path+'/Font', exist_ok=True)
        os.makedirs(self.project_path+'/Image', exist_ok=True)
        os.makedirs(self.project_path+'/Sound', exist_ok=True)
        os.makedirs(self.project_path+'/Video', exist_ok=True)
    
    def frame_count_data(self, frame_count, dtype='all'):
        _data = []
        for _content in range(self.content):
            if _content['full_time'] and (dtype=='all' or _content['type']==dtype):
                _data.append(_content)
        return _data
        
    def __create_data(self):
        _data = {}
        _data['video'] = self.video
        _data['sound'] = self.sound
        _data['fps'] = self.fps
        _data['maximum_frame'] = self.maximum_frame
        _data['width'] = self.width
        _data['height'] = self.height
        _data['output_fmt'] = self.output_fmt
        _data['content'] = self.__create_list_data(self.content)
        return _data
    
    def __create_list_data(self, list_data):
        _list = []
        for _count, _content in enumerate(list_data):
            _list.append({})
            for _key in _content.keys():
                if type(_content[_key]) is list:
                    _list[_count][_key] = self.__create_list_data(_content[_key])
                else:
                    _list[_count][_key] = _content[_key]
        return _list
    
    def set_data(self, path):
        _data = load_json(path)
        self.video = _data['video']
        self.sound = _data['sound']
        self.fps = _data['fps']
        self.maximum_frame = _data['maximum_frame']
        self.width = _data['width']
        self.height = _data['height']
        self.output_fmt = _data['output_fmt']
        self.content = _data['content']
        self.fonts  = []
        self.images = []
        self.sounds = []
        self.videos = []
        for _content in self.content:
            self.fonts  += [i for i in _content if i['type'] == 'font']
            self.images += [i for i in _content if i['type'] == 'image']
            self.sounds += [i for i in _content if i['type'] == 'sound']
            self.videos += [i for i in _content if i['type'] == 'video']
    
    def __se_frame(self, content):
        _start_frame = content['start_frame']
        _end_frame = _start_frame + content['frame'][1] - content['frame'][0]
        return _start_frame, _end_frame
    
    def check_content_index(self, frame_count):
        _content_index = []
        for i, _content_list in enumerate(self.content):
            for j, _content in enumerate(_content_list):
                _sf, _ef = self.__se_frame(_content['start_frame'])
                if _sf < frame_count < _ef:
                    _content_index.append([i, j])
        return _content_index
    
    def __check_content_block(self, contents, frame=(0,0)):
        for _content in contents:
            _sf, _ef = self.__se_frame(_content['start_frame'])
            if not (_ef < frame[0] or frame[1] < _sf):
                return False
        return True
    
    def content_index(self, data):
        _frame = self.__se_frame(data)
        for i, contents in enumerate(self.content):
            if self.__check_content_block(contents, _frame):
                return i
        return len(self.content)
    
    def add_image(self, path, animation_val=None, start_frame=0, frame=(0,0), size=None, pos=(0,0), angle=0):
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
        num = self.content_index(_data)
        if len(self.content) == num:
            self.content.append([_data])
        else:
            self.content[num].append(_data)


def async_func(function, *args):
    _th = Thread(target=function, args=args)
    _th.daemon = True
    _th.start()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_movie(path):
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

def frame2pil_image(frame):
    # time: 0.001s
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

def play_sound(audio_segment, audio_time):
    return play_buffer(
        audio_segment[audio_time*1000:].raw_data,
        num_channels = audio_segment.channels,
        bytes_per_sample = audio_segment.sample_width,
        sample_rate = audio_segment.frame_rate
        )