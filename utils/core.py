import os
import json
from time import time
from threading import Thread

import cv2
import numpy as np
from PIL import Image
from simpleaudio import play_buffer
from kivy.graphics.texture import Texture


class ProjectData:
    def __init__(self):
        self.video = False
        self.sound = False
        self.fps = 0
        self.maximum_frame = 0
        self.width = 0
        self.height = 0
        self.output_fmt = ''
        self.content = []
    
    def create(self, path):
        if os.path.isfile(path + '/project.json'):
            return
        _data = self.__create_data()
        write_json(path + '/project.json', _data)
        
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