# Stellar (Stellar)

Stellar is a quick-and-dirty GUI post-install menu for Ultramarine Linux. It's written in Python and uses libadwaita for the UI.

We hacked this together in a few days, just in time for Ultramarine Linux 39 which happened to get delayed due to some major GNOME 45 porting issues. It's meant to only be used for Ultramarine Linux 39's Anaconda post-install menu.

## Why?

So, Ultramarine 39 is supposed to have a script that detects NVIDIA GPUs and installs the proprietary drivers. However, this script is implemented directly in a Kickstart file, which is... not ideal, and also _literally_ injected in using a Bash script, inside a heredoc. This is a terrible idea, and I (Cappy) wanted to improve it a little bit.

This script will be deprecated in the future when we implement our own OOBE (probably 41.) For now, it's a stopgap in our transitional OOBE (Readymade install -> Anaconda/DE OOBE -> Stellar)

## Running

To test Stellar, you'll need the following

- Python 3.11 (or newer)
- GTK 4.4 (or newer)
- libadwaita 1.0 (or newer)

And optionally, a chroot of Ultramarine Linux 39. You can use the following command to run Stellar:

```sh
export STELLAR_CHROOT=/path/to/chroot
python3 -m umstellar
```

## Naming

Stellar is named after Hoshimachi Suisei's hit track, [Stellar Stellar]. It's honestly a banger and you should listen to it.

[Stellar Stellar]: https://youtu.be/a51VH9BYzZA
