from . import validation
from .exceptions import MissingValueError, ValidationError

class Param:
    def __init__(self, checker, desc='', default=None, required=False):
        self.checker = validation.get_checker(checker)
        self.default = default
        self.desc = desc
        self.required = required

    def __str__(self):

        result = ""

        if self.required:
            result += "[Required] "

        if self.default is not None:
            result += f"[default={self.default}] "

        result += f"{self.checker.help()}"

        if len(self.desc):
            result += ": " + self.desc

        return result

    def __repr__(self):
        return str(self)

    def validate(self, value):
        if value is None and self.required:
            raise MissingValueError()
        try:
            return self.checker.check(value)
        except Exception:
            raise ValidationError()

