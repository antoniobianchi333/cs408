"""Read current usage figures from the local Codex CLI's /status readout."""

from __future__ import annotations

import fcntl
import os
import pty
import re
import select
import shutil
import struct
import subprocess
import termios
import time


_STATUS_PATTERN = re.compile(
    r"5h\s+(\d+)\s*%\s*left.*?weekly\s*(\d+)\s*%\s*left",
    re.IGNORECASE | re.DOTALL,
)
_ANSI_PATTERN = re.compile(
    rb"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))"
)


def _plain_text(terminal_output: bytes) -> str:
    return _ANSI_PATTERN.sub(b"", terminal_output).replace(b"\r", b"\n").decode(
        "utf-8", errors="replace"
    )


def get_usage_status(timeout: float = 20.0) -> str:
    """Return the current 5-hour and weekly remaining percentages as a string."""
    codex = shutil.which("codex")
    if codex is None:
        raise RuntimeError("Codex CLI was not found on PATH.")

    master_fd, slave_fd = pty.openpty()
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 120, 0, 0))
    env = os.environ.copy()
    env.setdefault("TERM", "xterm-256color")

    process = subprocess.Popen(
        [codex, "--no-daemon", "--no-alt-screen"],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
        env=env,
    )
    os.close(slave_fd)
    output = bytearray()

    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Codex CLI exited before its prompt was ready.")
            readable, _, _ = select.select([master_fd], [], [], 0.2)
            if readable:
                try:
                    output.extend(os.read(master_fd, 65536))
                except OSError:
                    break
                if "Ask Codex to do anything" in _plain_text(output):
                    break
        else:
            raise TimeoutError("Timed out waiting for the Codex CLI prompt.")

        output.clear()
        os.write(master_fd, b"/status\n")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            readable, _, _ = select.select([master_fd], [], [], 0.2)
            if readable:
                try:
                    output.extend(os.read(master_fd, 65536))
                except OSError:
                    break
                match = _STATUS_PATTERN.search(_plain_text(output))
                if match:
                    hours_remaining, weekly_remaining = match.groups()
                    return f"5h {hours_remaining}% left · weekly {weekly_remaining}% left"
            if process.poll() is not None:
                break

        raise TimeoutError("Could not read both usage percentages from Codex /status.")
    finally:
        if process.poll() is None:
            try:
                os.write(master_fd, b"\x03")
                time.sleep(0.1)
                os.write(master_fd, b"\x04")
                process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        os.close(master_fd)


if __name__ == "__main__":
    print(get_usage_status())
