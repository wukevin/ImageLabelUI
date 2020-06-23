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
    parser.add_argument("--mode", type=str, choices=("mask", "bbox"), default="mask")
    return parser


def main():
    """Main program loop"""
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "mask":
        app = gui.ImageLabeller(args.image)
    elif args.mode == "bbox":
        app = gui.ImageBBoxLabeller(args.image)
    else:
        raise ValueError(f"Unrecognized mode: {args.mode}")
    app.mainloop()


if __name__ == "__main__":
    main()
