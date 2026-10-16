#!/usr/bin/env python3
"""tabhub_bus: a tiny newline-JSON broadcast bus over a unix socket.

The daemons (pen-scroll, tabhub-gestures) publish state/action events; the tray
subscribes to visualise them in its test tabs. Kept free of Qt and external
deps so daemons can import it cheaply.

  Broadcaster: server side. Feed it into a select() loop via socks()/on_readable.
  Client:      subscriber side. Runs a background thread and calls on_message.
"""
from __future__ import annotations

import json
import os
import socket
import threading
import time


def default_paths() -> dict[str, str]:
    run = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
    return {
        "pen": os.path.join(run, "tabhub-pen.sock"),
        "gestures": os.path.join(run, "tabhub-gestures.sock"),
    }


class Broadcaster:
    def __init__(self, path: str):
        self.path = path
        self.clients: list[socket.socket] = []
        self.srv: socket.socket | None = None
        try:
            if os.path.exists(path):
                os.unlink(path)
            srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            srv.bind(path)
            srv.listen(8)
            srv.setblocking(False)
            self.srv = srv
        except OSError:
            self.srv = None

    def socks(self) -> list[socket.socket]:
        return ([self.srv] if self.srv else []) + self.clients

    def is_server(self, sock) -> bool:
        return sock is self.srv

    def accept(self) -> None:
        if not self.srv:
            return
        try:
            c, _ = self.srv.accept()
            c.setblocking(False)
            self.clients.append(c)
        except OSError:
            pass

    def drop(self, c: socket.socket) -> None:
        if c in self.clients:
            self.clients.remove(c)
        try:
            c.close()
        except OSError:
            pass

    def drain(self, c: socket.socket) -> None:
        try:
            if not c.recv(4096):
                self.drop(c)
        except OSError:
            self.drop(c)

    def send(self, obj: dict) -> None:
        if not self.clients:
            return
        line = (json.dumps(obj) + "\n").encode()
        for c in list(self.clients):
            try:
                c.send(line)
            except OSError:
                self.drop(c)

    def close(self) -> None:
        for c in list(self.clients):
            self.drop(c)
        if self.srv:
            try:
                self.srv.close()
            except OSError:
                pass
            try:
                os.unlink(self.path)
            except OSError:
                pass


class Client:
    """Subscribe to a Broadcaster. on_message(dict) runs on a worker thread."""

    def __init__(self, path: str, on_message, on_status=None):
        self.path = path
        self.on_message = on_message
        self.on_status = on_status
        self._stop = False
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def _run(self) -> None:
        while not self._stop:
            s = None
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(self.path)
                if self.on_status:
                    self.on_status(True)
                buf = b""
                while not self._stop:
                    data = s.recv(4096)
                    if not data:
                        break
                    buf += data
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            self.on_message(json.loads(line))
                        except Exception:  # noqa: BLE001
                            pass
            except OSError:
                pass
            finally:
                if s:
                    try:
                        s.close()
                    except OSError:
                        pass
                if self.on_status:
                    self.on_status(False)
            if not self._stop:
                time.sleep(1)

    def stop(self) -> None:
        self._stop = True
