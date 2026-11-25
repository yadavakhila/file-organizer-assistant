"""Entry point for File Organizer Assistant (Terminal CLI & Tkinter GUI)."""

import argparse
import sys

from core.app_service import AppService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="File Organizer Assistant - SmartCommunity Hack Project #105"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cli",
        action="store_true",
        help="Launch the interactive terminal interface (default).",
    )
    group.add_argument(
        "--gui",
        action="store_true",
        help="Launch the Tkinter graphical desktop interface.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = AppService()

    if args.gui:
        try:
            from gui.app import launch_gui

            launch_gui(service)
            return 0
        except Exception as exc:
            print(f"[!] Could not launch Tkinter GUI ({exc}). Falling back to Terminal CLI...")

    from cli import TerminalCLI

    TerminalCLI(service).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
