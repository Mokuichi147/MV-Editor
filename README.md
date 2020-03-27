# MV-Editor

Windows10のPCで動画編集をするためのソフト  
MacOSでの動作も確認済み


## Requirement

事前にインストールしておく必要のあるもの

* FFmpeg (mp4等を読み込む場合)

必要なライブラリ

* numpy
* pydub
* simpleaudio
* kivy
* opencv-python
* pillow


## Installation

FFmpegは[公式ページ](https://ffmpeg.org/)から

Python 3.6 以上推奨

```bash
pip install numpy
pip install pydub
pip install simpleaudio
pip install kivy
pip install opencv-python
pip install pillow
```


## Usage

```bash
git clone https://github.com/Mokuichi147/MV-Editor.git
cd MV-Editor
mkdir TestProject
# TestProjectに動画等を移す
python main.py
```


## Note

まだ動画の再生しか出来ない