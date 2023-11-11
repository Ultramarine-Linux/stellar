import os
import subprocess
import threading
# from gi.repository import Gtk, GObject
# Run payload in either the a chroot as a temporary script, or run directly on the host

def execute(payload: str):
    """
    This function accepts a string, and executes it as a script
    """
    # Check if there's an envar called STELLAR_CHROOT
    if os.environ.get("STELLAR_CHROOT"):
        print("Running in chroot...")
        chroot = os.environ.get("STELLAR_CHROOT")
        # first, check the string if there's a shebang

        pl = payload

        if not pl.startswith("#!"):
            # prepend shebang
            pl = "#!/bin/sh\n" + pl

        # Now, write the payload to a temporary file
        tmpfile = os.path.join(chroot, "tmp", "stellar-payload.sh")

        os.makedirs(os.path.dirname(tmpfile), exist_ok=True)

        with open(tmpfile, "w") as f:
            f.write(pl)

        # chmod +x the temporary file

        os.chmod(tmpfile, 0o755)

        # finally execute the script

        proc = subprocess.Popen(f"chroot {chroot} /tmp/stellar-payload.sh", shell=True)

        p = proc.wait()

        # remove the temporary file
        os.remove(tmpfile)
        

    else:
        print("Running on host...")
        # Run the payload directly on the host
        proc = subprocess.Popen(payload, shell=True)

        p = proc.wait()
        return p
