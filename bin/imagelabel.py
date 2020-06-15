"""
Main thread
"""

import os
import sys
import argparse

import tkinter as tk

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
import gui


def build_parser():
    """Return the argument parser"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("image", type=str, help="Image to load")
    return parser


def main():
    """Main program loop"""
    parser = build_parser()
    args = parser.parse_args()

    app = gui.ImageLabeller(args.image)
    app.mainloop()


if __name__ == "__main__":
    main()
