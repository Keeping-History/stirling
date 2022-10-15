import shutil
import uuid

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




def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
