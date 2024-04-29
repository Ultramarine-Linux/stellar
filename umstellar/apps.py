# List of apps/presets to be installed

import os
import logging
from . import driver
import gi
from . import util

gi.require_version("Gtk", "4.0")
# libadwaita
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


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
        option: Option | None = None,
        category: str | None = None,
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
                "option": self.option.option,
            }
            if self.option
            else None,
            "category": self.category,
        }

    def execute(self):
        self.payload.result()


apps = {
    "nvidia": App(
        name="NVIDIA Drivers",
        description="Install NVIDIA drivers",
        # Define payload, but don't run it yet
        payload=Payload(driver.setup_nvidia),
        option=Option(description="Set NVIDIA GPU as primary GPU"),
        category="System"
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
                    sed -i '/PrefersNonDefaultGPU/d' /usr/share/applications/steam.desktop
                    sed -i '/X-KDE-RunOnDiscreteGpu/d' /usr/share/applications/steam.desktop
                fi
                """
            ),
        ),
        option=Option(description="Don't start with dedicated GPU (Optimus patch)"),
        category="Gaming",
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
                sudo dnf remove -y firefox
                sudo dnf install -y google-chrome-stable || true
                """
            )
        ),
        category="Browsers",
    ),
        "chromium": App(
        name="Chromium",
        description="Chrome without Google",
        payload=Payload(
            Script(
                """
                echo "Installing Chromium"
                sudo dnf remove -y firefox
                sudo dnf install -y chromium || true
                """
            )
        ),
        category="Browsers",
        ),
        "firefox": App(
        name="Firefox (Default)",
        description="Open-source web browser",
        payload=Payload(
            Script(
                """
                echo "Firefox already installed :3"
                """
            )
        ),
        category="Browsers",
        ),
        "epiphany": App(
        name="Web",
        description="A simple web browser for GNOME, AKA Epiphany",
        payload=Payload(
            Script(
                """
                echo "Installing Epiphany"
                sudo dnf remove -y firefox
                sudo dnf install -y epiphany || true
                """
            )
        ),
        category="Browsers",
        ),
    "vscode": App(
        name="Visual Studio Code",
        description="Our team's IDE of choice. Simple and versatile.",
        payload=Payload(
            Script(
                """
                sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
                sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
                sudo dnf install -y code
                """
            )
        ),
        category="Development",
    ),
       "codium": App(
        name="VSCodium",
        description="Visual Studio Code, without Microsoft",
        payload=Payload(
            Script(
                """
                sudo rpmkeys --import https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg
                printf "[gitlab.com_paulcarroty_vscodium_repo]\nname=download.vscodium.com\nbaseurl=https://download.vscodium.com/rpms/\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=1\ngpgkey=https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg\nmetadata_expire=1h" | sudo tee -a /etc/yum.repos.d/vscodium.repo
                sudo dnf install -y codium
                """
            )
        ),
        category="Development",
    ),
    "tailscale": App(
        name="Tailscale",
        description="VPN for simulating LAN",
        payload=Payload(
            Script(
                """
                sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo
                sudo dnf install -y tailscale
                sudo systemctl enable tailscale
                """
            )
        ),
         category="Development",
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
        category="Browsers",
    ),
    "geary": App(
        name="Geary",
        description="Simple email client",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.gnome.Geary
                """
            )
        ),
        category="Email Apps",
    ),
        "evolution": App(
        name="Evolution",
        description="Outlook-style email with calendaring and contacts",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.gnome.Evolution
                """
            )
        ),
        category="Email Apps",
    ),
        "thunderbird": App(
        name="Thunderbird",
        description="Open-source email, calendar, and chat tool. Made by the same team as Firefox",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.mozilla.Thunderbird
                """
            )
        ),
        category="Email Apps",
    ),
      "kontact": App(
        name="Kontact",
        description="Personal Information Manager for KDE",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.kde.kontact
                """
            )
        ),
        category="Email Apps",
    ),
    "gnome-terminal": App(
        name="GNOME Terminal",
        description="Default terminal for GNOME",
        payload=Payload(
            Script(
                """
                sudo dnf install -y gnome-terminal
                """
            )
        ),
        category="Terminals",
    ),
        "gnome-console": App(
        name="GNOME Console",
        description="Responsive terminal for GNOME",
        payload=Payload(
            Script(
                """
                sudo dnf install -y gnome-console
                """
            )
        ),
        category="Terminals",
    ),
        "konsole": App(
        name="Konsole",
        description="Default terminal for KDE",
        payload=Payload(
            Script(
                """
                sudo dnf install -y konsole
                """
            )
        ),
        category="Terminals",
    ),
        "terminator": App(
        name="Terminator",
        description="Tiling terminal",
        payload=Payload(
            Script(
                """
                sudo dnf install -y terminator
                """
            )
        ),
        category="Terminals",
    ),
            "warp": App(
        name="Warp",
        description="Modern terminal with quality of life tweaks and AI features. A favourite of our team. x86 only!",
        payload=Payload(
            Script(
                """
                sudo tee /etc/yum.repos.d/warpdotdev.repo
                [warpdotdev]
                name=warpdotdev
                baseurl=https://releases.warp.dev/linux/rpm/stable
                enabled=1
                gpgcheck=1
                gpgkey=https://releases.warp.dev/linux/keys/warp.asc
                sudo dnf install -y warp
                """
            )
        ),
        category="Terminals",
    ),
            "libreoffice": App(
        name="LibreOffice (Default)",
        description="Open-source office suite. Compatible with Microsoft Office.",
        payload=Payload(
            Script(
                """
                echo "LibreOffice already installed :3"
                """
            )
        ),
        category="Productivity",
    ),
            "onlyoffice": App(
        name="OnlyOffice",
        description="Office suite designed to replicate Microsoft Office. Includes collaboration features if you host your own server.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.onlyoffice.desktopeditors
                """
            )
        ),
        category="Productivity",
                    ),
            "notejot": App(
        name="Notejot",
        description="Simple notes app, developed by a team member.",
        payload=Payload(
            Script(
                """
                echo "We love you Lains"
                flatpak install -y flathub io.github.lainsce.Notejot
                """
            )
        ),
        category="Productivity",
                    ),
           "rnote": App(
        name="Rnote",
        description="A team favourite. Handwritten notes and simple drawings.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.github.flxzt.rnote
                """
            )
        ),
        category="Productivity",
                    ),
           "gimp": App(
        name="GIMP",
        description="Photoshop-like image editor.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.gimp.GIMP
                """
            )
        ),
        category="Photos and Art",
                    ),
           "krita": App(
        name="Krita",
        description="Powerful drawing software.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.kde.krita
                """
            )
        ),
        category="Photos and Art",
                    ),
           "inkscape": App(
        name="Inkscape",
        description="Illustrator-style vector editor.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.inkscape.Inkscape
                """
            )
        ),
        category="Photos and Art",
                    ),
           "wacom": App(
        name="Wacom Support",
        description="Support for Wacom tablets and platforms.",
        payload=Payload(
            Script(
                """
                echo "Already installed :p"
                """
            )
        ),
        category="Photos and Art",
                    ),
           "obs": App(
        name="OBS Studio",
        description="Industry standard recording and broadcasting software.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.obsproject.Studio
                """
            )
        ),
        category="Video",

                    ),
           "vlc": App(
        name="VLC",
        description="Versatile media player.",
        payload=Payload(
            Script(
                """
                sudo dnf install -y vlc
                """
            )
        ),
        category="Video",

                    ),
           "kdenlive": App(
        name="Kdenlive",
        description="Open-source video editor.",
        payload=Payload(
            Script(
                """
                sudo dnf install -y kdenlive
                """
            )
        ),
        category="Video",
           ),
           "kicad": App(
        name="KiCad",
        description="Schematic and circuit board design software.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.kicad.KiCad
                """
            )
        ),
        category="Makers",
           ),
          "cura": App(
        name="UltiMaker Cura",
        description="Slicer for 3D Printing Projects.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.ultimaker.cura
                """
            )
        ),
        category="Makers",
           ),
          "arduino": App(
        name="Arduino IDE v2",
        description="IDE and tools for Arduino (and similar) devices.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub cc.arduino.IDE2
                """
            )
        ),
        category="Makers",
           ),
         "rpi-imager": App(
        name="Raspberry Pi Imager",
        description="Tool to write OS images for Raspberry Pi.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.raspberrypi.rpi-imager
                """
            )
        ),
        category="Makers",
           ),
         "vboot-utils": App(
        name="Depthcharge Utilities",
        description="Utilities and configuration for ChromeOS' depthcharge.",
        payload=Payload(
            Script(
                """
                sudo dnf install -y vboot-utils
                """
            )
        ),
        category="Hardware",
           ),
         "adb": App(
        name="Android Tools",
        description="Tools for Android and Fastboot debugging.",
        payload=Payload(
            Script(
                """
                sudo dnf install -y android-tools
                """
            )
        ),
        category="Hardware",
           ),
         "prism-launcher": App(
        name="Prism Launcher",
        description="Advanced Minecraft launcher with easy mod support.",
        payload=Payload(
            Script(
                """
                sudo dnf install -y prism-launcher
                """
            )
        ),
        category="Gaming",
           ),
         "heroic": App(
        name="Heroic Games Launcher",
        description="Launcher for the Epic Games Store.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.heroicgameslauncher.hgl
                """
            )
        ),
        category="Gaming",
           ),
         "minecraft": App(
        name="Minecraft Launcher",
        description="The official Minecraft launcher.",
        payload=Payload(
            Script(
                """
                sudo dmf install -y minecraft-launcher
                """
            )
        ),
        category="Gaming",
           ),
         "discord": App(
        name="Discord",
        description="Chat and Voice for Gamers",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.discordapp.Discord
                """
            )
        ),
        category="Communication",
           ),
         "discord-ptb": App(
        name="Discord PTB",
        description="Chat and Voice for Gamers",
        payload=Payload(
            Script(
                """
                sudo yum install -y discord-ptb
                """
            )
        ),
        category="Communication",
           ),
         "discord-canary": App(
        name="Discord Canary",
        description="Chat and Voice for Gamers",
        payload=Payload(
            Script(
                """
                sudo yum install -y discord-canary
                """
            )
        ),
        category="Communication",
           ),
         "armcord": App(
        name="Armcord",
        description="Lightweight Discord client",
        payload=Payload(
            Script(
                """
                sudo yum install -y armcord
                """
            )
        ),
        category="Communication",
           ),
         "vesktop": App(
        name="Vencord Desktop (Vesktop)",
        description="Discord with Vencord preinstalled",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub dev.vencord.Vesktop
                """
            )
        ),
        category="Communication",
           ),
         "element": App(
        name="Element",
        description="Official Matrix Client",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub im.riot.Riot
                """
            )
        ),
        category="Communication",
           ),
         "signal": App(
        name="Signal Desktop",
        description="Truly private messaging. Requires a phone! x86 only!",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.signal.Signal
                """
            )
        ),
        category="Communication",
           ),
         "telegram": App(
        name="Telegram",
        description="Simple and expressive messaging.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.telegram.desktop
                """
            )
        ),
        category="Communication",
           ),
         "slack": App(
        name="Slack",
        description="Chat for Enterprises.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub com.slack.Slack
                """
            )
        ),
        category="Communication",
           ),
         "polari": App(
        name="Polari",
        description="IRC Client for GNOME.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.gnome.Polari
                """
            )
        ),
        category="Communication",
           ),
         "konversation": App(
        name="Konversation",
        description="IRC Client for KDE.",
        payload=Payload(
            Script(
                """
                flatpak install -y flathub org.kde.konversation
                """
            )
        ),
        category="Communication",
           ),
    "docker": App(
        name="Docker",
        description="Docker container engine",
        payload=Payload(
            Script(
                """
                sudo dnf install -y moby-engine moby-compose moby-buildx
                sudo systemctl enable docker.socket
                """
            )
        ),
         category="Development",
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
        category="Gaming",
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
        # category="apps",
    ),
    "fish": App(
        name="Fish Shell",
        description="Fish shell",
        payload=Payload(
            Script(
                """
                sudo dnf install -y fish
                """
            )
        ),
         category="System",
    ),
    "nushell": App(
        name="Nushell",
        description="Nushell shell",
        payload=Payload(
            Script(
                """
                sudo dnf install -y nushell
                """
            )
        ),
         category="System",
    ),
    "waydroid": App(
        name="Waydroid",
        description="Linux subsystem for Android, powered by Wayland and LXC (Does not work on X11 and NVIDIA GPUs)",
        payload=Payload(
            Script(
                """
                sudo dnf install -y waydroid
                """
            )
        ),
         category="System"
    ),
    "flatpak-warehouse": App(
        name="Warehouse",
        description="Graphical Flatpak manager",
        payload=Payload(
            Script(
                """
                sudo flatpak install -y flathub io.github.flattool.Warehouse || true
                """
            )
        ),
    ),
    "1password": App(
        name="1Password",
        description="1Password password manager",
        option=Option(description="Also install 1Password CLI"),
        category="apps",
        payload=Payload(
            Script(
                """
                rpm --import https://downloads.1password.com/linux/keys/1password.asc
                sh -c 'echo -e "[1password]\nname=1Password Stable Channel\nbaseurl=https://downloads.1password.com/linux/rpm/stable/\$basearch\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=1\ngpgkey=\"https://downloads.1password.com/linux/keys/1password.asc\"" > /etc/yum.repos.d/1password.repo'
                sudo dnf install -y 1password

                if [ "$STELLAR_OPTION" = "1" ]; then
                    sudo dnf install -y 1password-cli
                fi
                """
            )
        ),
    ),
    "broadcom": App(
        name="Broadcom Drivers",
        description="Broadcom wifi and bluetooth drivers",
        payload=Payload(driver.setup_broadcom),
        category="drivers",
    ),
    "v4l2loopback": App(
        name="v4l2loopback",
        description="Virtual webcam and video loopback driver",
        payload=Payload(
            Script(
                """
                sudo dnf install -y akmod-v4l2loopback
                """
            )
        ),
        category="drivers",
    ),
    "crystalhd": App(
        name="Crystal HD",
        description="Broadcom Crystal HD video decoder driver",
        payload=Payload(
            Script(
                """
                sudo dnf install -y akmod-crystalhd
                """
            )
        ),
        category="drivers",
    ),
    "intel-ipu6": App(
        name="Intel IPU6 Drivers",
        description="Intel IPU6 component for MIPI camera support on Intel Tiger Lake, Alder Lake, and beyond",
        payload=Payload(
            Script(
                """
                sudo dnf install -y akmod-intel-ipu6
                """
            )
        ),
        category="drivers",
    ),
    "prismlauncher": App(
        name="Prism Launcher",
        description="Advanced Minecraft: Java Edition launcher",
        payload=Payload(
            Script(
                """
                if [ "$STELLAR_OPTION" = "1" ]; then
                    flatpak install -y flathub org.prismlauncher.PrismLauncher || true
                else
                    sudo dnf install -y prismlauncher
                fi
                """
            )
        ),
        category="apps",
        option=Option(description="Install as flatpak (Removes system Java dependency)"),
    )
}


