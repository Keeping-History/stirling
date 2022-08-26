# VIDEO RENDITIONS
# A rendition is a version of the video file that will be transcoded,
# based on the resolution and bitrate settings. The order of these renditions
# is important; the highest-quality rendition should be at the top, followed
# in descending order the remaining lesser-resolution renditions. This is
# because HLS streaming will select the first index.
# These standard profiles should work with any video/audio encoder.

# Quality	    Resolution	bitrate - low	bitrate - high	audio bitrate
# 120p          160x120     96k             128k            32k
# 240p	        426x240	    400k	        600k	        64k
# 360p	        640x360	    700k	        900k	        96k
# 480p	        854x480	    1250k	        1600k	        96k
# 720p	        1280x720	2500k	        3200k	        128k
# 1080p         1920x1080	4500k	        5300k	        128k
# 1080p High  	1920x1080	5800k	        7400k	        192k
# 4k    	    3840x2160	14000k	        18200	        192k
# 4k High   	3840x2160	23000k	        29500k	        192k

# TODO: Finish adding profiles here
hls_renditions = {
    "4k-high": {
        "width": "3840",
        "height": "2160",
        "bitrate": "29500",  # kbps
        "audio-bitrate": "192",  # kbps
    },
    "4k": {
        "width": "3840",
        "height": "2160",
        "bitrate": "14000",  # kbps
        "audio-bitrate": "192",  # kbps
    },
    "1080p-high": {
        "name": "1080p-high",
        "width": "1920",
        "height": "1080",
        "bitrate": "7400",  # kbps
        "audio-bitrate": "192",  # kbps
    },
    "1080p": {
        "name": "1080p",
        "width": "1920",
        "height": "1080",
        "bitrate": "7400",  # kbps
        "audio-bitrate": "128",  # kbps
    },
    "720p": {
        "name": "720p",
        "width": "1280",
        "height": "720",
        "bitrate": "7400",  # kbps
        "audio-bitrate": "128",  # kbps
    },
    "480p": {
        "name": "480p",
        "width": "640",
        "height": "480",
        "bitrate": "800",  # kbps
        "audio-bitrate": "96",  # kbps
    },
    "360p": {
        "name": "360p",
        "width": "480",
        "height": "360",
        "bitrate": "700",  # kbps
        "audio-bitrate": "96",  # kbps
    },
    "240p": {
        "name": "240p",
        "width": "320",
        "height": "240",
        "bitrate": "300",  # kbps
        "audio-bitrate": "64",  # kbps
    },
    "120p": {
        "name": "120p",
        "width": "160",
        "height": "120",
        "bitrate": "128",  # kbps
        "audio-bitrate": "32",  # kbps
    },
}

# Profiles are collections of renditions.
encoder_profiles = {
    "sd": [hls_renditions["120p"], hls_renditions["240p"], hls_renditions["480p"]],
}
