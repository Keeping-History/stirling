from dataclasses import dataclass
from typing import List

from core import core, framework


@dataclass
class StirlingEncoder(core.StirlingClass):
    """StirlingEncoder is a class for handling encoder options.

    Attributes:
        name (str): The name of the encoder. We prefer to focus on the name
            of the underlying Video Coding Format (or Video Compression
            Format/Standard, VCF for short) and not the container format or
            codec. For example, we use `AVC` (for h.264 standard video)
            instead of `mp4` or `ts`, or `AV1` instead of `webm` or `mkv`.
        options (dict): A dictionary of options to pass to the encoder.

    """

    name: str
    encoder_library_default: str
    options: dict
    frameworks: List[framework.StirlingMediaFramework]
    encoder_libraries: List[str]


@dataclass(kw_only=True)
class StirlingVideoEncoderAV1(StirlingEncoder):
    """A class for handling the AV1 Video Coding Format.

    A StirlingVideoEncoderAV1 contains the necessary options for creating
    a video/audio file using the AV1 Video Coding Format. The class makes
    creating a video file using the AV1 Video Coding Format easy by providing
    a minimal set of options that provide the best, opinionated defaults for
    video encoding.


    Attributes:
        name (str): The name of the encoder. This is `av1`.
        frameworks (str): A list of frameworks supported by this encoder.
        encoder_libraries (list): A list of available encoder libraries for the AV1 Video Coding Format.
        options (dict): A holder for all the encoder's options, until
            they are ready to be parsed into a command (or arguments for a
            command).
        encoder_library_default (str): The encoder or encoder library to use. Defaults
            to `aom` (or `libaom-av1`), which is the current reference encoder
            for AV1. SVT-AV1 is the newest reference encoder going forward.
            Currently, we are not providing support for `librav1e` (which
            promises to be faster, but has poorer documentation IMHO).
        encoder_keyframe_fps_interval (float): Sets the number of seconds between
            keyframes. This value is multiplied by the frames-per-second (fps)
            of the source video file to determine how many frames should pass
            before inserting a new keyframe. For AV1, this will also set the GOP
            (Group of Pictures) size.
        encoder_fps (int): The frames-per-second of the video. This is used to
            calculate the keyframe interval, among other things.
        encoder_mode (str): When encoding video, we will either aim for a
            Constant Bit Rate (CBR) or a Variable Bit Rate (VBR). CBR is for
            streaming files where we want to control the bitrate (or, setting a
            consistent amount of data size for each frame of video). VBR is for
            files that we want to archive at their full quality, without
            worrying about the bitrate, but rather the final file size. Default
            is VBR.
        encoder_quality_level (int): The quality level is the Constant Rate
            Factor (CRF) for the encoder when using VBR encoding, or an
            alternative to setting a minimum and maximum bitrate target when
            using CBR encoding. Since our video encoder is intended to create
            files for archival rather than streaming, we're more concerned with
            over quality rather than a set bitrate. The default value is 12,
            which is a good high-quality setting without adding too much extra
            size to the file. For SVT-AV1, the range is 1-63, with 1 being the
            best quality but highest file size, and 63 being the worst quality
            but lowest file size.
        encoder_bitrate_target (int): The target bitrate (or size per frame)
            of the video, in kilobits. This is used when encoding using CBR. If
            the `encoder_bitrate_min` and `encoder_bitrate_max` are not set,
            then the `encoder_quality_level` must be set.
        encoder_bitrate_min (int): The minimum bitrate (or size per frame) of
            the video, in kilobits. This is used when encoding using CBR.
            Generally, the encoder_bitrate_target should be set. Must also be
            set with encoder_bitrate_max.
        encoder_bitrate_max (int): The maximum bitrate (or size per frame) of
            the video, in kilobits. This is used when encoding using CBR.
            Generally, the encoder_bitrate_target should be set, however the
            maximum is useful when creating lower-quality previews of a video.
            Must also be set with encoder_bitrate_min.
        encoder_quality_profile (str): The quality profile (or in some encoders,
            like AV1, the preset) refers to the `preset` option available in
            some AV1 encoders. Currently, only SVT-AV1 supports this option. The
            default preset is 0 for maximum quality.

    """

    name: str = "av1"
    frameworks: list = field(default_factory=lambda: ["ffmpeg"])
    encoders: list = field(default_factory=lambda: ["aom", "svt"])
    formats: list = field(default_factory=lambda: ["av1"]) # TODO: WHAT ARE WE TRYING TO ACCOMPLISH HERE?
    options: dict = field(default_factory=dict)
    encoder_default: str = "aom"
    encoder_keyframe_interval: float = 10
    encoder_fps: int = 0
    encoder_mode: str = "vbr"
    encoder_quality_level: int = 12
    encoder_quality_profile: str = "0"
    encoder_bitrate_target: int = 0
    encoder_bitrate_min: int = 0
    encoder_bitrate_max: int = 0
    encoder_subjective: bool = True
    encoder_keyframe_interval: float
    encoder_fps: int
    encoder_mode: str
    encoder_quality_level: int
    encoder_quality_profile: str
    encoder_bitrate_target: int
    encoder_bitrate_min: int
    encoder_bitrate_max: int
    encoder_subjective: bool

    def __post_init__(self):
        self.name = "av1"
        self.frameworks = [framework.StirlingMediaFrameworkFFmpeg]
        self.encoder_libraries = ["aom", "svt"]
        self.encoder_library_default = "aom"
        self.encoder_mode = "vbr"
        self.encoder_quality_level = 12
        self.encoder_quality_profile = "0"
        self.encoder_bitrate_target = 0
        self.encoder_bitrate_min = 0
        self.encoder_bitrate_max = 0
        self.encoder_subjective = True
        self.encoder_keyframe_interval = 10.0

    def get(self, encoder_library: str, options: dict = None):
        if encoder_library is None:
            encoder_library = self.encoder_library_default
        if encoder_library in self.options:
            return self.__get_encoder_options(encoder_library, options)

    def __get_encoder_options(self, encoder_library: str, options: dict):
        keyframe_fps_interval = self.encoder_keyframe_interval * self.encoder_fps
        if keyframe_fps_interval <= 0:
            keyframe_fps_interval = 30  # default to 1 frame every 30 frames

        match encoder_library:
            case "aom":
                self.options = {
                    "c:v": "libaom-av1",
                    "g": keyframe_fps_interval,
                    "keyint_min": keyframe_fps_interval,
                }
                match self.encoder_mode:
                    case "vbr":
                        vbr_options = {
                            "crf": self.encoder_quality_level,
                            "b:v": 0,  # Must be set to 0 for CRF.
                        }
                        self.options = {**self.options, **vbr_options}
                    case "cbr":
                        cbr_options = {
                            "b:v": self.encoder_bitrate_target + "k",
                        }
                        if (
                            self.encoder_bitrate_min is not None
                            and self.encoder_bitrate_max is not None
                        ):
                            cbr_bitrate_options = {
                                "minrate": self.encoder_bitrate_min + "k",
                                "maxrate": self.encoder_bitrate_max + "k",
                            }
                        else:
                            cbr_bitrate_options = {
                                "b:v": self.encoder_bitrate_target + "k",
                                "crf": self.encoder_quality_level,
                            }
                        self.options = {
                            **self.options,
                            **cbr_options,
                            **cbr_bitrate_options,
                        }

            case "svt":
                self.options = {
                    "c:v": "libsvtav1",
                    "g": self.encoder_keyframe_fps_interval * self.encoder_fps,
                }
                match self.encoder_mode:
                    case "vbr":
                        vbr_options = {
                            "crf": self.encoder_quality_level,
                            "preset": int(self.encoder_quality_profile),
                            "svtav1-params": f"tune={0 if self.encoder_subjective else 1}",
                        }
