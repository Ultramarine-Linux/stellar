import multiprocessing as mp
import os
import sys
import time
from contextlib import suppress
from multiprocessing import Process, Queue
from subprocess import PIPE, Popen
from typing import IO, Callable, Iterable

from . import App, Dnf, DnfRm, Flatpak, Payload, Procedure

job = mp.Value("i", 0)
total_jobs = 0
state = mp.Value("i", 0)
PROC = 1
SCRIPT = 2
DNFRM = 3
DNFIN = 4
FLATPAK = 5


def gather[T: Payload](cls: type[T], apps: dict[str, App]) -> list[T]:
    return list(
        payload
        for app in apps.values()
        for payload in app.payloads
        if isinstance(payload, cls)
    )


def process_installs(apps: dict[str, App]):
    global total_jobs
    # FIXME: add dnf downloads and installs separately
    total_jobs = len(apps)
    p = mp.Process(target=install, args=(apps))
    p.start()
    # TODO: start the GUI here
    p.join()


def install(apps: dict[str, App]):
    global job, state
    dnfrms = gather(DnfRm, apps)
    dnfs = gather(Dnf, apps)
    flatpaks = gather(Flatpak, apps)
    pre = [
        payload
        for app in apps.values()
        for payload in app.payloads
        if payload.priority < 0
    ]
    pre.sort(key=lambda p: p.priority)
    for p in pre:
        state.value = PROC if isinstance(p, Procedure) else SCRIPT
        job.value += 1
        p()
    state.value = DNFRM
    run_dnf("rm", map(lambda x: x.name, dnfrms))
    state.value = DNFIN
    run_dnf("in", map(lambda x: x.name, dnfs))
    state.value = FLATPAK
    run_flatpak(map(lambda x: x.name, flatpaks))
    post = [
        payload
        for app in apps.values()
        for payload in app.payloads
        if payload.priority > 0
    ]
    post.sort(key=lambda p: p.priority)
    for p in post:
        state.value = PROC if isinstance(p, Procedure) else SCRIPT
        job.value += 1
        p()


def run_dnf(act: str, pkgs: Iterable[str]):
    # TODO: separate install and download parsing
    run_with_line_parse(["sudo", "dnf5", act, *pkgs], line_parse=_dnf5_line_parse)


def run_flatpak(pkgs: Iterable[str]):
    # TODO: implement progress tracking for flatpak
    run_with_line_parse(["sudo", "flatpak", "install", *pkgs], line_parse=lambda _: ())


def _dnf5_line_parse(line: str):
    global job
    if not line.startswith("["):
        return
    right = line.find("]")
    mid = line.find("/")
    if right == -1 or mid == -1:
        return
    with suppress(ValueError):
        job.value = int(line[1:mid])


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
