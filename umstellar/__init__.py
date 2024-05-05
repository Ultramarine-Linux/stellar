import os, logging, typing
from . import util


# TODO: add app name into Payload for better progress tracking
class Payload:
    """Payload describes how a package can be installed."""

    priority: int = 0
    app: "App"

    def __init__(self, prio: int = 0):
        self.priority = prio

    def __call__(self):
        logging.warn(f"{self.__repr__()} has not implemented `__call__()`.")

    def set_app(self, app: "App"):
        self.app = app


class Option:
    """Binary option with description"""

    def __init__(self, description: str, option: bool = False):
        self.description = description
        self.option = option
        # set environment variable to true if option is selected
        if self.option:
            os.environ["STELLAR_OPTION"] = "1"
        else:
            os.environ["STELLAR_OPTION"] = "0"

    def set(self, option: bool | None = None):
        self.option = option or self.option
        if self.option:
            os.environ["STELLAR_OPTION"] = "1"
        else:
            os.environ["STELLAR_OPTION"] = "0"

    def __repr__(self):
        return f"Option(description={self.description}, option={self.option})"


class App:
    name: str
    description: str
    payloads: list[Payload]
    option: Option | None
    category: str | None

    def __init__(
        self,
        name: str,
        description: str,
        payloads: list[Payload],
        option: Option | None = None,
        category: str | None = None,
    ):
        self.name = name
        self.description = description
        self.payloads = payloads
        self.option = option
        self.category = category
        [p.set_app(self) for p in self.payloads]

        logging.debug(f"App {self.name} created")
        logging.debug(self.payloads)

    def __repr__(self):
        return f"App(name={self.name}, description={self.description}, payloads={self.payloads}, option={self.option}, category={self.category})"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "payloads": self.payloads,
            "option": {
                "description": self.option.description,
                "option": self.option.option,
            }
            if self.option
            else None,
            "category": self.category,
        }


class Dnf(Payload):
    """Represents installing a dnf5 package."""

    name: str

    def __init__(self, name: str, **kwargs):
        self.name = name
        Payload.__init__(self, **kwargs)

    def __call__(self):
        logging.warn(f"Dnf(name='{self.name}').__call__() should not be called.")


class DnfRm(Payload):
    """Represents removing a dnf5 package."""

    name: str

    def __init__(self, name: str, **kwargs):
        self.name = name
        Payload.__init__(self, **kwargs)

    def __call__(self):
        logging.warn(f"DnfRm(name='{self.name}').__call__() should not be called.")


class Flatpak(Payload):
    """Represents installing a Flatpak package."""

    name: str

    def __init__(self, name: str, **kwargs):
        self.name = name
        Payload.__init__(self, **kwargs)

    def __call__(self):
        logging.warn(f"Flatpak(name='{self.name}').__call__() should not be called.")


class Script(Payload):
    """A script. It is what it is."""

    script: str

    def __init__(self, script: str, **kwargs):
        self.script = script
        Payload.__init__(self, **kwargs)

    def __call__(self):
        if self.app.option is not None:
            self.app.option.set()
        util.execute(self.script)


class Procedure(Payload):
    """A Python function."""

    f: typing.Callable

    def __init__(self, f: typing.Callable, **kwargs):
        self.f = f
        Payload.__init__(self, **kwargs)

    def __call__(self):
        self.f()
