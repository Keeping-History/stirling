from datetime import datetime
from enum import Enum
from json import dumps
from pathlib import Path
from uuid import UUID

from colored import attr, bg, fg
from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.encodings import StirlingJSONEncoder


class StirlingLoggerLevel(int, Enum):
    """StirlingLoggerLevel is a class that contains all of the levels that can be used by the StirlingLogger."""

    QUIET = 0
    CRITICAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5


class StirlingLoggerColors:
    """StirlingLoggerColors is a class that contains all of the colors that can be used by the StirlingLogger.

    A table of colors is available by running the following command in a terminal window:
    curl -s https://gist.githubusercontent.com/HaleTom/89ffe32783f89f403bba96bd7bcd1263/raw/e50a28ec54188d2413518788de6c6367ffcea4f7/print256colours.sh | bash

    """

    DEFAULT = attr(0)

    SEPARATOR = fg(8)
    HEADER = bg(8) + fg(0)
    TIMESTAMP = fg(18)
    DURATION = fg(8)

    ERROR = bg(9) + fg(0)
    WARNING = bg(3) + fg(0)
    INFO = fg(2)
    DEBUG = fg(11)
    RESET = attr(0)

    MESSAGE = attr(0)

    OBJECT = fg(8)
    OBJECT_LINE_HEADER = fg(8)

