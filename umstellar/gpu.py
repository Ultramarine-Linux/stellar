# GPU detection and driver versioning module

import subprocess
import requests

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
        print("WARN: Unsupported NVIDIA GPU detected, keeping nouveau drivers")
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


def setup_nvidia(primary_gpu: bool = False):
    # Set up NVIDIA drivers, if applicable

    # Check if an internet connection is available

    if not check_internet_connection():
        print("No internet connection detected, skipping Nvidia driver setup")
        return

    if not check_nvidia_gpu():
        print("No Nvidia GPU detected, skipping Nvidia driver setup")
        return

    pkgs = get_nvidia_packages()

    print(f"Installing Nvidia packages: {pkgs}")

    args = ["sudo", "dnf", "install", "-y", "--allowerasing", "--best"]
    args.extend(pkgs)

    print(f"Running command: {args}")

    subprocess.run(args)

    if primary_gpu:
        print("Setting Nvidia GPU as primary GPU")
        subprocess.Popen(
            """
            sudo cp -p /usr/share/X11/xorg.conf.d/nvidia.conf /etc/X11/xorg.conf.d/nvidia.conf
            sudo sed -i '10i\        Option "PrimaryGPU" "yes"' /etc/X11/xorg.conf.d/nvidia.conf
            """,
            shell=True,
        )


if __name__ == "__main__":
    setup_nvidia()
