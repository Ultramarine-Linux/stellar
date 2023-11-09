# List of apps/presets to be installed

import os
from . import gpu
import subprocess


import gi
from . import apps

gi.require_version("Gtk", "4.0")
# libadwaita
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

class Script:
    def __init__(self, script):
        self.script = script

    def process(self):
        subprocess.run(self.script, shell=True)


class Payload:
    # payload can be either, a script or a function that returns a boolean
    def __init__(self, payload):
        self.payload = payload

    def result(self):
        print(self.payload)
        if isinstance(self.payload, Script):
            self.payload.process()
        else:
            print("Payload is not a script")
            # check if payload is a function
            if callable(self.payload):
                print("Payload is a function")
                # Execute lambda function inside and return the result
                return self.payload()


class Option:
    # Binary option with description

    def __init__(self, description: str, option: bool = False):
        self.description = description
        self.option = option
        # set environment variable to true if option is selected
        if self.option:
            os.environ["STELLAR_OPTION"] = "1"
        else:
            os.environ["STELLAR_OPTION"] = "0"

    def set(self, option: bool):
        self.option = option
        if self.option:
            os.environ["STELLAR_OPTION"] = "1"
        else:
            os.environ["STELLAR_OPTION"] = "0"


class App:
    def __init__(
        self, name: str, description: str, payload: Payload, option: Option = None
    ):
        self.name = name
        self.description = description
        self.payload = payload
        self.option = option

        print(f"App {self.name} created")
        print(payload)

    def __repr__(self):
        return f"<App {self.name}>"

    def execute(self):
        self.payload.result()


apps = {
    "nvidia": App(
        name="NVIDIA Drivers",
        description="Install NVIDIA drivers",
        # Define payload, but don't run it yet
        payload=Payload(gpu.setup_nvidia),
        option=Option(description="Set NVIDIA GPU as primary GPU"),
    ),
    "steam": App(
        name="Steam",
        description="The Steam gaming platform",
        payload=Payload(
            Script(
                """
    echo "Installing Steam"
    echo "option=$STELLAR_OPTION"
    sudo dnf install -y steam
"""
            ),
        ),
        option=Option(description="Don't start with dedicated GPU (Optimus patch)"),
    ),
}


def main():
    # test: try to install steam
    apps["steam"].option.set(True)
    apps["steam"].execute()
    # apps["nvidia"].execute()


class AppEntry(Adw.ActionRow):
    def __init__(self, app: App, id: str):
        super().__init__()
        self.app = app
        self.appid = id
        self.set_title(app.name)
        self.set_subtitle(app.description)
        self.set_activatable(False)
        self.connect("activate", self.on_activate)

        # add tickbox to the right
        self.tickbox = Gtk.CheckButton()
        

        # add as suffix
        self.add_prefix(self.tickbox)

        # Prefix, for the feature flags
        self.option_toggle = Gtk.CheckButton()
        # set sensitive to whatever the tickbox status is by connecting it

        # Ideally, we should use a popover for the option toggle,
        # but I don't know how to do that yet
        if app.option:
            # add option toggle as suffix

            self.optionbox = Gtk.Box()
            # make it horizontal
            self.optionbox.set_orientation(Gtk.Orientation.HORIZONTAL)
            desc_label = Gtk.Label()
            # make text small
            desc_label.add_css_class("h6")
            desc_label.set_text(app.option.description)
            self.optionbox.append(desc_label)
            self.optionbox.append(self.option_toggle)
            self.add_suffix(self.optionbox)
            
            


    def on_activate(self, action_row):
        print(f"Activating {self.app.name}")
        pass