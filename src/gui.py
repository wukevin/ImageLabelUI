"""
Classes for GUI elements

Useful references:
- https://stackoverflow.com/questions/40604233/draw-on-python-tkinter-canvas-using-mouse-and-obtain-points-to-a-list
- https://stackoverflow.com/questions/30168896/tkinter-draw-one-pixel
- https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image
- https://www.c-sharpcorner.com/blogs/basics-for-displaying-image-in-tkinter-python
- https://stackoverflow.com/questions/15269682/python-tkinter-canvas-fail-to-bind-keyboard
- https://stackoverflow.com/questions/42333288/how-to-delete-lines-using-tkinter
- https://stackoverflow.com/questions/38444299/trouble-with-adding-scrollbar-to-canvas-in-tkinter
"""
import os
import sys
import functools
from typing import *

import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk

import image_utils


class ImageLabeller(tk.Tk):
    """
    Image labeller for a single image
    """

    def __init__(self, img_fname: str, pb_color=image_utils.ANNOT_COLORS["GREEN"]):
        tk.Tk.__init__(self)
        self.img_fname = img_fname
        img = image_utils.load_img(img_fname)
        self.height, self.width, _channels = img.shape
        self.rgb_color = pb_color

        self.recorded_points = []
        self.tkinter_lines = []
        self.canvas = tk.Canvas(
            # self, width=self.width, height=self.height, cursor="cross"
            self,
            width=1000,
            height=1000,
            cursor="cross",
            scrollregion=(0, 0, self.width, self.height),
        )
        # self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.grid(row=0, column=0)
        self.hbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.config(command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky=tk.E + tk.W)

        self.vbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.config(command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky=tk.NE + tk.SE)

        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self.disp_img = ImageTk.PhotoImage(Image.open(img_fname))
        self.canvas.create_image(0, 0, image=self.disp_img, anchor=tk.NW)

        self.canvas.focus_set()
        self.canvas.bind("<B1-Motion>", self.paintbrush)
        self.canvas.bind("<Button-1>", self.initialize_paintbrush)
        self.canvas.bind("<ButtonRelease-1>", self.close_paintbrush)
        self.canvas.bind("<Return>", self.save_mask)
        self.canvas.bind("<BackSpace>", self.clearall)

        self.pil_image = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        self.pil_draw = ImageDraw.Draw(self.pil_image)

    def initialize_paintbrush(self, event):
        """Initialize paintbrush on click"""
        # Each new mouse click event starts a new list of points
        # This allows for drawing multiple shapes for a single mask
        self.recorded_points.append([(event.x, event.y)])

    def paintbrush(self, event):
        """Draw paintbrush line"""
        pos = event.x, event.y
        self.recorded_points[-1].append(pos)
        line_coords = [
            *self.recorded_points[-1][-2],
            *self.recorded_points[-1][-1],
        ]
        assert len(line_coords) == 4
        line_id = self.canvas.create_line(line_coords, fill=_from_rgb(self.rgb_color))
        self.tkinter_lines.append(line_id)
        self.pil_draw.line(line_coords, fill=self.rgb_color)

    def close_paintbrush(self, event):
        """Close the paintbrush shape on click release"""
        pos = event.x, event.y
        self.recorded_points[-1].append(pos)

        line_coords = [  # Connect first and last point
            *self.recorded_points[-1][-1],  # Last point
            *self.recorded_points[-1][0],  # First point
        ]
        line_id = self.canvas.create_line(*line_coords, fill=_from_rgb(self.rgb_color))
        self.tkinter_lines.append(line_id)
        self.pil_draw.line(line_coords, fill=self.rgb_color)

    def save_mask(self, _event):
        try:
            fname = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                initialfile=os.path.splitext(os.path.basename(self.img_fname))[0]
                + "_mask.png",
                title="Save to file mask",
                filetypes=(("png files", "*.png"), ("all files", "*.*")),
            )
            filled_image = image_utils.lift_masks_from_img(
                np.array(self.pil_image), color_rgb=self.rgb_color, connect_iters=5,
            )
            image_utils.write_img(filled_image, fname)
        except ValueError:
            pass

    def clearall(self, _event):
        for line_id in self.tkinter_lines:
            self.canvas.delete(line_id)
        # Reset record of points
        self.tkinter_lines = []
        self.recorded_points = []
        self.pil_image = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        self.pil_draw = ImageDraw.Draw(self.pil_image)


@functools.lru_cache(maxsize=32)
def _from_rgb(rgb: Tuple[int, int, int]) -> str:
    """
    translates an rgb tuple of int to a tkinter friendly color code
    https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
    """
    return "#%02x%02x%02x" % rgb