category_icons = {
    "drivers": "application-x-firmware-symbolic",
    "apps": "system-software-install",
    "Utilities": "emoji-symbols",
    "browser": "system-globe-alt2-symbolic",
    "development": "code-symbolic",
    "email apps": "mail-symbolic",
    "gaming": "gamepad2-symbolic,",
    "Productivity": "open-book-symbolic",
    "system": "processor-symbolic",
    "terminals": "terminal-symbolic"
}


def test():
    # test: try to install steam
    assert apps["steam"].option
    apps["steam"].option.set(True)
    apps["steam"].execute()
    # apps["nvidia"].execute()


class AppEntry(Adw.ExpanderRow):
    def __init__(self, app: App, id: str):
        super().__init__(enable_expansion=False)
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

        if not app.option:
            # hide enable expansion button if there's no option
            self.set_show_enable_switch(False)

        if app.option:
            # Prefix, for the feature flags
            # set sensitive to whatever the tickbox status is by connecting it
            act = app.option.option
            self.option_toggle = Gtk.CheckButton(
                # sensitive=act, active=act,
                margin_start=10,
                margin_end=10,
                margin_bottom=5,
                margin_top=5,
            )

            # add option toggle as suffix
            self.optionbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self.desc_label = Gtk.Label(
                css_classes=["h4"], label=app.option.description
            )
            self.optionbox.append(self.option_toggle)
            self.optionbox.append(self.desc_label)
            self.add_row(self.optionbox)

    def on_activate(self, _):
        logging.debug(f"Activating {self.app.name}")

    def on_tickbox_toggled(self, tickbox):
        if self.app.option:
            self.set_enable_expansion(self.tickbox.get_active())
