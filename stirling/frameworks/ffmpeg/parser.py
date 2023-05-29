from argunparse import ArgumentUnparser


def get_default_unparser():
    ffmpeg_unparser_options = {
        "long_opt": "-",
        "opt_value": " ",
        "begin_delim": "",
        "end_delim": "",
    }

    return ArgumentUnparser(**ffmpeg_unparser_options)


def get_probe_unparser():
    return get_default_unparser()


def get_command_unparser():
    return get_default_unparser()


def get_default_cli_options():
    return {
        "y": True,  # if output file exists, overwrite it
        "loglevel": "quiet",  # only print error messages
        "hide_banner": True,  # hide the ffmpeg command banner on launch
    }
