# List of apps/presets to be installed

import os
import logging
from . import driver
import gi
from gi.repository import Gtk, Adw
from . import App, Option, Procedure, Script, Dnf, DnfRm, Flatpak

gi.require_version("Gtk", "4.0")
# libadwaita
gi.require_version("Adw", "1")


apps = {
    "nvidia": App(
        name="NVIDIA Drivers",
        description="Install NVIDIA drivers",
        # Define payload, but don't run it yet
        payloads=[Procedure(driver.setup_nvidia)],
        option=Option(description="Set NVIDIA GPU as primary GPU"),
        category="System",
    ),
    "steam": App(
        name="Steam",
        description="The Steam gaming platform",
        payloads=[
            Dnf("steam"),
            Script(
                """
                if [ "$STELLAR_OPTION" = "1" ]; then
                    sed -i '/PrefersNonDefaultGPU/d' /usr/share/applications/steam.desktop
                    sed -i '/X-KDE-RunOnDiscreteGpu/d' /usr/share/applications/steam.desktop
                fi
                """
            ),
        ],
        option=Option(description="Don't start with dedicated GPU (Optimus patch)"),
        category="Gaming",
    ),
    "chrome": App(
        name="Google Chrome",
        description="The Google Chrome web browser",
        payloads=[
            Script(
                """
                echo "Installing Google Chrome"
                cat <<EOF | sudo tee /etc/yum.repos.d/google-chrome.repo
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/\\$basearch
enabled=1
gpgcheck=1
gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub
EOF""",
                prio=-10,
            ),
            DnfRm("firefox"),
            Dnf("google-chrome-stable"),
        ],
        category="Browsers",
    ),
    "chromium": App(
        name="Chromium",
        description="Chrome without Google",
        payloads=[
            DnfRm("firefox"),
            Dnf("chromium"),
        ],
        category="Browsers",
    ),
    "firefox": App(
        name="Firefox (Default)",
        description="Open-source web browser",
        payloads=[],  # Firefox is installed by default
        category="Browsers",
    ),
    "epiphany": App(
        name="Web",
        description="A simple web browser for GNOME, AKA Epiphany",
        payloads=[
            DnfRm("firefox"),
            Dnf("epiphany"),
        ],
        category="Browsers",
    ),
    "vscode": App(
        name="Visual Studio Code",
        description="Our team's IDE of choice. Simple and versatile.",
        payloads=[
            Script(
                """
                sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
                sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
                """,
                prio=-10,
            ),
            Dnf("code"),
        ],
        category="Development",
    ),
    "codium": App(
        name="VSCodium",
        description="Visual Studio Code, without Microsoft",
        payloads=[
            Script(
                """
                sudo rpmkeys --import https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg
                printf "[gitlab.com_paulcarroty_vscodium_repo]\nname=download.vscodium.com\nbaseurl=https://download.vscodium.com/rpms/\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=1\ngpgkey=https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg\nmetadata_expire=1h" | sudo tee -a /etc/yum.repos.d/vscodium.repo
                """,
                prio=-10,
            ),
            Dnf("codium"),
        ],
        category="Development",
    ),
    "tailscale": App(
        name="Tailscale",
        description="VPN for simulating LAN",
        payloads=[
            Script(
                """
                sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo
                """,
                prio=-10,
            ),
            Dnf("tailscale"),
            Script("sudo systemctl enable tailscale", prio=1),
        ],
        category="Development",
    ),
    "msedge": App(
        name="Microsoft Edge",
        description="Microsoft Edge web browser",
        payloads=[
            Script(
                """
                sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
                sudo dnf config-manager --add-repo https://packages.microsoft.com/yumrepos/edge
                """,
                prio=-10,
            ),
            Dnf("microsoft-edge-stable"),
        ],
        category="Browsers",
    ),
    "geary": App(
        name="Geary",
        description="Simple email client",
        payloads=[Flatpak("org.gnome.Geary")],
        category="Email Apps",
    ),
    "evolution": App(
        name="Evolution",
        description="Outlook-style email with calendaring and contacts",
        payloads=[Flatpak("org.gnome.Evolution")],
        category="Email Apps",
    ),
    "thunderbird": App(
        name="Thunderbird",
        description="Open-source email, calendar, and chat tool. Made by the same team as Firefox",
        payloads=[Flatpak("org.mozilla.Thunderbird")],
        category="Email Apps",
    ),
    "kontact": App(
        name="Kontact",
        description="Personal Information Manager for KDE",
        payloads=[Flatpak("org.kde.kontact")],
        category="Email Apps",
    ),
    "gnome-terminal": App(
        name="GNOME Terminal",
        description="Default terminal for GNOME",
        payloads=[Dnf("gnome-terminal")],
        category="Terminals",
    ),
    "gnome-console": App(
        name="GNOME Console",
        description="Responsive terminal for GNOME",
        payloads=[Dnf("gnome-console")],
        category="Terminals",
    ),
    "konsole": App(
        name="Konsole",
        description="Default terminal for KDE",
        payloads=[Dnf("konsole")],
        category="Terminals",
    ),
    "terminator": App(
        name="Terminator",
        description="Tiling terminal",
        payloads=[Dnf("terminator")],
        category="Terminals",
    ),
    "warp": App(
        name="Warp",
        description="Modern terminal with quality of life tweaks and AI features. A favourite of our team. x86 only!",
        payloads=[
            Script(
                """
                sudo tee /etc/yum.repos.d/warpdotdev.repo
                [warpdotdev]
                name=warpdotdev
                baseurl=https://releases.warp.dev/linux/rpm/stable
                enabled=1
                gpgcheck=1
                gpgkey=https://releases.warp.dev/linux/keys/warp.asc
                """,
                prio=-10,
            ),
            Dnf("warp"),
        ],
        category="Terminals",
    ),
    "libreoffice": App(
        name="LibreOffice (Default)",
        description="Open-source office suite. Compatible with Microsoft Office.",
        payloads=[],  # libreoffice already installed :3
        category="Productivity",
    ),
    "onlyoffice": App(
        name="OnlyOffice",
        description="Office suite designed to replicate Microsoft Office. Includes collaboration features if you host your own server.",
        payloads=[Flatpak("org.onlyoffice.desktopeditors")],
        category="Productivity",
    ),
    "notejot": App(
        name="Notejot",
        description="Simple notes app, developed by a team member.",
        payloads=[
            Flatpak("io.github.lainsce.Notejot"),
            Script('echo "We love you Lains"'),
        ],
        category="Productivity",
    ),
    "rnote": App(
        name="Rnote",
        description="A team favourite. Handwritten notes and simple drawings.",
        payloads=[Flatpak("com.github.flxzt.rnote")],
        category="Productivity",
    ),
    "gimp": App(
        name="GIMP",
        description="Photoshop-like image editor.",
        payloads=[Flatpak("org.gimp.GIMP")],
        category="Photos and Art",
    ),
    "krita": App(
        name="Krita",
        description="Powerful drawing software.",
        payloads=[Flatpak("org.kde.krita")],
        category="Photos and Art",
    ),
    "inkscape": App(
        name="Inkscape",
        description="Illustrator-style vector editor.",
        payloads=[Flatpak("org.inkscape.Inkscape")],
        category="Photos and Art",
    ),
    "wacom": App(
        name="Wacom Support",
        description="Support for Wacom tablets and platforms.",
        payloads=[],  # already installed
        category="Photos and Art",
    ),
    "obs": App(
        name="OBS Studio",
        description="Industry standard recording and broadcasting software.",
        payloads=[Flatpak("com.obsproject.Studio")],
        category="Video",
    ),
    "vlc": App(
        name="VLC",
        description="Versatile media player.",
        payloads=[Dnf("vlc")],
        category="Video",
    ),
    "kdenlive": App(
        name="Kdenlive",
        description="Open-source video editor.",
        payloads=[Dnf("kdenlive")],
        category="Video",
    ),
    "kicad": App(
        name="KiCad",
        description="Schematic and circuit board design software.",
        payloads=[Flatpak("org.kicad.KiCad")],
        category="Makers",
    ),
    "cura": App(
        name="UltiMaker Cura",
        description="Slicer for 3D Printing Projects.",
        payloads=[Flatpak("com.ultimaker.cura")],
        category="Makers",
    ),
    "arduino": App(
        name="Arduino IDE v2",
        description="IDE and tools for Arduino (and similar) devices.",
        payloads=[Flatpak("cc.arduino.IDE2")],
        category="Makers",
    ),
    "rpi-imager": App(
        name="Raspberry Pi Imager",
        description="Tool to write OS images for Raspberry Pi.",
        payloads=[Flatpak("org.raspberrypi.rpi-imager")],
        category="Makers",
    ),
    "vboot-utils": App(
        name="Depthcharge Utilities",
        description="Utilities and configuration for ChromeOS' depthcharge.",
        payloads=[Dnf("vboot-utils")],
        category="Hardware",
    ),
    "adb": App(
        name="Android Tools",
        description="Tools for Android and Fastboot debugging.",
        payloads=[Dnf("android-tools")],
        category="Hardware",
    ),
    "prism-launcher": App(
        name="Prism Launcher",
        description="Advanced Minecraft launcher with easy mod support.",
        payloads=[Dnf("prism-launcher")],
        category="Gaming",
    ),
    "heroic": App(
        name="Heroic Games Launcher",
        description="Launcher for the Epic Games Store.",
        payloads=[Flatpak("com.heroicgameslauncher.hgl")],
        category="Gaming",
    ),
    "minecraft": App(
        name="Minecraft Launcher",
        description="The official Minecraft launcher.",
        payloads=[Dnf("minecraft-launcher")],
        category="Gaming",
    ),
    "discord": App(
        name="Discord",
        description="Chat and Voice for Gamers",
        payloads=[Flatpak("com.discordapp.Discord")],
        category="Communication",
    ),
    "discord-ptb": App(
        name="Discord PTB",
        description="Chat and Voice for Gamers",
        payloads=[Dnf("discord-ptb")],
        category="Communication",
    ),
    "discord-canary": App(
        name="Discord Canary",
        description="Chat and Voice for Gamers",
        payloads=[Dnf("discord-canary")],
        category="Communication",
    ),
    "armcord": App(
        name="Armcord",
        description="Lightweight Discord client",
        payloads=[Dnf("armcord")],
        category="Communication",
    ),
    "vesktop": App(
        name="Vencord Desktop (Vesktop)",
        description="Discord with Vencord preinstalled",
        payloads=[Flatpak("dev.vencord.Vesktop")],
        category="Communication",
    ),
    "element": App(
        name="Element",
        description="Official Matrix Client",
        payloads=[Flatpak("im.riot.Riot")],
        category="Communication",
    ),
    "signal": App(
        name="Signal Desktop",
        description="Truly private messaging. Requires a phone! x86 only!",
        payloads=[Flatpak("org.signal.Signal")],
        category="Communication",
    ),
    "telegram": App(
        name="Telegram",
        description="Simple and expressive messaging.",
        payloads=[Flatpak("org.telegram.desktop")],
        category="Communication",
    ),
    "slack": App(
        name="Slack",
        description="Chat for Enterprises.",
        payloads=[Flatpak("com.slack.Slack")],
        category="Communication",
    ),
    "polari": App(
        name="Polari",
        description="IRC Client for GNOME.",
        payloads=[Flatpak("org.gnome.Polari")],
        category="Communication",
    ),
    "konversation": App(
        name="Konversation",
        description="IRC Client for KDE.",
        payloads=[Flatpak("org.kde.konversation")],
        category="Communication",
    ),
    "docker": App(
        name="Docker",
        description="Docker container engine",
        payloads=[Dnf("moby-engine"), Dnf("moby-compose"), Dnf("moby-buildx")],
        category="Development",
    ),
    "bottles": App(
        name="Bottles",
        description="Windows compatibility layer",
        payloads=[Flatpak("com.usebottles.bottles")],
        category="Gaming",
    ),
    "sandbox-tools": App(
        name="Sandboxing Tools",
        description="Tools for sandboxing applications, such as Toolbx and Distrobox",
        payloads=[Dnf("distrobox"), Dnf("toolbox")],
        # category="apps",
    ),
    "fish": App(
        name="Fish Shell",
        description="Fish shell",
        payloads=[Dnf("fish")],
        category="System",
    ),
    "nushell": App(
        name="Nushell",
        description="Nushell shell",
        payloads=[Dnf("nushell")],
        category="System",
    ),
    "waydroid": App(
        name="Waydroid",
        description="Linux subsystem for Android, powered by Wayland and LXC (Does not work on X11 and NVIDIA GPUs)",
        payloads=[Dnf("waydroid")],
        category="System",
    ),
    "flatpak-warehouse": App(
        name="Warehouse",
        description="Graphical Flatpak manager",
        payloads=[Flatpak("io.github.flattool.Warehouse")],
    ),
    "1password": App(
        name="1Password",
        description="1Password password manager",
        option=Option(description="Also install 1Password CLI"),
        category="apps",
        payloads=[
            Script(
                """
                rpm --import https://downloads.1password.com/linux/keys/1password.asc
                sh -c 'echo -e "[1password]\nname=1Password Stable Channel\nbaseurl=https://downloads.1password.com/linux/rpm/stable/\$basearch\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=1\ngpgkey=\"https://downloads.1password.com/linux/keys/1password.asc\"" > /etc/yum.repos.d/1password.repo'
                """,
                prio=-10,
            ),
            Dnf("1password"),
            Script("""
                if [ "$STELLAR_OPTION" = "1" ]; then
                    sudo dnf install -y 1password-cli
                fi
                """),
        ],
    ),
    "broadcom": App(
        name="Broadcom Drivers",
        description="Broadcom wifi and bluetooth drivers",
        payloads=[Procedure(driver.setup_broadcom)],
        category="drivers",
    ),
    "v4l2loopback": App(
        name="v4l2loopback",
        description="Virtual webcam and video loopback driver",
        payloads=[Dnf("akmod-v4l2loopback")],
        category="drivers",
    ),
    "crystalhd": App(
        name="Crystal HD",
        description="Broadcom Crystal HD video decoder driver",
        payloads=[Dnf("akmod-crystalhd")],
        category="drivers",
    ),
    "intel-ipu6": App(
        name="Intel IPU6 Drivers",
        description="Intel IPU6 component for MIPI camera support on Intel Tiger Lake, Alder Lake, and beyond",
        payloads=[Dnf("akmod-intel-ipu6")],
        category="drivers",
    ),
    "prismlauncher": App(
        name="Prism Launcher",
        description="Advanced Minecraft: Java Edition launcher",
        payloads=[
            Script(
                """
                if [ "$STELLAR_OPTION" = "1" ]; then
                    flatpak install -y flathub org.prismlauncher.PrismLauncher || true
                else
                    sudo dnf install -y prismlauncher
                fi
                """
            )
        ],
        category="apps",
        option=Option(
            description="Install as flatpak (Removes system Java dependency)"
        ),
    ),
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
    "terminals": "terminal-symbolic",
}


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
