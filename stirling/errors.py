class StirlingError(Exception):
    """Base class for other exceptions"""

    pass


class MissingFrameworkError(StirlingError):
    """Raised when the framework requested for the job is not available."""

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


# Python standard exceptions:
# BaseException
#  +-- SystemExit
#  +-- KeyboardInterrupt
#  +-- GeneratorExit
#  +-- Exception
#       +-- StopIteration
#       +-- StandardError
#       |    +-- BufferError
#       |    +-- ArithmeticError
#       |    |    +-- FloatingPointError
#       |    |    +-- OverflowError
#       |    |    +-- ZeroDivisionError
#       |    +-- AssertionError
#       |    +-- AttributeError
#       |    +-- EnvironmentError
#       |    |    +-- IOError
#       |    |    +-- OSError
#       |    |         +-- WindowsError (Windows)
#       |    |         +-- VMSError (VMS)
#       |    +-- EOFError
#       |    +-- ImportError
#       |    +-- LookupError
#       |    |    +-- IndexError
#       |    |    +-- KeyError
#       |    +-- MemoryError
#       |    +-- NameError
#       |    |    +-- UnboundLocalError
#       |    +-- ReferenceError
#       |    +-- RuntimeError
#       |    |    +-- NotImplementedError
#       |    +-- SyntaxError
#       |    |    +-- IndentationError
#       |    |         +-- TabError
#       |    +-- SystemError
#       |    +-- TypeError
#       |    +-- ValueError
#       |         +-- UnicodeError
#       |              +-- UnicodeDecodeError
#       |              +-- UnicodeEncodeError
#       |              +-- UnicodeTranslateError
#       +-- Warning
#            +-- DeprecationWarning
#            +-- PendingDeprecationWarning
#            +-- RuntimeWarning
#            +-- SyntaxWarning
#            +-- UserWarning
#            +-- FutureWarning
#   +-- ImportWarning
#   +-- UnicodeWarning
#   +-- BytesWarning
#
