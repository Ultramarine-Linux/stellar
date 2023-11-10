# List of apps/presets to be installed

import os
import subprocess
import logging
from . import log
import gi
from . import gpu, util

gi.require_version("Gtk", "4.0")
# libadwaita
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio


class Script:
    def __init__(self, script):
        self.script = script

    def process(self):
        util.execute(self.script)


class Payload:
    # payload can be either, a script or a function that returns a boolean
    def __init__(self, payload):
        self.payload = payload

    def result(self):
        logging.debug(self.payload)
        if isinstance(self.payload, Script):
            self.payload.process()
        else:
            logging.debug("Payload is not a script")
            # check if payload is a function
            if callable(self.payload):
                logging.debug("Payload is a function")
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
            
    def __repr__(self):
        return f"Option(description={self.description}, option={self.option})"



class App:
    def __init__(
        self,
        name: str,
        description: str,
        payload: Payload,
        option: Option = None,
        category: str = None,
    ):
        self.name = name
        self.description = description
        self.payload = payload
        self.option = option
        self.category = category

        logging.debug(f"App {self.name} created")
        logging.debug(self.payload)

    def __repr__(self):
        return f"App(name={self.name}, description={self.description}, payload={self.payload}, option={self.option}, category={self.category})"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "payload": self.payload,
            "option": {
                "description": self.option.description,
                "option": self.option.option
            } if self.option else None,
            "category": self.category
        }

    def execute(self):
        self.payload.result()


apps = {
    "nvidia": App(
        name="NVIDIA Drivers",
        description="Install NVIDIA drivers",
        # Define payload, but don't run it yet
        payload=Payload(gpu.setup_nvidia),
        option=Option(description="Set NVIDIA GPU as primary GPU"),
        category="drivers",
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
                if [ "$STELLAR_OPTION" = "1" ]; then
                    sed -i '/PrefersNonDefaultGPU/d' /usr/share/steam/steam.desktop
                    sed -i '/X-KDE-RunOnDiscreteGpu/d' /usr/share/steam/steam.desktop
                fi
                """
            ),
        ),
        option=Option(description="Don't start with dedicated GPU (Optimus patch)"),
        category="apps",
    ),
    "chrome": App(
        name="Google Chrome",
        description="The Google Chrome web browser",
        payload=Payload(
            Script(
                """
                echo "Installing Google Chrome"
                cat <<EOF | sudo tee /etc/yum.repos.d/google-chrome.repo
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/\$basearch
enabled=1
gpgcheck=1
gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub
EOF
                sudo dnf install -y google-chrome-stable || true
                """
            )
        ),
        category="apps",
    ),
    "vscode": App(
        name="Visual Studio Code",
        description="The Visual Studio Code editor",
        payload=Payload(
            Script(
                """
                sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
                sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
                sudo dnf install -y code
                """
            )
        ),
        category="apps",
    ),
    "tailscale": App(
        name="Tailscale",
        description="The Tailscale VPN",
        payload=Payload(
            Script(
                """
                sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo
                sudo dnf install -y tailscale
                sudo systemctl enable tailscaled
                """
            )
        ),
        category="apps",
    ),
    "msedge": App(
        name="Microsoft Edge",
        description="Microsoft Edge web browser",
        payload=Payload(
            Script(
                """
                sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
                sudo dnf config-manager --add-repo https://packages.microsoft.com/yumrepos/edge
                sudo dnf install -y microsoft-edge-stable
                """
            )
        ),
        category="apps",
    ),
    "docker": App(
        name="Docker (Moby Engine)",
        description="Docker container engine",
        payload=Payload(
            Script(
                """
                sudo dnf install -y moby-engine moby-compose moby-buildx
                sudo systemctl enable docker.socket
                """
            )
        ),
        category="apps",
    ),
    "bottles": App(
        name="Bottles",
        description="Windows compatibility layer",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.usebottles.bottles || true
                """
            )
        ),
        category="apps",
    ),
    "sandbox-tools": App(
        name="Sandboxing Tools",
        description="Tools for sandboxing applications, such as Toolbx and Distrobox",
        payload=Payload(
            Script(
                """
                sudo dnf install -y toolbox distrobox
                """
            )
        ),
        category="apps",
    ),
    "fish": App(
        name="Fish",
        description="Fish shell",
        payload=Payload(
            Script(
                """
                sudo dnf install -y fish
                """
            )
        ),
        category="apps",
    ),
}


def test():
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
        self.tickbox.connect("toggled", self.on_tickbox_toggled)

        # add as suffix
        self.add_prefix(self.tickbox)

        # Prefix, for the feature flags
        self.option_toggle = Gtk.CheckButton()
        # set sensitive to whatever the tickbox status is by connecting it
        if app.option is not None:
            self.option_toggle.set_sensitive(app.option.option)
            self.option_toggle.set_active(app.option.option)
        else:
            self.option_toggle.set_sensitive(False)

        if app.option:
            self.option_toggle.set_active(app.option.option)

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

    def on_activate(self, _):
        logging.debug(f"Activating {self.app.name}")

    def on_tickbox_toggled(self, tickbox):
        self.option_toggle.set_sensitive(tickbox.get_active())
