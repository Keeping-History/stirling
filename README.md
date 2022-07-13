# The Stirling Engine
The Stirling Engine is the processing tool for Keeping History. It provides media conversion and compression, data analysis, metadata enhancement, stream packaging and archival, and is extensible through plugins.

## About
The Stirling Engine is meant to be a lightweight, efficient way to process incoming media files. The engine's main responsibilties are to:
- Normalize uploaded media
- Extract data from the media
- Re-encode the media using modern, stream-ready standards
- Analyze extracted data for additional data enhancements
- Package media and metadata in a standard, open format

## Getting Started

### Requirements/Prerequisites

### Installation

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
- Create audiowaveform data
- Create transcript data - Google
- Alllow translations - Google
- Extract thumnails at internval (for video scrubbing)
- Integrate (http://imageai.readthedocs.io)[imageai] library
  - Add object detection
  - Add face detection
  - Add building detection
  - Add known face model
- Automatically mark speakers in transcript
   - Train model on known speakers
- Add Sentitment Analysis
  - Transcript
  - Voice
- Add Natural Language Processing Analysis
  - Known keywords
  - Known personas
  - Known locations
  - Known phrases
  - Repetitions and count analysis

## Contributing
First off, thank you so much for even considering contributing. It is people like you who make the Open Source communuity a thriving place for exploration. Feel free to fork this repository and create a pull request. There are no pull requests too small.

## Specifications
### Job
A job is specified by a JSON object that can be passed from service to service. Each service will add it's metadata to the object, in its own key to prevent clashes.

An example JSON job from a completed job is below:
```json
{
  "info" : {
    "id" : "bdfabf92-dd1c-4859-935b-9a004141d88f",
    "time_start" : "2022-07-11 21:02:02.796361",
    "time_end" : "2022-07-11 21:02:52.337067",
    "duration" : 49.540706,
    "log_file" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/job.log",
    "job_file" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/job.json",
    "arguments" : {
      "source" : "source.mp4",
      "output" : null,
      "input_directory" : "",
      "output_directory_prefix" : "output",
      "disable_delete_source" : true,
      "disable_source_copy" : false,
      "disable_audio" : false,
      "disable_transcript" : false,
      "disable_peaks" : false,
      "disable_hls" : false,
      "hls_profile" : "sd",
      "input_video_stream" : -1,
      "input_audio_stream" : -1,
      "hls_segment_duration" : 4,
      "hls_bitrate_ratio" : 1.07,
      "hls_buffer_ratio" : 1.5,
      "hls_crf" : 20,
      "hls_keyframe_multiplier" : 1,
      "simulate" : false,
      "debug" : true
    }
  },
  "output" : {
    "directory" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f",
    "outputs" : [
      "output/bdfabf92-dd1c-4859-935b-9a004141d88f/peaks.json",
      "output/bdfabf92-dd1c-4859-935b-9a004141d88f/subtitles.json",
      "output/bdfabf92-dd1c-4859-935b-9a004141d88f"
    ],
    "audio_extract" : "Splitting the commandline.\nReading option '-hide_banner' ... matched as option 'hide_banner' (do not show program banner) with argument '1'.\nReading option '-y' ... matched as option 'y' (overwrite output files) with argument '1'.\nReading option '-loglevel' ... matched as option 'loglevel' (set logging level) with argument 'debug'.\nReading option '-i' ... matched as input url with argument 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4'.\nReading option '-ac' ... matched as option 'ac' (set number of audio channels) with argument '1'.\nReading option '-acodec' ... matched as option 'acodec' (force audio codec ('copy' to copy stream)) with argument 'pcm_s16le'.\nReading option '-ar' ... matched as option 'ar' (set audio sampling rate (in Hz)) with argument '44800'.\nReading option '-map' ... matched as option 'map' (set input stream mapping) with argument '0:a:0'.\nReading option 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav' ... matched as output url.\nFinished splitting the commandline.\nParsing a group of options: global .\nApplying option hide_banner (do not show program banner) with argument 1.\nApplying option y (overwrite output files) with argument 1.\nApplying option loglevel (set logging level) with argument debug.\nSuccessfully parsed a group of options.\nParsing a group of options: input url output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4.\nSuccessfully parsed a group of options.\nOpening an input file: output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4.\n[NULL @ 0x12d7041e0] Opening 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4' for reading\n[file @ 0x12d704670] Setting default whitelist 'file,crypto,data'\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] Format mov,mp4,m4a,3gp,3g2,mj2 probed with size=2048 and score=100\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] ISO: File Type Major Brand: mp42\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] Unknown dref type 0x206c7275 size 12\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] Processing st: 0, edit list 0 - media time: 0, duration: 71477806\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] Unknown dref type 0x206c7275 size 12\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] Processing st: 1, edit list 0 - media time: 0, duration: 44673629\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] Before avformat_find_stream_info() pos: 625824 bytes read:621563 seeks:1 nb_streams:2\n[h264 @ 0x10d605290] nal_unit_type: 7(SPS), nal_ref_idc: 1\n[h264 @ 0x10d605290] nal_unit_type: 8(PPS), nal_ref_idc: 1\n[h264 @ 0x10d605290] nal_unit_type: 7(SPS), nal_ref_idc: 1\n[h264 @ 0x10d605290] nal_unit_type: 8(PPS), nal_ref_idc: 1\n[h264 @ 0x10d605290] nal_unit_type: 6(SEI), nal_ref_idc: 0\n    Last message repeated 1 times\n[h264 @ 0x10d605290] nal_unit_type: 5(IDR), nal_ref_idc: 1\n    Last message repeated 4 times\n[h264 @ 0x10d605290] Format yuv420p chosen by get_format().\n[h264 @ 0x10d605290] Reinit context to 480x368, pix_fmt: yuv420p\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] All info found\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x12d7041e0] After avformat_find_stream_info() pos: 703947 bytes read:654331 seeks:2 frames:48\nInput #0, mov,mp4,m4a,3gp,3g2,mj2, from 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4':\n  Metadata:\n    major_brand     : mp42\n    minor_version   : 1\n    compatible_brands: mp41mp42isom\n    creation_time   : 2017-10-09T19:23:41.000000Z\n  Duration: 00:24:49.12, start: 0.000000, bitrate: 1008 kb/s\n  Stream #0:0[0x1](eng), 47, 1/48000: Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp, 252 kb/s (default)\n    Metadata:\n      creation_time   : 2017-10-09T19:23:41.000000Z\n      handler_name    : Core Media Audio\n      vendor_id       : [0][0][0][0]\n  Stream #0:1[0x2](und), 1, 1/30000: Video: h264 (High), 1 reference frame (avc1 / 0x31637661), yuv420p(tv, smpte170m/smpte170m/bt709, progressive, left), 480x360 (480x368) [SAR 1:1 DAR 4:3], 0/1, 753 kb/s, 29.97 fps, 29.97 tbr, 30k tbn (default)\n    Metadata:\n      creation_time   : 2017-10-09T19:23:41.000000Z\n      handler_name    : Core Media Video\n      vendor_id       : [0][0][0][0]\nSuccessfully opened the file.\nParsing a group of options: output url output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav.\nApplying option ac (set number of audio channels) with argument 1.\nApplying option acodec (force audio codec ('copy' to copy stream)) with argument pcm_s16le.\nApplying option ar (set audio sampling rate (in Hz)) with argument 44800.\nApplying option map (set input stream mapping) with argument 0:a:0.\nSuccessfully parsed a group of options.\nOpening an output file: output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav.\n[file @ 0x10511a8f0] Setting default whitelist 'file,crypto,data'\nSuccessfully opened the file.\nStream mapping:\n  Stream #0:0 -> #0:0 (aac (native) -> pcm_s16le (native))\nPress [q] to stop, [?] for help\ncur_dts is invalid st:0 (0) [init:0 i_done:0 finish:0] (this is harmless if it occurs once at the start per stream)\ndetected 10 logical cores\n[graph_0_in_0_0 @ 0x11d604360] Setting 'time_base' to value '1/48000'\n[graph_0_in_0_0 @ 0x11d604360] Setting 'sample_rate' to value '48000'\n[graph_0_in_0_0 @ 0x11d604360] Setting 'sample_fmt' to value 'fltp'\n[graph_0_in_0_0 @ 0x11d604360] Setting 'channel_layout' to value '0x3'\n[graph_0_in_0_0 @ 0x11d604360] tb:1/48000 samplefmt:fltp samplerate:48000 chlayout:0x3\n[format_out_0_0 @ 0x105404380] Setting 'sample_fmts' to value 's16'\n[format_out_0_0 @ 0x105404380] Setting 'sample_rates' to value '44800'\n[format_out_0_0 @ 0x105404380] Setting 'channel_layouts' to value '0x4'\n[format_out_0_0 @ 0x105404380] auto-inserting filter 'auto_aresample_0' between the filter 'Parsed_anull_0' and the filter 'format_out_0_0'\n[AVFilterGraph @ 0x12d6390d0] query_formats: 4 queried, 6 merged, 3 already done, 0 delayed\n[auto_aresample_0 @ 0x105404b50] [SWR @ 0x148008000] Using fltp internally between filters\n[auto_aresample_0 @ 0x105404b50] [SWR @ 0x148008000] Matrix coefficients:\n[auto_aresample_0 @ 0x105404b50] [SWR @ 0x148008000] FC: FL:0.500000 FR:0.500000 \n[auto_aresample_0 @ 0x105404b50] ch:2 chl:stereo fmt:fltp r:48000Hz -> ch:1 chl:mono fmt:s16 r:44800Hz\nOutput #0, wav, to 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav':\n  Metadata:\n    major_brand     : mp42\n    minor_version   : 1\n    compatible_brands: mp41mp42isom\n    ISFT            : Lavf59.16.100\n  Stream #0:0(eng), 0, 1/44800: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44800 Hz, mono, s16, 716 kb/s (default)\n    Metadata:\n      creation_time   : 2017-10-09T19:23:41.000000Z\n      handler_name    : Core Media Audio\n      vendor_id       : [0][0][0][0]\n      encoder         : Lavc59.18.100 pcm_s16le\nsize=       2kB time=00:00:00.02 bitrate= 746.6kbits/s speed=2.1e+04x    \nsize=   29952kB time=00:05:43.78 bitrate= 713.7kbits/s speed= 688x    \nsize=   59136kB time=00:11:17.71 bitrate= 714.8kbits/s speed= 678x    \nsize=   89088kB time=00:16:59.09 bitrate= 716.1kbits/s speed= 679x    \nsize=  118784kB time=00:22:39.44 bitrate= 715.8kbits/s speed= 680x    \n[out_0_0 @ 0x105404200] EOF on sink link out_0_0:default.\nNo more output streams to write to, finishing.\nsize=  130299kB time=00:24:49.13 bitrate= 716.8kbits/s speed= 682x    \nvideo:0kB audio:130299kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 0.000058%\nInput file #0 (output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4):\n  Input stream #0:0 (audio): 69803 packets read (46934088 bytes); 69803 frames decoded (71478272 samples); \n  Input stream #0:1 (video): 1 packets read (448 bytes); \n  Total: 69804 packets (46934536 bytes) demuxed\nOutput file #0 (output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav):\n  Output stream #0:0 (audio): 69804 frames encoded (66713053 samples); 69804 packets muxed (133426106 bytes); \n  Total: 69804 packets (133426106 bytes) muxed\n[AVIOContext @ 0x105106e30] Statistics: 133426192 bytes written, 4 seeks, 511 writeouts\n69803 frames successfully decoded, 0 decoding errors\n[AVIOContext @ 0x12d7047f0] Statistics: 138116091 bytes read, 1064 seeks",
    "audio_peak_generation" : "Input file: output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav\nFrames: 66713053\nSample rate: 44800 Hz\nChannels: 1\nFormat: 0x10002\nSections: 1\nSeekable: yes\nGenerating waveform data...\nSamples per pixel: 256\nInput channels: 1\nOutput channels: 1\n\nDone: 0%\nDone: 1%\nDone: 2%\nDone: 3%\nDone: 4%\nDone: 5%\nDone: 6%\nDone: 7%\nDone: 8%\nDone: 9%\nDone: 10%\nDone: 11%\nDone: 12%\nDone: 13%\nDone: 14%\nDone: 15%\nDone: 16%\nDone: 17%\nDone: 18%\nDone: 19%\nDone: 20%\nDone: 21%\nDone: 22%\nDone: 23%\nDone: 24%\nDone: 25%\nDone: 26%\nDone: 27%\nDone: 28%\nDone: 29%\nDone: 30%\nDone: 31%\nDone: 32%\nDone: 33%\nDone: 34%\nDone: 35%\nDone: 36%\nDone: 37%\nDone: 38%\nDone: 39%\nDone: 40%\nDone: 41%\nDone: 42%\nDone: 43%\nDone: 44%\nDone: 45%\nDone: 46%\nDone: 47%\nDone: 48%\nDone: 49%\nDone: 50%\nDone: 51%\nDone: 52%\nDone: 53%\nDone: 54%\nDone: 55%\nDone: 56%\nDone: 57%\nDone: 58%\nDone: 59%\nDone: 60%\nDone: 61%\nDone: 62%\nDone: 63%\nDone: 64%\nDone: 65%\nDone: 66%\nDone: 67%\nDone: 68%\nDone: 69%\nDone: 70%\nDone: 71%\nDone: 72%\nDone: 73%\nDone: 74%\nDone: 75%\nDone: 76%\nDone: 77%\nDone: 78%\nDone: 79%\nDone: 80%\nDone: 81%\nDone: 82%\nDone: 83%\nDone: 84%\nDone: 85%\nDone: 86%\nDone: 87%\nDone: 88%\nDone: 89%\nDone: 90%\nDone: 91%\nDone: 92%\nDone: 93%\nDone: 94%\nDone: 95%\nDone: 96%\nDone: 97%\nDone: 98%\nDone: 99%\nDone: 100%\nRead 66713053 frames\nGenerated 260598 points\nOutput file: output/bdfabf92-dd1c-4859-935b-9a004141d88f/peaks.json\nDone",
    "transcript_generation" : "Converting speech regions to FLAC files:   0% |                | ETA:  --:--:--\nConverting speech regions to FLAC files:   0% |                | ETA:  --:--:--\nConverting speech regions to FLAC files:   1% |                | ETA:   0:00:16\nConverting speech regions to FLAC files:   3% |                | ETA:   0:00:07\nConverting speech regions to FLAC files:   6% |#               | ETA:   0:00:05\nConverting speech regions to FLAC files:   8% |#               | ETA:   0:00:05\nConverting speech regions to FLAC files:  11% |#               | ETA:   0:00:04\nConverting speech regions to FLAC files:  14% |##              | ETA:   0:00:03\nConverting speech regions to FLAC files:  16% |##              | ETA:   0:00:03\nConverting speech regions to FLAC files:  19% |###             | ETA:   0:00:03\nConverting speech regions to FLAC files:  21% |###             | ETA:   0:00:02\nConverting speech regions to FLAC files:  24% |###             | ETA:   0:00:02\nConverting speech regions to FLAC files:  27% |####            | ETA:   0:00:02\nConverting speech regions to FLAC files:  30% |####            | ETA:   0:00:02\nConverting speech regions to FLAC files:  32% |#####           | ETA:   0:00:02\nConverting speech regions to FLAC files:  35% |#####           | ETA:   0:00:02\nConverting speech regions to FLAC files:  38% |######          | ETA:   0:00:02\nConverting speech regions to FLAC files:  40% |######          | ETA:   0:00:01\nConverting speech regions to FLAC files:  43% |######          | ETA:   0:00:01\nConverting speech regions to FLAC files:  45% |#######         | ETA:   0:00:01\nConverting speech regions to FLAC files:  48% |#######         | ETA:   0:00:01\nConverting speech regions to FLAC files:  50% |########        | ETA:   0:00:01\nConverting speech regions to FLAC files:  53% |########        | ETA:   0:00:01\nConverting speech regions to FLAC files:  55% |########        | ETA:   0:00:01\nConverting speech regions to FLAC files:  58% |#########       | ETA:   0:00:01\nConverting speech regions to FLAC files:  60% |#########       | ETA:   0:00:01\nConverting speech regions to FLAC files:  63% |##########      | ETA:   0:00:01\nConverting speech regions to FLAC files:  65% |##########      | ETA:   0:00:01\nConverting speech regions to FLAC files:  68% |##########      | ETA:   0:00:00\nConverting speech regions to FLAC files:  70% |###########     | ETA:   0:00:00\nConverting speech regions to FLAC files:  73% |###########     | ETA:   0:00:00\nConverting speech regions to FLAC files:  74% |###########     | ETA:   0:00:00\nConverting speech regions to FLAC files:  78% |############    | ETA:   0:00:00\nConverting speech regions to FLAC files:  81% |############    | ETA:   0:00:00\nConverting speech regions to FLAC files:  83% |#############   | ETA:   0:00:00\nConverting speech regions to FLAC files:  86% |#############   | ETA:   0:00:00\nConverting speech regions to FLAC files:  88% |##############  | ETA:   0:00:00\nConverting speech regions to FLAC files:  91% |##############  | ETA:   0:00:00\nConverting speech regions to FLAC files:  92% |##############  | ETA:   0:00:00\nConverting speech regions to FLAC files:  96% |############### | ETA:   0:00:00\nConverting speech regions to FLAC files:  98% |############### | ETA:   0:00:00\nConverting speech regions to FLAC files: 100% |################| Time:  0:00:02\nPerforming speech recognition:   0% |                          | ETA:  --:--:--\nPerforming speech recognition:   0% |                          | ETA:  --:--:--\nPerforming speech recognition:   0% |                          | ETA:   0:02:45\nPerforming speech recognition:   2% |                          | ETA:   0:00:50\nPerforming speech recognition:   3% |                          | ETA:   0:00:36\nPerforming speech recognition:   3% |                          | ETA:   0:01:04\nPerforming speech recognition:   5% |#                         | ETA:   0:00:43\nPerforming speech recognition:   7% |#                         | ETA:   0:00:45\nPerforming speech recognition:   8% |##                        | ETA:   0:00:37\nPerforming speech recognition:   9% |##                        | ETA:   0:00:38\nPerforming speech recognition:  10% |##                        | ETA:   0:00:34\nPerforming speech recognition:  10% |##                        | ETA:   0:00:38\nPerforming speech recognition:  11% |###                       | ETA:   0:00:38\nPerforming speech recognition:  13% |###                       | ETA:   0:00:34\nPerforming speech recognition:  15% |###                       | ETA:   0:00:31\nPerforming speech recognition:  16% |####                      | ETA:   0:00:30\nPerforming speech recognition:  16% |####                      | ETA:   0:00:31\nPerforming speech recognition:  18% |####                      | ETA:   0:00:30\nPerforming speech recognition:  18% |####                      | ETA:   0:00:30\nPerforming speech recognition:  20% |#####                     | ETA:   0:00:28\nPerforming speech recognition:  20% |#####                     | ETA:   0:00:28\nPerforming speech recognition:  21% |#####                     | ETA:   0:00:29\nPerforming speech recognition:  22% |#####                     | ETA:   0:00:27\nPerforming speech recognition:  23% |######                    | ETA:   0:00:27\nPerforming speech recognition:  24% |######                    | ETA:   0:00:26\nPerforming speech recognition:  25% |######                    | ETA:   0:00:27\nPerforming speech recognition:  25% |######                    | ETA:   0:00:28\nPerforming speech recognition:  28% |#######                   | ETA:   0:00:24\nPerforming speech recognition:  29% |#######                   | ETA:   0:00:26\nPerforming speech recognition:  30% |#######                   | ETA:   0:00:25\nPerforming speech recognition:  31% |########                  | ETA:   0:00:24\nPerforming speech recognition:  32% |########                  | ETA:   0:00:23\nPerforming speech recognition:  32% |########                  | ETA:   0:00:24\nPerforming speech recognition:  34% |########                  | ETA:   0:00:24\nPerforming speech recognition:  34% |#########                 | ETA:   0:00:24\nPerforming speech recognition:  36% |#########                 | ETA:   0:00:22\nPerforming speech recognition:  36% |#########                 | ETA:   0:00:23\nPerforming speech recognition:  36% |#########                 | ETA:   0:00:23\nPerforming speech recognition:  37% |#########                 | ETA:   0:00:22\nPerforming speech recognition:  38% |#########                 | ETA:   0:00:22\nPerforming speech recognition:  38% |##########                | ETA:   0:00:22\nPerforming speech recognition:  40% |##########                | ETA:   0:00:21\nPerforming speech recognition:  40% |##########                | ETA:   0:00:21\nPerforming speech recognition:  40% |##########                | ETA:   0:00:22\nPerforming speech recognition:  43% |###########               | ETA:   0:00:20\nPerforming speech recognition:  44% |###########               | ETA:   0:00:20\nPerforming speech recognition:  46% |############              | ETA:   0:00:19\nPerforming speech recognition:  47% |############              | ETA:   0:00:19\nPerforming speech recognition:  48% |############              | ETA:   0:00:20\nPerforming speech recognition:  50% |#############             | ETA:   0:00:19\nPerforming speech recognition:  50% |#############             | ETA:   0:00:19\nPerforming speech recognition:  52% |#############             | ETA:   0:00:18\nPerforming speech recognition:  52% |#############             | ETA:   0:00:18\nPerforming speech recognition:  52% |#############             | ETA:   0:00:18\nPerforming speech recognition:  53% |#############             | ETA:   0:00:18\nPerforming speech recognition:  55% |##############            | ETA:   0:00:17\nPerforming speech recognition:  55% |##############            | ETA:   0:00:17\nPerforming speech recognition:  56% |##############            | ETA:   0:00:18\nPerforming speech recognition:  60% |###############           | ETA:   0:00:15\nPerforming speech recognition:  61% |################          | ETA:   0:00:15\nPerforming speech recognition:  62% |################          | ETA:   0:00:14\nPerforming speech recognition:  63% |################          | ETA:   0:00:15\nPerforming speech recognition:  66% |#################         | ETA:   0:00:13\nPerforming speech recognition:  66% |#################         | ETA:   0:00:13\nPerforming speech recognition:  66% |#################         | ETA:   0:00:14\nPerforming speech recognition:  70% |##################        | ETA:   0:00:11\nPerforming speech recognition:  70% |##################        | ETA:   0:00:11\nPerforming speech recognition:  71% |##################        | ETA:   0:00:11\nPerforming speech recognition:  72% |##################        | ETA:   0:00:10\nPerforming speech recognition:  73% |###################       | ETA:   0:00:10\nPerforming speech recognition:  74% |###################       | ETA:   0:00:10\nPerforming speech recognition:  75% |###################       | ETA:   0:00:10\nPerforming speech recognition:  77% |####################      | ETA:   0:00:09\nPerforming speech recognition:  78% |####################      | ETA:   0:00:08\nPerforming speech recognition:  78% |####################      | ETA:   0:00:08\nPerforming speech recognition:  79% |####################      | ETA:   0:00:08\nPerforming speech recognition:  80% |####################      | ETA:   0:00:08\nPerforming speech recognition:  82% |#####################     | ETA:   0:00:07\nPerforming speech recognition:  86% |######################    | ETA:   0:00:05\nPerforming speech recognition:  86% |######################    | ETA:   0:00:05\nPerforming speech recognition:  87% |######################    | ETA:   0:00:05\nPerforming speech recognition:  88% |#######################   | ETA:   0:00:04\nPerforming speech recognition:  91% |#######################   | ETA:   0:00:03\nPerforming speech recognition:  91% |#######################   | ETA:   0:00:03\nPerforming speech recognition:  92% |########################  | ETA:   0:00:03\nPerforming speech recognition:  93% |########################  | ETA:   0:00:02\nPerforming speech recognition:  95% |########################  | ETA:   0:00:01\nPerforming speech recognition:  96% |########################  | ETA:   0:00:01\nPerforming speech recognition:  96% |######################### | ETA:   0:00:01\nPerforming speech recognition: 100% |##########################| Time:  0:00:43\nSubtitles file created at output/bdfabf92-dd1c-4859-935b-9a004141d88f/subtitles.json",
    "video_hls_generation" : "Splitting the commandline.\nReading option '-hide_banner' ... matched as option 'hide_banner' (do not show program banner) with argument '1'.\nReading option '-y' ... matched as option 'y' (overwrite output files) with argument '1'.\nReading option '-loglevel' ... matched as option 'loglevel' (set logging level) with argument 'debug'.\nReading option '-i' ... matched as input url with argument 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4'.\nReading option '-map' ... matched as option 'map' (set input stream mapping) with argument '0:v:1'.\nReading option '-acodec' ... matched as option 'acodec' (force audio codec ('copy' to copy stream)) with argument 'aac'.\nReading option '-ar' ... matched as option 'ar' (set audio sampling rate (in Hz)) with argument '44100'.\nReading option '-vcodec' ... matched as option 'vcodec' (force video codec ('copy' to copy stream)) with argument 'h264'.\nReading option '-profile:v' ... matched as option 'profile' (set profile) with argument 'main'.\nReading option '-crf' ... matched as AVOption 'crf' with argument '20'.\nReading option '-sc_threshold' ... matched as AVOption 'sc_threshold' with argument '40'.\nReading option '-g' ... matched as AVOption 'g' with argument '60'.\nReading option '-keyint_min' ... matched as AVOption 'keyint_min' with argument '60'.\nReading option '-hls_time' ... matched as AVOption 'hls_time' with argument '2'.\nReading option '-hls_playlist_type' ... matched as AVOption 'hls_playlist_type' with argument 'vod'.\nReading option '-movflags' ... matched as AVOption 'movflags' with argument '+faststart'.\nReading option '-vf' ... matched as option 'vf' (set video filters) with argument 'scale=w=160:h=120:force_original_aspect_ratio=decrease'.\nReading option '-b:v' ... matched as option 'b' (video bitrate (please use -b:v)) with argument '128k'.\nReading option '-maxrate' ... matched as AVOption 'maxrate' with argument '128k'.\nReading option '-bufsize' ... matched as AVOption 'bufsize' with argument '128k'.\nReading option '-b:a' ... matched as option 'b' (video bitrate (please use -b:v)) with argument '32k'.\nReading option '-hls_segment_filename' ... matched as AVOption 'hls_segment_filename' with argument 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/120p_%09d.ts'.\nReading option 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/120p.m3u8' ... matched as output url.\nReading option '-acodec' ... matched as option 'acodec' (force audio codec ('copy' to copy stream)) with argument 'aac'.\nReading option '-ar' ... matched as option 'ar' (set audio sampling rate (in Hz)) with argument '44100'.\nReading option '-vcodec' ... matched as option 'vcodec' (force video codec ('copy' to copy stream)) with argument 'h264'.\nReading option '-profile:v' ... matched as option 'profile' (set profile) with argument 'main'.\nReading option '-crf' ... matched as AVOption 'crf' with argument '20'.\nReading option '-sc_threshold' ... matched as AVOption 'sc_threshold' with argument '40'.\nReading option '-g' ... matched as AVOption 'g' with argument '60'.\nReading option '-keyint_min' ... matched as AVOption 'keyint_min' with argument '60'.\nReading option '-hls_time' ... matched as AVOption 'hls_time' with argument '2'.\nReading option '-hls_playlist_type' ... matched as AVOption 'hls_playlist_type' with argument 'vod'.\nReading option '-movflags' ... matched as AVOption 'movflags' with argument '+faststart'.\nReading option '-vf' ... matched as option 'vf' (set video filters) with argument 'scale=w=320:h=240:force_original_aspect_ratio=decrease'.\nReading option '-b:v' ... matched as option 'b' (video bitrate (please use -b:v)) with argument '300k'.\nReading option '-maxrate' ... matched as AVOption 'maxrate' with argument '300k'.\nReading option '-bufsize' ... matched as AVOption 'bufsize' with argument '300k'.\nReading option '-b:a' ... matched as option 'b' (video bitrate (please use -b:v)) with argument '64k'.\nReading option '-hls_segment_filename' ... matched as AVOption 'hls_segment_filename' with argument 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/240p_%09d.ts'.\nReading option 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/240p.m3u8' ... matched as output url.\nReading option '-acodec' ... matched as option 'acodec' (force audio codec ('copy' to copy stream)) with argument 'aac'.\nReading option '-ar' ... matched as option 'ar' (set audio sampling rate (in Hz)) with argument '44100'.\nReading option '-vcodec' ... matched as option 'vcodec' (force video codec ('copy' to copy stream)) with argument 'h264'.\nReading option '-profile:v' ... matched as option 'profile' (set profile) with argument 'main'.\nReading option '-crf' ... matched as AVOption 'crf' with argument '20'.\nReading option '-sc_threshold' ... matched as AVOption 'sc_threshold' with argument '40'.\nReading option '-g' ... matched as AVOption 'g' with argument '60'.\nReading option '-keyint_min' ... matched as AVOption 'keyint_min' with argument '60'.\nReading option '-hls_time' ... matched as AVOption 'hls_time' with argument '2'.\nReading option '-hls_playlist_type' ... matched as AVOption 'hls_playlist_type' with argument 'vod'.\nReading option '-movflags' ... matched as AVOption 'movflags' with argument '+faststart'.\nReading option '-vf' ... matched as option 'vf' (set video filters) with argument 'scale=w=640:h=480:force_original_aspect_ratio=decrease'.\nReading option '-b:v' ... matched as option 'b' (video bitrate (please use -b:v)) with argument '800k'.\nReading option '-maxrate' ... matched as AVOption 'maxrate' with argument '800k'.\nReading option '-bufsize' ... matched as AVOption 'bufsize' with argument '800k'.\nReading option '-b:a' ... matched as option 'b' (video bitrate (please use -b:v)) with argument '96k'.\nReading option '-hls_segment_filename' ... matched as AVOption 'hls_segment_filename' with argument 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/480p_%09d.ts'.\nReading option 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/480p.m3u8' ... matched as output url.\nFinished splitting the commandline.\nParsing a group of options: global .\nApplying option hide_banner (do not show program banner) with argument 1.\nApplying option y (overwrite output files) with argument 1.\nApplying option loglevel (set logging level) with argument debug.\nSuccessfully parsed a group of options.\nParsing a group of options: input url output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4.\nSuccessfully parsed a group of options.\nOpening an input file: output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4.\n[NULL @ 0x149f04b80] Opening 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4' for reading\n[file @ 0x149f04ed0] Setting default whitelist 'file,crypto,data'\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] Format mov,mp4,m4a,3gp,3g2,mj2 probed with size=2048 and score=100\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] ISO: File Type Major Brand: mp42\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] Unknown dref type 0x206c7275 size 12\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] Processing st: 0, edit list 0 - media time: 0, duration: 71477806\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] Unknown dref type 0x206c7275 size 12\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] Processing st: 1, edit list 0 - media time: 0, duration: 44673629\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] Before avformat_find_stream_info() pos: 625824 bytes read:621563 seeks:1 nb_streams:2\n[h264 @ 0x149f07010] nal_unit_type: 7(SPS), nal_ref_idc: 1\n[h264 @ 0x149f07010] nal_unit_type: 8(PPS), nal_ref_idc: 1\n[h264 @ 0x149f07010] nal_unit_type: 7(SPS), nal_ref_idc: 1\n[h264 @ 0x149f07010] nal_unit_type: 8(PPS), nal_ref_idc: 1\n[h264 @ 0x149f07010] nal_unit_type: 6(SEI), nal_ref_idc: 0\n    Last message repeated 1 times\n[h264 @ 0x149f07010] nal_unit_type: 5(IDR), nal_ref_idc: 1\n    Last message repeated 4 times\n[h264 @ 0x149f07010] Format yuv420p chosen by get_format().\n[h264 @ 0x149f07010] Reinit context to 480x368, pix_fmt: yuv420p\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] All info found\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x149f04b80] After avformat_find_stream_info() pos: 703947 bytes read:654331 seeks:2 frames:48\nInput #0, mov,mp4,m4a,3gp,3g2,mj2, from 'output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4':\n  Metadata:\n    major_brand     : mp42\n    minor_version   : 1\n    compatible_brands: mp41mp42isom\n    creation_time   : 2017-10-09T19:23:41.000000Z\n  Duration: 00:24:49.12, start: 0.000000, bitrate: 1008 kb/s\n  Stream #0:0[0x1](eng), 47, 1/48000: Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp, 252 kb/s (default)\n    Metadata:\n      creation_time   : 2017-10-09T19:23:41.000000Z\n      handler_name    : Core Media Audio\n      vendor_id       : [0][0][0][0]\n  Stream #0:1[0x2](und), 1, 1/30000: Video: h264 (High), 1 reference frame (avc1 / 0x31637661), yuv420p(tv, smpte170m/smpte170m/bt709, progressive, left), 480x360 (480x368) [SAR 1:1 DAR 4:3], 0/1, 753 kb/s, 29.97 fps, 29.97 tbr, 30k tbn (default)\n    Metadata:\n      creation_time   : 2017-10-09T19:23:41.000000Z\n      handler_name    : Core Media Video\n      vendor_id       : [0][0][0][0]\nSuccessfully opened the file.\nParsing a group of options: output url output/bdfabf92-dd1c-4859-935b-9a004141d88f/120p.m3u8.\nApplying option map (set input stream mapping) with argument 0:v:1.\nStream map '0:v:1' matches no streams.\nTo ignore this, add a trailing '?' to the map.\n[AVIOContext @ 0x149f05030] Statistics: 654331 bytes read, 2 seeks"
  },
  "commands" : {
    "hls" : {
      "command" : "ffmpeg -hide_banner -y -loglevel debug -i output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4 -map 0:v:1  -acodec aac -ar 44100 -vcodec h264 -profile:v main -crf 20 -sc_threshold 40 -g 60 -keyint_min 60 -hls_time 2 -hls_playlist_type vod -movflags +faststart -vf scale=w=160:h=120:force_original_aspect_ratio=decrease -b:v 128k -maxrate 128k -bufsize 128k -b:a 32k -hls_segment_filename \"output/bdfabf92-dd1c-4859-935b-9a004141d88f/120p_%09d.ts\" \"output/bdfabf92-dd1c-4859-935b-9a004141d88f/120p.m3u8\" -acodec aac -ar 44100 -vcodec h264 -profile:v main -crf 20 -sc_threshold 40 -g 60 -keyint_min 60 -hls_time 2 -hls_playlist_type vod -movflags +faststart -vf scale=w=320:h=240:force_original_aspect_ratio=decrease -b:v 300k -maxrate 300k -bufsize 300k -b:a 64k -hls_segment_filename \"output/bdfabf92-dd1c-4859-935b-9a004141d88f/240p_%09d.ts\" \"output/bdfabf92-dd1c-4859-935b-9a004141d88f/240p.m3u8\" -acodec aac -ar 44100 -vcodec h264 -profile:v main -crf 20 -sc_threshold 40 -g 60 -keyint_min 60 -hls_time 2 -hls_playlist_type vod -movflags +faststart -vf scale=w=640:h=480:force_original_aspect_ratio=decrease -b:v 800k -maxrate 800k -bufsize 800k -b:a 96k -hls_segment_filename \"output/bdfabf92-dd1c-4859-935b-9a004141d88f/480p_%09d.ts\" \"output/bdfabf92-dd1c-4859-935b-9a004141d88f/480p.m3u8\"",
      "output" : null,
      "hls_args" : {
        "hls_profile" : "sd",
        "hls_bitrate_ratio" : 1,
        "hls_buffer_ratio" : 1
      },
      "input_options" : {
        "i" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4",
        "map" : "0:v:1"
      },
      "output_options" : {
        "directory" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f"
      },
      "cli_options" : {
        "hide_banner" : true,
        "y" : true,
        "loglevel" : "debug"
      },
      "options" : {
        "acodec" : "aac",
        "ar" : "44100",
        "vcodec" : "h264",
        "profile:v" : "main",
        "crf" : "20",
        "sc_threshold" : "40",
        "g" : "60",
        "keyint_min" : "60",
        "hls_time" : "2",
        "hls_playlist_type" : "vod",
        "movflags" : "+faststart",
        "vf" : "",
        "b:v" : "",
        "maxrate" : "",
        "bufsize" : "",
        "b:a" : ""
      },
      "rendition_options" : {
        "vf" : "scale=w={}:h={}:force_original_aspect_ratio=decrease",
        "b:v" : "{}k",
        "maxrate" : "{0}k",
        "bufsize" : "{0}k",
        "b:a" : "{0}k",
        "hls_segment_filename" : "{0}/{1}_%09d.ts' '{0}/{1}.m3u8"
      }
    },
    "transcript" : {
      "command" : "autosub -o output/bdfabf92-dd1c-4859-935b-9a004141d88f/subtitles.json -D en -S en -C 10 -F json output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav",
      "output" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/subtitles.json",
      "options" : {
        "o" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/subtitles.json",
        "D" : "en",
        "S" : "en",
        "C" : "10",
        "F" : "json"
      }
    },
    "peaks" : {
      "command" : "audiowaveform -i output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav -o output/bdfabf92-dd1c-4859-935b-9a004141d88f/peaks.json",
      "output" : null,
      "options" : {
        "i" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav",
        "o" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/peaks.json"
      }
    },
    "audio" : {
      "command" : "ffmpeg -hide_banner -y -loglevel debug -i output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4 -ac 1 -acodec pcm_s16le -ar 44800 -map 0:a:0 output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.wav",
      "output" : null,
      "cli_options" : {
        "hide_banner" : true,
        "y" : true,
        "loglevel" : "debug"
      },
      "options" : {
        "i" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4",
        "ac" : "1",
        "acodec" : "pcm_s16le",
        "ar" : "44800",
        "map" : "0:a:0"
      }
    },
    "thumbnails" : {
      "command" : null,
      "output" : null,
      "cli_options" : {
        "hide_banner" : true,
        "y" : true,
        "loglevel" : "debug"
      },
      "options" : {
        "i" : "",
        "f" : "image2",
        "vf" : "fps=fps=1/10"
      }
    }
  },
  "source" : {
    "info" : {
      "programs" : [],
      "streams" : [
        {
          "index" : 0,
          "codec_name" : "aac",
          "codec_long_name" : "AAC (Advanced Audio Coding)",
          "profile" : "LC",
          "codec_type" : "audio",
          "codec_tag_string" : "mp4a",
          "codec_tag" : "0x6134706d",
          "sample_fmt" : "fltp",
          "sample_rate" : "48000",
          "channels" : 2,
          "channel_layout" : "stereo",
          "bits_per_sample" : 0,
          "id" : "0x1",
          "r_frame_rate" : "0/0",
          "avg_frame_rate" : "0/0",
          "time_base" : "1/48000",
          "start_pts" : 0,
          "start_time" : "0.000000",
          "duration_ts" : 71477806,
          "duration" : "1489.120958",
          "bit_rate" : "252135",
          "nb_frames" : "69805",
          "extradata_size" : 2,
          "disposition" : {
            "default" : 1,
            "dub" : 0,
            "original" : 0,
            "comment" : 0,
            "lyrics" : 0,
            "karaoke" : 0,
            "forced" : 0,
            "hearing_impaired" : 0,
            "visual_impaired" : 0,
            "clean_effects" : 0,
            "attached_pic" : 0,
            "timed_thumbnails" : 0,
            "captions" : 0,
            "descriptions" : 0,
            "metadata" : 0,
            "dependent" : 0,
            "still_image" : 0
          },
          "tags" : {
            "creation_time" : "2017-10-09T19:23:41.000000Z",
            "language" : "eng",
            "handler_name" : "Core Media Audio",
            "vendor_id" : "[0][0][0][0]"
          }
        },
        {
          "index" : 1,
          "codec_name" : "h264",
          "codec_long_name" : "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
          "profile" : "High",
          "codec_type" : "video",
          "codec_tag_string" : "avc1",
          "codec_tag" : "0x31637661",
          "width" : 480,
          "height" : 360,
          "coded_width" : 480,
          "coded_height" : 360,
          "closed_captions" : 0,
          "film_grain" : 0,
          "has_b_frames" : 0,
          "sample_aspect_ratio" : "1:1",
          "display_aspect_ratio" : "4:3",
          "pix_fmt" : "yuv420p",
          "level" : 30,
          "color_range" : "tv",
          "color_space" : "smpte170m",
          "color_transfer" : "bt709",
          "color_primaries" : "smpte170m",
          "chroma_location" : "left",
          "field_order" : "progressive",
          "refs" : 1,
          "is_avc" : "true",
          "nal_length_size" : "4",
          "id" : "0x2",
          "r_frame_rate" : "30000/1001",
          "avg_frame_rate" : "30000/1001",
          "time_base" : "1/30000",
          "start_pts" : 0,
          "start_time" : "0.000000",
          "duration_ts" : 44673629,
          "duration" : "1489.120967",
          "bit_rate" : "753340",
          "bits_per_raw_sample" : "8",
          "nb_frames" : "44629",
          "extradata_size" : 36,
          "disposition" : {
            "default" : 1,
            "dub" : 0,
            "original" : 0,
            "comment" : 0,
            "lyrics" : 0,
            "karaoke" : 0,
            "forced" : 0,
            "hearing_impaired" : 0,
            "visual_impaired" : 0,
            "clean_effects" : 0,
            "attached_pic" : 0,
            "timed_thumbnails" : 0,
            "captions" : 0,
            "descriptions" : 0,
            "metadata" : 0,
            "dependent" : 0,
            "still_image" : 0
          },
          "tags" : {
            "creation_time" : "2017-10-09T19:23:41.000000Z",
            "language" : "und",
            "handler_name" : "Core Media Video",
            "vendor_id" : "[0][0][0][0]"
          }
        }
      ],
      "chapters" : [],
      "format" : {
        "filename" : "output/bdfabf92-dd1c-4859-935b-9a004141d88f/source.mp4",
        "nb_streams" : 2,
        "nb_programs" : 0,
        "format_name" : "mov,mp4,m4a,3gp,3g2,mj2",
        "format_long_name" : "QuickTime / MOV",
        "start_time" : "0.000000",
        "duration" : "1489.120967",
        "size" : "187786787",
        "bit_rate" : "1008846",
        "probe_score" : 100,
        "tags" : {
          "major_brand" : "mp42",
          "minor_version" : "1",
          "compatible_brands" : "mp41mp42isom",
          "creation_time" : "2017-10-09T19:23:41.000000Z"
        }
      }
    },
    "input" : {
      "filename" : null,
      "video_stream" : 1,
      "audio_stream" : 0
    }
  }
}
```
