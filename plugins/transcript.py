from dataclasses import dataclass, field
from typing import List

from core import args, definitions, helpers, jobs

# Specify the required binaries in a list.
required_binaries = ["autosub"]


@dataclass
class StirlingPluginTranscript(definitions.StirlingClass):
    """StirlingPluginTranscript are for creating speech-to-text transcripts.
    These transcripts can be used as-is, or can be used later for
    confidence training, language analysis or for adding other contexts."""

    _plugin_name: str = "transcript"
    _depends_on: list = field(default_factory=lambda: ['audio'])
    _weight: int = 10

    # Disable the generation of audio peak data.
    transcript_disable: bool = False
    # Command to run to execute this plugin.
    commands: List[definitions.StrilingCmd] = field(default_factory=list)
    # Files to output.
    outputs: list = field(default_factory=list)

    # Additional configuration variables for this plugin.
    transcript_lang_input: str = "en"
    # Additional configuration variables for this plugin.
    transcript_lang_output: str = "en"
    # The number of concurrent API requests to make
    transcript_concurrency: int = 10
    # The format to output the transcript to.
    transcript_format: str = "json"

    ## Extract Audio from file
    def __post_init__(self):
        if not self.transcript_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert helpers.check_dependencies_binaries(
                required_binaries
            ), AssertionError("Missing required binaries: {}".format(required_binaries))

    ## Extract Audio from file
    def cmd(self, job: jobs.StirlingJob):
        output_file = (
            job.output_directory
            / job.output_annotations_directory
            / (self._plugin_name + ".json")
        )

        # Set the options to extract audio from the source file.
        options = {
            "o": str(output_file),
            "D": self.transcript_lang_output,
            "S": self.transcript_lang_input,
            "C": self.transcript_concurrency,
            "F": self.transcript_format,
        }

        self.commands.append(
            definitions.StrilingCmd(
                plugin_name=self._plugin_name,
                command="autosub {} {}".format(
                    args.default_unparser.unparse(**options), str(job.media_info.source)
                ),
                weight=self._weight,
                output=output_file,
                depends_on=self._depends_on,
            )
        )
