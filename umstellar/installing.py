# WARN: horrible code incoming
# This piece of progress bar + parallel install thingy is made by mado in something like a day.
# No time has been wasted on things like refactoring stuff. I don't care, and I can't be bothered.
# Don't blame me for the abusive use of global variables, poor logics and lack of error handling.
# I have no idea why everyone else in my team is a deadline fighter and no one has the intention
# to even attempt to meet deadlines.
import logging
import multiprocessing as mp
import os
import sys
import time
from contextlib import suppress
from multiprocessing import Process, Queue
from subprocess import PIPE, Popen
from threading import Thread
from typing import IO, Callable, Iterable

from gi.repository import GLib, Gtk

from . import App, Dnf, DnfRm, Flatpak, Payload, Procedure

job = mp.Value("i", 0)
total_jobs = 0
state = mp.Value("i", 0)
PROC = 1
SCRIPT = 2
DNFRM = 3
DNFIN = 4
DNFDL = 6
FLATPAK = 5
before_dnf = 0
dnf_total = 0


class InstallProgressWindow(Gtk.ApplicationWindow):
    lbl = Gtk.Label(label="Test Label")
    progress = Gtk.ProgressBar(hexpand=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 600)
        # self.header_bar = Adw.HeaderBar()
        # self.header_bar.set_show_end_title_buttons(False)
        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            vexpand=False,
            hexpand=True,
            margin_top=25,
            margin_end=25,
            margin_start=25,
            margin_bottom=25,
        )
        self.box.append(self.lbl)
        self.box.append(self.progress)
        self.set_child(self.box)
        self.th = Thread(target=self.th_update_progress)
        self.th.daemon = True
        self.th.start()

    def th_update_progress(self):
        while job.value != total_jobs:
            GLib.idle_add(self.update_progress, job.value)
            time.sleep(0.1)

    def update_progress(self, value: float):
        self.progress.set_fraction(value)
        self.lbl.set_text(self.determine_state())
        return False

    def determine_state(self) -> str:
        global state, job, total_jobs, PROC, SCRIPT, DNFRM, DNFIN, DNFDL, FLATPAK
        match state.value:
            case PROC:
                return f"[{job.value}/{total_jobs}] Running function"
            case SCRIPT:
                return f"[{job.value}/{total_jobs}] Running script"
            case DNFRM:
                return f"[{job.value}/{total_jobs}] Removing packages"
            case DNFIN:
                return f"[{job.value}/{total_jobs}] Installing RPM packages"
            case DNFDL:
                return f"[{job.value}/{total_jobs}] Downloading RPM packages"
            case FLATPAK:
                return f"[{job.value}/{total_jobs}] Installing Flatpak packages"
            case _:
                logging.warn(f"Unknown state.value: {state.value}")


def gather[T: Payload](cls: type[T], apps: dict[str, App]) -> list[T]:
    return [
        payload
        for app in apps.values()
        for payload in app.payloads
        if isinstance(payload, cls)
    ]


def process_installs(apps: dict[str, App]):
    global total_jobs
    total_jobs = len(apps) + len(gather(Dnf, apps))
    p = mp.Process(target=install, args=(apps))
    p.start()
    gui = InstallProgressWindow()
    gui.present()
    p.join()
    gui.th.join()


def install(apps: dict[str, App]):
    global job, state
    dnfrms = gather(DnfRm, apps)
    dnfs = gather(Dnf, apps)
    flatpaks = gather(Flatpak, apps)
    run_special_payloads(apps, lambda payload: payload.priority < 0)
    # WARN: dnf/5 is a giant mess and it will fail
    # somehow someone here please do some proper error handling or sth
    # I don't really know like… how exactly we should do it, but for now
    # I'll just pray that they are just edge cases…
    # -- mado
    state.value = DNFRM
    run_dnf("rm", map(lambda x: x.name, dnfrms))
    state.value = 0
    run_dnf("in", map(lambda x: x.name, dnfs))
    state.value = FLATPAK
    run_flatpak(map(lambda x: x.name, flatpaks))
    job.value += len(flatpaks)
    run_special_payloads(apps, lambda payload: payload.priority > 0)


