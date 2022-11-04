# The Stirling Engine

The Stirling Engine is the processing tool for Keeping History. It provides media conversion and compression, data analysis, metadata enhancement, stream packaging and archival, and is extensible through plugins.

## About

The Stirling Engine is meant to be a lightweight, efficient way to process incoming media files. The engine's main responsibilities are to:

- Normalize uploaded media
- Extract data from the media
- Re-encode the media using modern, stream-ready standards
- Analyze extracted data for additional data enhancements
- Package media and metadata in a standard, open format

### Why is it named The Stirling Engine?

![An example of a Stirling Engine](https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Stirlingmotor_3.jpg/256px-Stirlingmotor_3.jpg)

The (actual) Stirling Engine is a masterpiece of elegant design and ultimate efficiency. A Stirling Engine uses a "regenerator" to exchange heat into energy.

The Stirling Engine incorporates this philosophy, using the "source" file as the "heat" and the outputs it creates as its energy.

[Read more about the Stirling Engine at Wikipedia](https://en.wikipedia.org/wiki/Stirling_engine).

## Getting Started

The Stirling Engine is a command-line tool. It is written in Python 3 and requires Python 3.10 or higher.

### Why Python 3.10?

Python 3.10 introduced the `match` and `case` statements, which are used extensively in the Stirling Engine. The `match` and `case` statements are a powerful way to write code that is more readable and easier to maintain. The Stirling Engine is intended to be deployed in a "locked" environment, where the runtime and dependencies are compiled at build time and do not change. We recommend Docker for this purpose.

### Requirements/Prerequisites

- [Python 3.10 or higher](https://www.python.org/downloads/)
- [`pip`](https://pypi.org/project/pip/) (Python package manager)
- [`ffmpeg`](https://www.ffmpeg.org) (for media processing) and `ffprobe` (for media analysis)

Additionally, to use the built-in plugins, you will need the following:

- `peaks` (audio waveform analysis)
  - [`audiowaveform`](https://github.com/bbc/audiowaveform) (tool for creating waveform data)
- `objects` (object detection) (IN ALPHA, may not work)
  - [`pytorch`](https://pytorch.org) (machine learning framework)
  - [`MTCNN`](https://github.com/ipazc/mtcnn) (face detection)
- `transcript` (speech-to-text) (IN ALPHA, may not work)
  - [`autosub`](https://github.com/agermanidis/autosub) (audio transcription tool)

### Installation

To install the Stirling Engine, you will need to install the prerequisites, clone the repository to your environment and run some setup commands. After that, you can start processing media!

1. Install the prerequisites, and make sure their executable files are available in your `PATH`.
   - Install Python 3.10 or higher (`python3` or `python3.10` depending on your installation method)
   - Install `pip` (could be `pip3` or `pip3.10`)
   - Install `ffmpeg` and `ffprobe`
   - Install `audiowaveform` (if you want to use the `peaks` plugin)
   - Install `autosub` (if you want to use the `transcript` plugin)
2. Clone the repository to your environment
   - `git clone https://github.com/Keeping-History/stirling`
3. Change into the repository directory
   - `cd stirling`
4. Install the Python package dependencies
   - `pip install -r requirements.txt`
5. Grab a source file (or use one of the example files in the `examples` directory)
6. Edit `main.py` and specify your source, as well as any options you'd like to specify for the job or the plugins (more documentation to come).

### Your first conversion

### Testing your conversion

## Next steps

## Goals

The goals of the Stirling Engine are to:

- Store open-source encoded media with long-lived compatibility
- Provide access to a wealth of metadata from media without any client-side processing
- Make multimedia accessible to all by providing additional context
- Relieve the pain of media processing for archivists, historians and teachers
- Make it extensible and a community-led project

## Roadmap

- Encode video to HLS using multi-stream
- Extract audio from video
- Automatically set encoder options based on incoming media
- Create `audiowaveform` data
- Create transcript data - Google
- Allow translations - Google
- Extract thumbnails at internal (for video scrubbing)
- Integrate [tensorflow](http://tensorflow.org):
  - Add object detection
  - Add face detection
  - Add building detection
  - Add known face model
  - Add black/scene cut detection
- Determine an annotation format for , tracked objects
- Automatically mark speakers in transcript
  - Train model on known speakers
- Add Sentiment Analysis
  - Transcript
  - Voice
- Add Natural Language Processing Analysis
  - Known keywords
  - Known personas
  - Known locations
  - Known phrases
  - Repetitions and count analysis

## Contributing

First off, thank you so much for even considering contributing. It is people like you who make the Open Source community a thriving place for exploration. Feel free to fork this repository and create a pull request. There are no pull requests too small.

## Specifications

### Job

A job is specified by a JSON object that each plugin will add it's metadata to the object, in its own key to prevent clashes.

An example JSON job (as of v0.0.2) from a job is below:

```json
{
    "source": "source.mp4",
    "id": "9db89deb-aa09-44e1-a055-c98bc7ecdcff",
    "time_start": "2022-10-23 15:40:37.634918",
    "log_file": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/job.log",
    "job_file": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/job.json",
    "input_directory": "/Users/robbiebyrd/Projects/stirling",
    "source_delete_disable": true,
    "output_directory": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff",
    "output_annotations_directory": "annotations",
    "source_copy_disable": true,
    "media_info": {
        "source": "source.mp4",
        "video_streams": [
            {
                "stream": 1,
                "duration": 1489.120967,
                "codec": "h264",
                "profile": "High",
                "bitrate": "753340",
                "width": 480,
                "height": 360,
                "frame_rate": 29.97002997002997,
                "aspect": [
                    "4",
                    "3"
                ],
                "color_bits": "8",
                "color_model": "yuv420p",
                "scan_type": "progressive",
                "content_type": "video"
            }
        ],
        "audio_streams": [
            {
                "stream": 0,
                "duration": 1489.120958,
                "codec": "aac",
                "profile": "LC",
                "bitrate": "252135",
                "sample_rate": "48000",
                "channels": 2,
                "channel_layout": "stereo",
                "content_type": "audio"
            }
        ],
        "preferred": {
            "video": 1
        }
    },
    "plugins": [
        {
            "name": "audio",
            "depends_on": [],
            "priority": 0,
            "audio_disable": false,
            "audio_source_stream": 0,
            "audio_output_format": [
                "wav",
                "wav"
            ]
        },
        {
            "name": "peaks",
            "depends_on": [
                "audio"
            ],
            "priority": 10,
            "peaks_disable": false,
            "peaks_output_format": "json"
        },
        {
            "name": "video",
            "depends_on": [],
            "priority": 0,
            "video_disable": false,
            "video_source_stream": 1,
            "video_frames_disable": false,
            "frames_interval": 1
        },
        {
            "name": "transcript",
            "depends_on": [
                "audio"
            ],
            "priority": 10,
            "transcript_disable": false,
            "transcript_lang_input": "en",
            "transcript_lang_output": "en",
            "transcript_concurrency": 10,
            "transcript_format": "json"
        },
        {
            "name": "hls",
            "depends_on": [
                "video"
            ],
            "priority": 50,
            "video_source_stream": 1,
            "audio_source_stream": 0,
            "hls_disable": false,
            "hls_profile": "sd",
            "hls_segment_duration": 4,
            "hls_bitrate_ratio": 1.07,
            "hls_buffer_ratio": 1.5,
            "hls_crf": 20,
            "hls_keyframe_multiplier": 1,
            "hls_audio_codec": "aac",
            "hls_audio_sample_rate": 48000,
            "hls_video_codec": "h264",
            "hls_video_profile": "main",
            "hls_sc_threshold": 40,
            "hls_gop_size": 12,
            "hls_keyint_min": 25,
            "hls_target_segment_duration": 2,
            "hls_playlist_type": "vod",
            "hls_movflags": "+faststart",
            "hls_encoder_profiles": [
                {
                    "name": "120p",
                    "width": "160",
                    "height": "120",
                    "bitrate": "128",
                    "audio-bitrate": "32",
                    "ratio": "4:3"
                },
                {
                    "name": "240p",
                    "width": "320",
                    "height": "240",
                    "bitrate": "300",
                    "audio-bitrate": "64",
                    "ratio": "4:3"
                },
                {
                    "name": "480p",
                    "width": "640",
                    "height": "480",
                    "bitrate": "800",
                    "audio-bitrate": "96",
                    "ratio": "4:3"
                }
            ]
        }
    ],
    "commands": [
        {
            "name": "video",
            "command": "ffmpeg -hide_banner -loglevel quiet -y -i source.mp4 -f image2 -map 0:v:1 -vf fps=1 -vsync 0 -frame_pts 1 source.mp4 /Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/video/frames%d.jpg",
            "priority": 0,
            "expected_output": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/video/frames",
            "depends_on": [],
            "status": "FAILED",
            "log": ""
        },
        {
            "name": "audio",
            "command": "ffmpeg -hide_banner -y -loglevel quiet -i source.mp4 -f wav -map 0:a:0 /Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/audio/source.wav",
            "priority": 0,
            "expected_output": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/audio/source.wav",
            "depends_on": [],
            "status": "RUNNING",
            "log": ""
        },
        {
            "name": "hls",
            "command": "ffmpeg -hide_banner -loglevel quiet -y -i source.mp4 -map 0:v:1 -vcodec h264 -profile:v main -crf 20 -sc_threshold 40 -g 12 -keyint_min 25 -hls_time 2 -hls_playlist_type vod -movflags +faststart -map 0:a:0 -acodec aac -ar 48000 -vf scale=w=160:h=120:force_original_aspect_ratio=decrease -b:v 128k -maxrate 136.96k -bufsize 192.0k -b:a 32k -hls_segment_filename \"/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls/120p_%09d.ts' '/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls/120p.m3u8\"-vf scale=w=320:h=240:force_original_aspect_ratio=decrease -b:v 300k -maxrate 321.0k -bufsize 450.0k -b:a 64k -hls_segment_filename \"/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls/240p_%09d.ts' '/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls/240p.m3u8\"-vf scale=w=640:h=480:force_original_aspect_ratio=decrease -b:v 800k -maxrate 856.0k -bufsize 1200.0k -b:a 96k -hls_segment_filename \"/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls/480p_%09d.ts' '/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls/480p.m3u8\"",
            "priority": 50,
            "expected_output": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/hls",
            "depends_on": [
                "video"
            ],
            "status": "FAILED",
            "log": ""
        },
        {
            "name": "transcript",
            "command": "autosub -o /Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/annotations/transcript.json -D en -S en -C 10 -F json source.mp4",
            "priority": 10,
            "expected_output": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/annotations/transcript.json",
            "depends_on": [
                "audio"
            ],
            "status": "QUEUED",
            "log": null
        },
        {
            "name": "peaks",
            "command": "audiowaveform -i source.mp4 -o /Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/annotations/peaks.json --output-format json",
            "priority": 10,
            "expected_output": "/Users/robbiebyrd/Projects/stirling/output/9db89deb-aa09-44e1-a055-c98bc7ecdcff/annotations/peaks.json",
            "depends_on": [
                "audio"
            ],
            "status": "QUEUED",
            "log": null
        }
    ]
}
```
