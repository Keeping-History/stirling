from dataclasses import dataclass, field

from core import args, definitions, helpers, jobs

# Specify the required binaries in a list.
required_binaries = ["autosub"]


@dataclass
class StirlingPluginTranscript(definitions.StirlingPlugin):
    """StirlingPluginTranscript are for creating speech-to-text transcripts.
    These transcripts can be used as-is, or can be used later for
    confidence training, language analysis or for adding other contexts."""

    plugin_name: str = "transcript"
    depends_on: list = field(default_factory=lambda: ["audio"])
    priority: int = 10

    # Disable the generation of audio peak data.
    transcript_disable: bool = False
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
            / (self.plugin_name + ".json")
        )

        # Set the options to extract audio from the source file.
        options = {
            "o": str(output_file),
            "D": self.transcript_lang_output,
            "S": self.transcript_lang_input,
            "C": self.transcript_concurrency,
            "F": self.transcript_format,
        }

        job.commands.append(
            definitions.StrilingCmd(
                plugin_name=self.plugin_name,
                command="autosub {} {}".format(
                    args.default_unparser.unparse(**options), str(job.media_info.source)
                ),
                priority=self.priority,
                expected_output=output_file,
                depends_on=self.depends_on,
            )
        )
