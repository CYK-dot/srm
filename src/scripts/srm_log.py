#!/usr/bin/env python3
"""
Common logging module for SRM tools.
"""
import sys
from typing import List

def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def _colorize(text: str, color_code: str) -> str:
    if _supports_color():
        return f"\033[{color_code}m{text}\033[0m"
    return text

def _green(text: str) -> str: return _colorize(text, "32")
def _red(text: str) -> str: return _colorize(text, "31")
def _yellow(text: str) -> str: return _colorize(text, "33")
def _cyan(text: str) -> str: return _colorize(text, "36")

class Logger:
    def __init__(self, prog_name: str):
        self.prog_name = prog_name

    def info(self, msg: str) -> None:
        print(f"[{self.prog_name}] {msg}")

    def ok(self, msg: str) -> None:
        print(_green(f"[{self.prog_name}] {msg}"))

    def warn(self, msg: str) -> None:
        print(_yellow(f"[{self.prog_name}] warning: {msg}"), file=sys.stderr)

    def error(self, msg: str) -> None:
        print(_red(f"[{self.prog_name}] error: {msg}"), file=sys.stderr)

    def verbose(self, msg: str) -> None:
        print(_cyan(f"[{self.prog_name}] {msg}"))

    def error_multiline(self, title: str, lines: List[str]) -> None:
        print(_red(f"[{self.prog_name}] error: {title}"), file=sys.stderr)
        for line in lines:
            print(_red(f"    {line}"), file=sys.stderr)