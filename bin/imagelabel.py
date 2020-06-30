"""
Program for annotating images with either bounding boxes
or closed polygons.
"""

import os
import sys
import argparse

import tkinter as tk

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
import gui
import image_utils


def build_parser():
    """Return the argument parser"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("image", type=str, help="Image to load")
    parser.add_argument(
        "--mode", "-m", type=str, choices=("mask", "bbox"), default="mask"
    )
    parser.add_argument(
        "--windowsize", "-w", type=int, default=750, help="Size of GUI window in pixels"
    )
    parser.add_argument(
        "--color",
        "-c",
        type=str,
        choices=image_utils.ANNOT_COLORS.keys(),
        default="GREEN",
        help="Color to use when annotating",
    )
    return parser


def main():
    """Main program loop"""
    parser = build_parser()
    args = parser.parse_args()

    # Determine the app class based on args
    if args.mode == "mask":
        app_class = gui.ImageLabeller
    elif args.mode == "bbox":
        app_class = gui.ImageBBoxLabeller
    else:
        raise ValueError(f"Unrecognized mode: {args.mode}")

    app = app_class(
        args.image,
        pb_color=image_utils.ANNOT_COLORS[args.color],
        width=args.windowsize,
        height=args.windowsize,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
