import argunparse

default_unparser = argunparse.ArgumentUnparser(long_opt="--", opt_value=" ")
autosub_unparser = argunparse.ArgumentUnparser(long_opt="--", opt_value="=")
ffmpeg_unparser = argunparse.ArgumentUnparser(
    long_opt="-", opt_value=" ", begin_delim="", end_delim=""
)
