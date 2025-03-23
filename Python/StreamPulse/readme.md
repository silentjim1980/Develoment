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