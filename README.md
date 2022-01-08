# MV-Editor

Software for video editing.  
<br>


## Requirement

* [FFmpeg](https://ffmpeg.org/)  
<br>


## Installation

```
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade poetry
poetry install
```
<details>
<summary>When an error occurs on Linux</summary>

```
sudo apt install git gcc make zlib1g-dev libffi-dev libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev python3-tk python3-distutils python3-pip ffmpeg
```
</details>
<details>
<summary>When an error occurs on Windows</summary>

- If you get an error when installing simpleaudio
    1. Install or update [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/ja/visual-cpp-build-tools/)
    1. Reboot the computer
</details>
<br>


## Usage

Linux or MacOS    
```
mkdir TestProject
poetry run python main.py
```

Windows 10 or 11
```
mkdir TestProject
poetry run python.exe main.py
```
<br>


## Build

```
poetry run pyinstaller main.spec
```
<br>


## Note

- [x] Play the video
- [ ] Edit the video  
<br>


## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.  
<br>


### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.


### Redistribution

<details>
<summary>NotoSansJP</summary>

[SIL OPEN FONT LICENSE Version 1.1](resources/fonts/OFL.txt)
```
├── resources  
│   ├── fonts  
│   │   ├── NotoSansJP-Medium.otf  
│   │   └── OFL.txt
```
</details>