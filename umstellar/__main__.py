import gi
from . import gpu
gi.require_version('Gtk', '4.0')
# libadwaita
gi.require_version('Adw', '1')


def main():
    print("Hello world!")
    print(gpu.get_nvidia_chipset())

if __name__ == "__main__":
    main()