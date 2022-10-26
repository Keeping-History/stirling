# define Python user-defined exceptions
class StirlingError(Exception):
    """Base class for other exceptions"""
    pass


class FileOuputDirectoryError(StirlingError):
    """Raised when the output directory cannot be created, cannot be accessed or is not writable."""
    pass


class FileLogFileNotFound(StirlingError):
    """Raised when the Log File is not found"""
    pass


class ValueTooLargeError(StirlingError):
    """Raised when the input value is too large"""
    pass
