import json
import os
import sys
from time import time
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
def frame2texture(frame, size):
    if size[0] > 1920 and size[1] > 1080:
        # time: 0.003~0.004s
        frame = cv2.resize(frame, (1920,1080))
        size = (1920,1080)
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