#         self.paint = {
#             'black': '0',
#             'red': '1',
#             'green': '2',
#             'yellow': '3',
#             'blue': '4',
#             'magenta': '5',
#             'cyan': '6',
#             'light_gray': '7',
#             'dark_gray': '8',
#             'light_red': '9',
#             'light_green': '10',
#             'light_yellow': '11',
#             'light_blue': '12',
#             'light_magenta': '13',
#             'light_cyan': '14',
#             'white': '15',
#             'grey_0': '16',
#             'navy_blue': '17',
#             'dark_blue': '18',
#             'blue_3a': '19',
#             'blue_3b': '20',
#             'blue_1': '21',
#             'dark_green': '22',
#             'deep_sky_blue_4a': '23',
#             'deep_sky_blue_4b': '24',
#             'deep_sky_blue_4c': '25',
#             'dodger_blue_3': '26',
#             'dodger_blue_2': '27',
#             'green_4': '28',
#             'spring_green_4': '29',
#             'turquoise_4': '30',
#             'deep_sky_blue_3a': '31',
#             'deep_sky_blue_3b': '32',
#             'dodger_blue_1': '33',
#             'green_3a': '34',
#             'spring_green_3a': '35',
#             'dark_cyan': '36',
#             'light_sea_green': '37',
#             'deep_sky_blue_2': '38',
#             'deep_sky_blue_1': '39',
#             'green_3b': '40',
#             'spring_green_3b': '41',
#             'spring_green_2a': '42',
#             'cyan_3': '43',
#             'dark_turquoise': '44',
#             'turquoise_2': '45',
#             'green_1': '46',
#             'spring_green_2b': '47',
#             'spring_green_1': '48',
#             'medium_spring_green': '49',
#             'cyan_2': '50',
#             'cyan_1': '51',
#             'dark_red_1': '52',
#             'deep_pink_4a': '53',
#             'purple_4a': '54',
#             'purple_4b': '55',
#             'purple_3': '56',
#             'blue_violet': '57',
#             'orange_4a': '58',
#             'grey_37': '59',
#             'medium_purple_4': '60',
#             'slate_blue_3a': '61',
#             'slate_blue_3b': '62',
#             'royal_blue_1': '63',
#             'chartreuse_4': '64',
#             'dark_sea_green_4a': '65',
#             'pale_turquoise_4': '66',
#             'steel_blue': '67',
#             'steel_blue_3': '68',
#             'cornflower_blue': '69',
#             'chartreuse_3a': '70',
#             'dark_sea_green_4b': '71',
#             'cadet_blue_2': '72',
#             'cadet_blue_1': '73',
#             'sky_blue_3': '74',
#             'steel_blue_1a': '75',
#             'chartreuse_3b': '76',
#             'pale_green_3a': '77',
#             'sea_green_3': '78',
#             'aquamarine_3': '79',
#             'medium_turquoise': '80',
#             'steel_blue_1b': '81',
#             'chartreuse_2a': '82',
#             'sea_green_2': '83',
#             'sea_green_1a': '84',
#             'sea_green_1b': '85',
#             'aquamarine_1a': '86',
#             'dark_slate_gray_2': '87',
#             'dark_red_2': '88',
#             'deep_pink_4b': '89',
#             'dark_magenta_1': '90',
#             'dark_magenta_2': '91',
#             'dark_violet_1a': '92',
#             'purple_1a': '93',
#             'orange_4b': '94',
#             'light_pink_4': '95',
#             'plum_4': '96',
#             'medium_purple_3a': '97',
#             'medium_purple_3b': '98',
#             'slate_blue_1': '99',
#             'yellow_4a': '100',
#             'wheat_4': '101',
#             'grey_53': '102',
#             'light_slate_grey': '103',
#             'medium_purple': '104',
#             'light_slate_blue': '105',
#             'yellow_4b': '106',
#             'dark_olive_green_3a': '107',
#             'dark_green_sea': '108',
#             'light_sky_blue_3a': '109',
#             'light_sky_blue_3b': '110',
#             'sky_blue_2': '111',
#             'chartreuse_2b': '112',
#             'dark_olive_green_3b': '113',
#             'pale_green_3b': '114',
#             'dark_sea_green_3a': '115',
#             'dark_slate_gray_3': '116',
#             'sky_blue_1': '117',
#             'chartreuse_1': '118',
#             'light_green_2': '119',
#             'light_green_3': '120',
#             'pale_green_1a': '121',
#             'aquamarine_1b': '122',
#             'dark_slate_gray_1': '123',
#             'red_3a': '124',
#             'deep_pink_4c': '125',
#             'medium_violet_red': '126',
#             'magenta_3a': '127',
#             'dark_violet_1b': '128',
#             'purple_1b': '129',
#             'dark_orange_3a': '130',
#             'indian_red_1a': '131',
#             'hot_pink_3a': '132',
#             'medium_orchid_3': '133',
#             'medium_orchid': '134',
#             'medium_purple_2a': '135',
#             'dark_goldenrod': '136',
#             'light_salmon_3a': '137',
#             'rosy_brown': '138',
#             'grey_63': '139',
#             'medium_purple_2b': '140',
#             'medium_purple_1': '141',
#             'gold_3a': '142',
#             'dark_khaki': '143',
#             'navajo_white_3': '144',
#             'grey_69': '145',
#             'light_steel_blue_3': '146',
#             'light_steel_blue': '147',
#             'yellow_3a': '148',
#             'dark_olive_green_3': '149',
#             'dark_sea_green_3b': '150',
#             'dark_sea_green_2': '151',
#             'light_cyan_3': '152',
#             'light_sky_blue_1': '153',
#             'green_yellow': '154',
#             'dark_olive_green_2': '155',
#             'pale_green_1b': '156',
#             'dark_sea_green_5b': '157',
#             'dark_sea_green_5a': '158',
#             'pale_turquoise_1': '159',
#             'red_3b': '160',
#             'deep_pink_3a': '161',
#             'deep_pink_3b': '162',
#             'magenta_3b': '163',
#             'magenta_3c': '164',
#             'magenta_2a': '165',
#             'dark_orange_3b': '166',
#             'indian_red_1b': '167',
#             'hot_pink_3b': '168',
#             'hot_pink_2': '169',
#             'orchid': '170',
#             'medium_orchid_1a': '171',
#             'orange_3': '172',
#             'light_salmon_3b': '173',
#             'light_pink_3': '174',
#             'pink_3': '175',
#             'plum_3': '176',
#             'violet': '177',
#             'gold_3b': '178',
#             'light_goldenrod_3': '179',
#             'tan': '180',
#             'misty_rose_3': '181',
#             'thistle_3': '182',
#             'plum_2': '183',
#             'yellow_3b': '184',
#             'khaki_3': '185',
#             'light_goldenrod_2a': '186',
#             'light_yellow_3': '187',
#             'grey_84': '188',
#             'light_steel_blue_1': '189',
#             'yellow_2': '190',
#             'dark_olive_green_1a': '191',
#             'dark_olive_green_1b': '192',
#             'dark_sea_green_1': '193',
#             'honeydew_2': '194',
#             'light_cyan_1': '195',
#             'red_1': '196',
#             'deep_pink_2': '197',
#             'deep_pink_1a': '198',
#             'deep_pink_1b': '199',
#             'magenta_2b': '200',
#             'magenta_1': '201',
#             'orange_red_1': '202',
#             'indian_red_1c': '203',
#             'indian_red_1d': '204',
#             'hot_pink_1a': '205',
#             'hot_pink_1b': '206',
#             'medium_orchid_1b': '207',
#             'dark_orange': '208',
#             'salmon_1': '209',
#             'light_coral': '210',
#             'pale_violet_red_1': '211',
#             'orchid_2': '212',
#             'orchid_1': '213',
#             'orange_1': '214',
#             'sandy_brown': '215',
#             'light_salmon_1': '216',
#             'light_pink_1': '217',
#             'pink_1': '218',
#             'plum_1': '219',
#             'gold_1': '220',
#             'light_goldenrod_2b': '221',
#             'light_goldenrod_2c': '222',
#             'navajo_white_1': '223',
#             'misty_rose1': '224',
#             'thistle_1': '225',
#             'yellow_1': '226',
#             'light_goldenrod_1': '227',
#             'khaki_1': '228',
#             'wheat_1': '229',
#             'cornsilk_1': '230',
#             'grey_100': '231',
#             'grey_3': '232',
#             'grey_7': '233',
#             'grey_11': '234',
#             'grey_15': '235',
#             'grey_19': '236',
#             'grey_23': '237',
#             'grey_27': '238',
#             'grey_30': '239',
#             'grey_35': '240',
#             'grey_39': '241',
#             'grey_42': '242',
#             'grey_46': '243',
#             'grey_50': '244',
#             'grey_54': '245',
#             'grey_58': '246',
#             'grey_62': '247',
#             'grey_66': '248',
#             'grey_70': '249',
#             'grey_74': '250',
#             'grey_78': '251',
#             'grey_82': '252',
#             'grey_85': '253',
#             'grey_89': '254',
#             'grey_93': '255',
#         }
@dataclass
class StirlingLogger(StirlingClass):
    log_file: Path
    log_level: StirlingLoggerLevel | int | None = StirlingLoggerLevel.QUIET
    time_start: datetime = datetime.now()
    header_separator: str = "|"
    line_continuation_prefix: str = "+"

    def _headers(self):
        return [self._date_line_header, self._duration_line_header]

    def log(self, message: str, *args) -> None:
        """Generic log function that defaults to info level."""
        return self.info(message, *args)

    def error(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.ERROR, *args)

    def warn(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.WARNING, *args)

    def info(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.INFO, *args)

    def debug(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.DEBUG, *args)

    def _date_line_header(self):
        return f"{StirlingLoggerColors.HEADER}{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}{StirlingLoggerColors.RESET}"

    def _duration_line_header(self):
        return f"{fg(8)}+{str(datetime.now() - self.time_start)}{attr(0)}"

    @staticmethod
    def _log_string(
        msg: str,
        line_identifier: str = line_continuation_prefix,
        indent: int = 4,
    ) -> str:
        """Log a string."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def _log_object(
        self, obj, prefix: str | None = None, header: str = "", indent: int = 4
    ) -> str:
        """Log an object.

        Args:
            obj: The object to log.
            prefix (str): The prefix to use for each line.
            header (str): A header to print before each line.
            indent (int): The number of spaces to indent each line of JSON.

        Returns:
            str: The object as a string for logging.
        """
        import re
        obj_string  = dumps(obj, indent=indent, cls=StirlingJSONEncoder)
        print(obj_string)

        def colorize_headers(obj_string):
            if group := obj_string.group():
                a = f"\"{StirlingLoggerColors.HEADER}{group[1:-2]}{StirlingLoggerColors.RESET}\":"
                return a

        def colorize_values(obj_string):
            if group := obj_string.group():
                a = f": {StirlingLoggerColors.HEADER}{group[2:-1]}{StirlingLoggerColors.RESET},"
                return a

        results = re.sub(r'\"(.*?)\":',colorize_headers, obj_string)
        results = re.sub(r': (.*?),',colorize_values, results)
        print(results)
        return self._log_string(
            header + dumps(obj, indent=indent, cls=StirlingJSONEncoder),
            prefix or self.line_continuation_prefix,
            indent,
        )

    def _logger(
        self, message: str, level=StirlingLoggerLevel.INFO, *args
    ) -> None:
        """Write a message to the log file.

        Args:
            message (str): The message to write to the log file.
            level (StirlingLoggerLevel): The level of the message.
            *args (object): Any additional objects to log to the file (as JSON).
        """

        if self.log_level >= level:
            obj_log = "".join(
                self._log_string(object_to_log)
                if isinstance(object_to_log, str)
                else self._log_object(object_to_log)
                for object_to_log in args
            )

            lines = [header() for header in self._headers()] + [
                level.name,
                f"{message}{obj_log}",
            ]

            log_line = f" {self.header_separator} ".join(lines)

            print(log_line)

            try:
                with open(
                    file=self.log_file, mode="a", encoding="utf-8"
                ) as log_file_object:
                    log_file_object.write(f"{log_line}")

                    # If we have any objects to log, log them
                    for line in obj_log.split("\n"):
                        # We're looping here in case we want to prettify each line
                        # (like above) in the future.
                        log_file_object.write(line + "\n")

            except OSError as exc:
                raise FileNotFoundError(
                    f"can't access the log file: {self.log_file}, \
                        stopping execution."
                ) from exc


@dataclass
class StirlingJobLogger(StirlingLogger):
    job_id: UUID | None = None

    def _headers(self):
        return [
            self._date_line_header,
            self._duration_line_header,
            self._job_id_header,
        ]

    def _job_id_header(self):
        return f"{StirlingLoggerColors.HEADER}{self.job_id}{StirlingLoggerColors.RESET}"
