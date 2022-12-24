from dataclasses import dataclass, field

from stirling import core, job

# Specify the required binaries in a list.
required_binaries = ["autosub"]


@dataclass
class StirlingPluginTranscript(core.StirlingPlugin):
    """StirlingPluginTranscript are for creating speech-to-text transcripts.
    These transcripts can be used as-is, or can be used later for
    confidence training, language analysis or for adding other contexts."""

    name: str = "transcript"
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
            assert core.check_dependencies_binaries(required_binaries), AssertionError(
                "Missing required binaries: {}".format(required_binaries)
            )

    ## Extract Audio from file
    def cmd(self, job: job.StirlingJob):
        if not self.transcript_disable:
            output_file = (
                job.output_directory
                / job.output_annotations_directory
                / (self.name + ".json")
            )

            input_file = job.get_plugin_asset("audio", "normalized_audio")

            # Set the options to extract audio from the source file.
            options = {
                "o": str(output_file),
                "D": self.transcript_lang_output,
                "S": self.transcript_lang_input,
                "C": self.transcript_concurrency,
                "F": self.transcript_format,
            }

            job.commands.append(
                core.StirlingCmd(
                    name=self.name,
                    command="autosub {} {}".format(
                        core.default_unparser.unparse(**options), str(input_file)
                    ),
                    priority=self.priority,
                    expected_output=str(output_file),
                    depends_on=self.depends_on,
                )
            )
