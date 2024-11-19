# MP4 Compress FTP

## Requirements

- [Python 3.8.x](https://www.python.org/downloads/release/python-3815/)
- [FFmpeg](https://ffmpeg.org/download.html)

## Installation

Install `ffmpeg-python`.

```sh
pip install ffmpeg-python
```

Change the FTP configuration in `main.py`

```py
# FTP config.
HOSTNAME = 'hostname'
USERNAME = 'username'
PASSWORD = 'password'
```

Create 2 directories named `input` and `output`. Put your MP4 files inside `input` directory.

Run.

```sh
python main.py
```
