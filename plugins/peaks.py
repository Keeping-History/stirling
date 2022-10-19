from dataclasses import dataclass, field
from typing import List

from core import args, definitions, helpers, jobs

required_binaries = ["audiowaveform"]


@dataclass
class StirlingPluginPeaks(definitions.StirlingClass):
    """StirlingPluginPeaks are are for creating waveform peaks from the input
    source's audio track."""

    _plugin_name: str = "peaks"
    _depends_on: list = field(default_factory=lambda: ['audio'])
    _weight: int = 10

    # Disable the generation of audio peak data.
    peaks_disable: bool = False

    # Additional configuration variables for this plugin.
    peaks_output_format: str = "json"

    # Command to run to execute this plugin.
    commands: List[definitions.StrilingCmd] = field(default_factory=list)
    # Files to output.
    outputs: list = field(default_factory=list)

    ## Extract Audio from file
    def __post_init__(self):
        if not self.peaks_disable:
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
            "i": str(job.media_info.source),
            "o": str(output_file),
            "output-format": self.peaks_output_format,
        }

        self.commands.append(
            definitions.StrilingCmd(
                plugin_name=self._plugin_name,
                command="audiowaveform {}".format(
                    args.default_unparser.unparse(**options)
                ),
                weight=self._weight,
                output=output_file,
                depends_on=self._depends_on,
            )
        )