def run_special_payloads(apps: dict[str, App], filter: Callable[[Payload], bool]):
    payloads = [p for app in apps.values() for p in app.payloads if filter(p)]
    payloads.sort(key=lambda p: p.priority)
    for p in payloads:
        state.value = PROC if isinstance(p, Procedure) else SCRIPT
        job.value += 1
        p()


def run_dnf(act: str, pkgs: Iterable[str]):
    global before_dnf
    # TODO: separate install and download parsing
    run_with_line_parse(["sudo", "dnf5", act, "-y", *pkgs], line_parse=_dnf5_line_parse)


def run_flatpak(pkgs: Iterable[str]):
    # TODO: implement progress tracking for flatpak
    # NOTE: I don't think it's actually possible…?
    run_with_line_parse(
        ["sudo", "flatpak", "install", "--noninteractive", *pkgs],
        line_parse=lambda _: (),
    )


def _dnf5_line_parse(line: str):
    global job, before_dnf, dnf_total
    if not line.startswith("["):
        return
    right = line.find("]")
    mid = line.find("/")
    if right == -1 or mid == -1:
        return
    with suppress(ValueError):
        if dnf_total != int(line[mid + 1 : right]):
            # downloading -> installing
            before_dnf = job.value
            if state.value == 0:
                state.value = DNFDL
            elif state.value == DNFDL:
                state.value = DNFIN
            else:
                # FIXME: I don't know
                pass
        job.value = before_dnf + int(line[1:mid])


def _just_read(qin: Queue, qres: Queue, fd: IO[bytes]):
    os.set_blocking(fd.fileno(), False)
    while True:
        with suppress(TypeError):
            if not (r := fd.read(1)):
                if not qin.empty():
                    break
                time.sleep(0.05)
                continue
            qres.put_nowait(r)
    qin.get()


# Copied from terrapkg/mkproj
def run_with_line_parse(
    cmd: list[str], prefix: str = "┃ ", *, line_parse: Callable[[str]]
) -> tuple[int, str, str]:
    # TODO: optimizations?
    print(end=f"\n{prefix}", flush=True)
    # Cannot use universal_newlines because it replaces \r with \n
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=0)
    assert proc.stdout
    assert proc.stderr
    qiout, qierr, qrout, qrerr = Queue(), Queue(), Queue(), Queue()
    th_out = Process(target=_just_read, args=[qiout, qrout, proc.stdout])
    th_err = Process(target=_just_read, args=[qierr, qrerr, proc.stderr])
    th_out.start()
    th_err.start()
    line, out, err, tmpout, tmperr = "", "", "", b"", b""
    while True:
        while not qrout.empty():
            tmpout += qrout.get_nowait()
        with suppress(TypeError):
            out += (sout := tmpout.decode("utf-8"))
            line += sout
            if "\n" in line:
                [line_parse(ln) for ln in line.splitlines()[:-1]]
                line = line.splitlines()[-1]
            tmpout = b""
            sys.stdout.write(
                sout.replace("\n", f"\n{prefix}")  # .replace("\r", f"\r{prefix}")
            )
        while not qrerr.empty():
            tmperr += qrerr.get_nowait()
        with suppress(TypeError):
            err += (serr := tmperr.decode("utf-8"))
            tmperr = b""
            sys.stderr.write(
                serr.replace("\n", f"\n{prefix}")  # .replace("\r", f"\r{prefix}")
            )
        if qrerr.empty() and qrout.empty() and (rc := proc.poll()) is not None:
            break
    if len(tmpout) > 0:
        print(f"Some bytes can't be decoded: {tmpout}")
    qiout.put(0)
    qierr.put(0)
    th_out.join()
    th_err.join()
    print()
    return rc, out, err
