# define Python user-defined exceptions
class StirlingError(Exception):
    """Base class for other exceptions"""

    pass


class FileOutputDirectoryError(StirlingError):
    """Raised when the output directory cannot be created, cannot be accessed or is not writable."""

    pass


class FileLogFileNotFound(StirlingError):
    """Raised when the Log File is not found"""

    pass


class DependencyMissingError(StirlingError):
    """Raised when the Log File is not found"""

    pass


class DependencyMissingBinaryError(DependencyMissingError):
    """Raised when a binary dependency is missing."""

    pass


class ValueTooLargeError(StirlingError):
    """Raised when the input value is too large."""

    pass


class ValueTooSmallError(StirlingError):
    """Raised when the input value is too small."""

    pass


class ValueWrongTypeError(StirlingError):
    """Raised when the input value is too large"""

    pass


class CommandError(StirlingError):
    """Raised when the input value is too large"""

    pass


class DependencyMissingDownloadError(StirlingError):
    """Raised when the binary file could not be downloaded."""

    pass


class DependencyMissingPostProcessError(StirlingError):
    """Raised when the package containing the binary file could not be processed."""

    pass
