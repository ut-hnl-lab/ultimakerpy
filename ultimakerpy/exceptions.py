class PrinterControlError(Exception):
    """Base exception for Ultimakerpy."""


class RequestError(PrinterControlError):
    """The URL does not exist or the request is not permitted."""


class FutureResultError(PrinterControlError):
    """The peration is not permitted in the state at the time."""


class RangeValidationError(PrinterControlError):
    """The given value is out of range."""


class ChoiceValidationError(PrinterControlError):
    """The given value is not a choice."""


class PrinterControlWarning(Warning):
    """Base warning for Ultimakerpy."""


class RequestModeWarning(PrinterControlWarning):
    """The request mode does not support the method."""


class PrintJobWarning(PrinterControlWarning):
    """The print job cannot be executed and is ignored."""
