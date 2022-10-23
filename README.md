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

[Read more about the Sterling Engine at Wikipedia](https://en.wikipedia.org/wiki/Stirling_engine).

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

An example JSON job from a completed job is below:

```json
TODO: This is not finalized for this release yet, please put a sample JSON job file here!
```
