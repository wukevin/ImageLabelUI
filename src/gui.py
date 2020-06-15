"""
Classes for GUI elements

Useful references:
- https://stackoverflow.com/questions/40604233/draw-on-python-tkinter-canvas-using-mouse-and-obtain-points-to-a-list
- https://stackoverflow.com/questions/30168896/tkinter-draw-one-pixel
- https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image
"""
from typing import *

import numpy as np
import tkinter as tk

import image_utils


class ImageLabeller(tk.Tk):
    def __init__(self, img_fname: str = "", pb_color=image_utils.ANNOT_COLORS["GREEN"]):
        tk.Tk.__init__(self)
        self.rgb_color = pb_color

        self.recorded_points = []
        self.canvas = tk.Canvas(width=400, height=400, bg="white", cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.mask_array = np.ndarray

        self.canvas.bind("<B1-Motion>", self.paintbrush)
        self.canvas.bind("<Button-1>", self.initialize_paintbrush)
        self.canvas.bind("<ButtonRelease-1>", self.close_paintbrush)

    def initialize_paintbrush(self, event):
        """Initialize paintbrush on click"""
        self.recorded_points.append([(event.x, event.y)])

    def paintbrush(self, event):
        """Draw paintbrush line"""
        pos = event.x, event.y
        self.recorded_points[-1].append(pos)
        self.canvas.create_line(
            *self.recorded_points[-1][-2],
            *self.recorded_points[-1][-1],
            fill=_from_rgb(self.rgb_color),
        )

    def close_paintbrush(self, event):
        """Close the paintbrush shape on click release"""
        pos = event.x, event.y
        self.recorded_points[-1].append(pos)
        self.canvas.create_line(
            *self.recorded_points[-1][-1],
            *self.recorded_points[-1][0],
            fill=_from_rgb(self.rgb_color),
        )

    def clearall(self):
        self.canvas.delete("all")


def _from_rgb(rgb: Tuple[int, int, int]) -> str:
    """
    translates an rgb tuple of int to a tkinter friendly color code
    https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
    """
    return "#%02x%02x%02x" % rgb
