This project was something I've really wanted to do for some time.
I run a Blue Iris machine for security cameras & have long wanted a way to add outside
sources as a camera source for Blue Iris.

What is Blue Iris?
It's Video security & Webcam software.
Find out more here: https://blueirissoftware.com/
If you are looking into security camera software for your home or business [not sponsored]

Blue Iris supports different streaming protocols i.e. rtsp, rtmp, onvif, & more.
However it doesn't [to the best of my knowledge] currently support adding other stream formats i.e. m3u8
HLS? I'm not sure. It also doesn't allow for say capturing source & streaming it.

I have my own personal reasons for wanting these features. I wanted a way to capture a window
on my desktop & stream it to Blue Iris. I also wanted a way to add non-supported (possibly) stream(ing) protocols. That meant I had to turn streams into the correct protocol, rtsp:// for Blue Iris to see them.

Enter AI & a bit of searching. I came across MediaMTX & yt-dlp.

What is MediaMTX? (formerly known as rtsp-simple-server)

MediaMTX is a ready-to-use and zero-dependency real-time media server and media proxy that allows to publish, read, proxy, record and playback video and audio streams. It has been conceived as a "media router" that routes media streams from one end to the other.
Found here: https://github.com/bluenviron/mediamtx

What is yt-dlp?

yt-dlp is a feature-rich command-line audio/video downloader with support for thousands of sites. The project is a fork of youtube-dl based on the now inactive youtube-dlc.
Found here: https://github.com/yt-dlp/yt-dlp

The setup process is fairly easy, the configuration was a bit involved due to what I wanted to accomplish.
Using MediaMTX & yt-dlp I can take live streams from a variety of different sources (only YouTube so far) & pipe/convert them into a protocol that I can add as a camera source to Blue Iris.

I'm sure there are other ways to do this, this probably isn't the "correct" or right way. This is just
the way I did it.

# streampulse - Stream Manager

**streampulse** is a Python application designed to capture window content or stream YouTube videos and output them via RTSP using FFmpeg and MediaMTX. It features a user-friendly PyQt5 GUI for managing streams, supporting window captures and YouTube streams with configurable resolutions and frame rates.

## Features
- Capture and stream specific windows or YouTube videos.
- Start, stop, add, and remove streams via a graphical interface.
- Edit stream sources (window names or URLs) directly in the table.
- Lock capture positions for window streams.
- Configurable width, height, and FPS settings.
- Real-time status monitoring with color-coded indicators.
- Comprehensive logging with file rotation.

## Prerequisites
- **Operating System**: Windows (due to use of `pygetwindow`, `win32gui`, and `.exe` executables).
- **Python**: Version 3.8 or higher.

## Installation

Follow these steps to set up **streampulse** on your system:

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/[YourUsername]/streampulse.git
cd streampulse

2. Create Project Directory Structure
Create a directory for the project and set up the following subdirectories:

streampulse/
├── ffmpeg/
│   └── ffmpeg.exe
├── yt-dlp/
│   └── yt-dlp.exe
├── mediamtx/
│   └── mediamtx.exe
├── logs/
└── streampulse.py

Replace [Directory Here] in streampulse.py with the absolute path to your streampulse/ directory (e.g., C:/Users/YourName/streampulse).

3. Install Dependencies
Install the required Python packages using pip. It’s recommended to use a virtual environment:
bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install PyQt5 psutil pygetwindow pywin32 screeninfo dxcam opencv-python numpy

4. Download External Tools
Download the following tools and place them in their respective directories:
FFmpeg: 
Download from FFmpeg Official Website (Windows builds).

Extract ffmpeg.exe and place it in streampulse/ffmpeg/.

yt-dlp: 
Download from yt-dlp GitHub Releases.

Place yt-dlp.exe in streampulse/yt-dlp/.

MediaMTX: 
Download from MediaMTX GitHub Releases.

Place mediamtx.exe in streampulse/mediamtx/.

5. Configure YouTube Streams
Edit streampulse.py to replace [URL Here] placeholders in the STREAMS dictionary with valid YouTube URLs if you plan to use YouTube streaming:
python

"Stream0": {
    "type": "youtube",
    "url": "https://www.youtube.com/watch?v=your_video_id",
    ...
},
"fallback": {
    "type": "youtube",
    "url": "https://www.youtube.com/watch?v=another_video_id",
    ...
}

6. Run MediaMTX
Start MediaMTX before running the application, as it acts as the RTSP server:
bash

cd mediamtx
mediamtx.exe

Ensure it runs with administrative privileges if necessary.

By default, it listens on localhost:8555 (matching RTSP_SERVER in the script).

7. Run streampulse
Launch the application:
bash

python streampulse.py

The GUI will appear, allowing you to manage streams.

Usage
Start MediaMTX: Ensure mediamtx.exe is running.

Launch streampulse: Run python streampulse.py.

Add Streams:
Enter a window name (e.g., "Notepad") or YouTube URL in the "Source" field.

Optionally set width, height, FPS, and lock position.

Click "Add Stream".

Manage Streams:
Use "Start/Stop" buttons to control streams.

Double-click the "Source" column to edit.

Use "Remove" to delete non-protected streams.

Check "Lock Position" for window streams to fix the capture region.

View Streams: Access streams at rtsp://localhost:8555/stream_key (e.g., rtsp://localhost:8555/radar) using a media player like VLC.

Troubleshooting
"MediaMTX not running": Start mediamtx.exe manually or check for port conflicts.

Window not found: Ensure the window title matches exactly (case-insensitive).

YouTube stream fails: Verify the URL and ensure yt-dlp.exe is updated.

Logs: Check the logs/ directory for detailed error messages.

Contributing
Feel free to submit issues or pull requests on GitHub. For major changes, please open an issue first to discuss your ideas.
License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments
Built with PyQt5, FFmpeg, yt-dlp, and MediaMTX.

Thanks to the open-source community for these amazing tools!

### Notes
- Replace `[YourUsername]` in the GitHub URL with your actual GitHub username.
- Ensure users adjust paths in the script to match their setup.
- The guide assumes a Windows environment due to the script’s dependencies and executable extensions.
- Add a `LICENSE` file to the repository if you choose to include one (e.g., MIT License).

