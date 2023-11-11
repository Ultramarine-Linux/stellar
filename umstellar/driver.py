# GPU detection and driver versioning module
from . import log
import logging
import os
import subprocess
import requests
from . import util

nvidia_prefixes = {
    # List of chipset prefixes with its corresponding last supported driver version
    # if it's not in the list, it's probably supported by the latest driver
    # but... if it's really really old, then you're out of luck
    # We're gonna be supporting GPUs from the 8000 series and up
    "NV": "unsupported",
    "MCP": "unsupported",
    "G7": "unsupported",
    "G8": "340xx",
    # wtf this goes from like 8000 to 100 series
    "G9": "340xx",
    # finally, a sane naming scheme
    # Tesla GPUs
    "GT": "340xx",
    # Fermi GPUs, in case you like burning your house down
    "GF": "390xx",
    # Kepler GPUs
    # now we're finally up to the modern era
    "GK": "470xx",
    # The rest should be supported by the latest driver, at least as of
    # late 2023
}


def get_nvidia_driver(chipset: str) -> str:
    """
    Returns the latest supported driver for the given chipset
    """
    for prefix, driver in nvidia_prefixes.items():
        if chipset.startswith(prefix):
            return driver
    return "latest"


# tests

assert get_nvidia_driver("NV34") == "unsupported"
assert get_nvidia_driver("GK104") == "470xx"
assert get_nvidia_driver("GP108") == "latest"
assert get_nvidia_driver("GK208") == "470xx"
assert get_nvidia_driver("GT218") == "340xx"


def check_internet_connection() -> bool:
    """
    Returns True if an internet connection is available
    """
    try:
        requests.get("https://ultramarine-linux.org")
        return True
    except requests.exceptions.ConnectionError:
        return False


def check_nvidia_gpu() -> bool:
    """
    Returns True if an Nvidia GPU is installed
    """
    # lspci | grep -q -i NVIDIA

    return subprocess.call("lspci | grep -q -i NVIDIA", shell=True) == 0


def get_nvidia_chipset() -> str:
    """
    Returns the chipset of the installed Nvidia GPU
    """
    # something with lspci and grep idk
    gpu = subprocess.getoutput(
        "lspci | grep -i NVIDIA | head -n 1 | cut -d ':' -f 3 | cut -d '[' -f 1 | sed -e 's/^[[:space:]]*//'",
    ).split()[-1]
    return gpu


def get_nvidia_packages() -> list[str]:
    """
    Returns a list of Nvidia packages to install
    """

    pkgs = ["nvidia-gpu-firmware", "libva-nvidia-driver"]
    chipset = get_nvidia_chipset()
    ver = get_nvidia_driver(chipset)

    if ver == "unsupported":
        logging.warning("Unsupported NVIDIA GPU detected, keeping nouveau drivers")
        return pkgs

    if ver == "latest":
        pkgs.extend(["akmod-nvidia", "xorg-x11-drv-nvidia", "xorg-x11-drv-nvidia-cuda"])
        return pkgs

    else:
        pkgs.extend(
            [
                f"akmod-nvidia-{ver}",
                f"xorg-x11-drv-nvidia-{ver}",
                f"xorg-x11-drv-nvidia-{ver}-cuda",
            ]
        )
        return pkgs


def check_ostree() -> bool:
    """
    Check whether the system is running on OSTree, or a normal RPM-based system

    Returns True if OSTree is detected
    """
    return os.path.exists("/ostree")


def setup_nvidia_ostree():
    # Set up Nvidia drivers while on RPM-OSTree
    pkgs = get_nvidia_packages()

    logging.info(f"Installing Nvidia packages: {pkgs}")

    args = ["rpm-ostree", "install", "-y"]

    args.extend(pkgs)

    command = " ".join(args)

    logging.info(f"Running command: {command}")

    util.execute(command)

    logging.info("Setting up OSTree kernel arguments")

    util.execute(
        "sudo rpm-ostree kargs --append=rd.driver.blacklist=nouveau --append=modprobe.blacklist=nouveau --append=nvidia-drm.modeset=1 initcall_blacklist=simpledrm_platform_driver_init"
    )

    logging.info("Complete! Please reboot to apply changes.")


def setup_nvidia(primary_gpu: bool = False):
    # Set to True anyway if STELLAR_OPTION is set to 1
    primary_gpu = False
    if "STELLAR_OPTION" in os.environ and os.environ["STELLAR_OPTION"] == "1":
        primary_gpu = True

    # Set up NVIDIA drivers, if applicable
    if not check_nvidia_gpu():
        logging.warning("No Nvidia GPU detected, skipping Nvidia driver setup")
        return

    if check_ostree():
        logging.info("OSTree detected, doing alternate Nvidia driver setup")
        setup_nvidia_ostree()
        return

    pkgs = get_nvidia_packages()

    logging.info(f"Installing Nvidia packages: {pkgs}")

    args = ["sudo", "dnf", "install", "-y", "--allowerasing", "--best"]
    args.extend(pkgs)

    logging.info(f"Running command: {args}")

    util.execute(" ".join(args))

    if primary_gpu:
        logging.info("Setting Nvidia GPU as primary GPU")
        util.execute(
            """
            sudo cp -p /usr/share/X11/xorg.conf.d/nvidia.conf /etc/X11/xorg.conf.d/nvidia.conf
            sudo sed -i '10i\\\tOption "PrimaryGPU" "yes"' /etc/X11/xorg.conf.d/nvidia.conf
            """,
        )



    


def nvidia_payload() -> bool:
    """
    Returns True if Nvidia GPU is installed
    """
    setup_nvidia()
    return True


# Broadcom Drivers

def check_broadcom_wifi() -> bool:
    """
    Returns True if a Broadcom wifi card is installed
    """
    # search if Network, and Broadcom are in the output of lspci

    return subprocess.call("lspci | grep -q -i Network | grep -q -i Broadcom", shell=True) == 0


def check_broadcom_bluetooth() -> bool:
    """
    Returns True if a Broadcom bluetooth card is installed
    """
    # search if Network, and Broadcom are in the output of lspci

    return subprocess.call("lspci | grep -q -i Bluetooth | grep -q -i Broadcom", shell=True) == 0


def setup_broadcom():
    if not check_broadcom_wifi():
        logging.warning("No Broadcom wifi card detected, skipping Broadcom driver setup")
        return
    else:
        logging.info("Broadcom wifi card detected, installing Broadcom wifi drivers")
        util.execute("sudo dnf install -y broadcom-wl akmod-wl")

    if not check_broadcom_bluetooth():
        logging.warning("No Broadcom bluetooth card detected, skipping Broadcom driver setup")
        return
    
    else:
        logging.info("Broadcom bluetooth card detected, installing Broadcom bluetooth drivers")
        util.execute("sudo dnf install -y broadcom-bt-firmware")




if __name__ == "__main__":
    if not check_internet_connection():
        logging.warning("No internet connection detected, skipping driver setup")
        exit(1)
    setup_nvidia()
    setup_broadcom()