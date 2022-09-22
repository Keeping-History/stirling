import json
import os
import pathlib
import shutil
from datetime import datetime

import requests
import validators


def write_object(obj, filename):
    # Write the object to a file
    output_file = open(filename, "w")
    output_file.write(json.dumps(obj, indent=4, default=str))
    output_file.close()


def check_dependencies_binaries(required_binaries):
    required_binaries_missing = []
    for program in required_binaries:
        if shutil.which(program) is None:
            required_binaries_missing.append(program)
    if not len(required_binaries_missing) == 0:
        return "missing binary dependencies: {}".format(
            " ".join(required_binaries_missing)
        )
    return True


def get_input(job):
    source = job["source"]["input"]["filename"]
    output = job["output"]["directory"]
    disable_delete_source = job["arguments"]["disable_delete_source"]
    disable_source_copy = job["arguments"]["disable_source_copy"]

    # Get a full path to name our source file when we move it. We'll use this
    # value later on as an input filename for specific commands.
    incoming_filename = str(output) + "/source" + pathlib.Path(source).suffix

    # If the incoming source is a URL, then let's download it.
    if validators.url(source):
        response = requests.get(source)
        open(incoming_filename, "wb").write(response.content)
    else:
        if not disable_source_copy:
            # Unless this is a simulation or we explicitly disabled it, copy the source
            # file to the output directory as 'source'
            shutil.copyfile(pathlib.Path(source).absolute(), incoming_filename)
            if not disable_delete_source:
                os.remove(source)
        else:
            incoming_filename = source

    job["source"]["input"]["filename"] = pathlib.Path(incoming_filename)
    return job


def get_output_directory(job):
    output = job["arguments"]["output"]
    prefix = job["arguments"]["output_directory_prefix"]

    # Check arguments and set any appropriate calculated defaults.
    # The output directory. If not specified, then create one using the job_id.
    if job["arguments"]["output_directory_prefix"] is not None:
        prefix = "/" + str(prefix)
    if job["arguments"]["output"] is None:
        output_directory = pathlib.Path(os.getcwd() + prefix + "/" + job["id"])
    else:   
        output_directory = pathlib.Path(prefix + output)

    # Make the output directory, if it doesn't exist.
    if not output_directory.is_dir():
        output_directory.mkdir(parents=True, exist_ok=True)
        output_directory = pathlib.Path(output_directory)
        annotations_output_directory = output_directory / "annotations"
        annotations_output_directory.mkdir(parents=True, exist_ok=True)

    job["output"]["directory"] = output_directory
    job["log_file"] = job["output"]["directory"] / job["arguments"]["log_file"]
    job["job_file"] = job["output"]["directory"] / job["arguments"]["job_file"]

    # Make sure we have a directory for the output files
    assert job["output"]["directory"].is_dir(), log(
        job,
        "could not find the path {} for output files".format(
            str(job["output"]["directory"])
        ),
    )

    # Make sure we can write to the directory for the output files
    assert os.access(str(job["output"]["directory"]), os.W_OK), log(
        "could not write to path {} for output files".format(
            str(job["output"]["directory"])
        )
    )

    return job


def log(job, message):
    stamp = datetime.now()
    duration = str((stamp - job["time_start"]))
    line_header = "[{}] [+{}] [{}]".format(
        stamp.strftime("%Y-%m-%d %H:%M:%S"), duration, job["id"]
    )

    if job["arguments"]["debug"]:
        print("{}: {}".format(line_header, message))

    file1 = open(job["log_file"], "a")  # append mode
    file1.write("{}: {}\n".format(line_header, message))
    file1.close()


def log_object(object, line_identifier="+", header="", indent=4):
    print(type(object))
    return log_string(
        header + json.dumps(vars(object), indent=indent), line_identifier, indent
    )


def log_string(string, line_identifier="+", indent=4):
    new_line_string = "\n" + line_identifier + " " * indent
    return new_line_string + new_line_string.join(string.splitlines())
