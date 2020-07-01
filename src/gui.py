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
- https://stackoverflow.com/questions/11305962/python-tkinter-how-to-get-coordinates-on-scrollable-canvas
"""
import os
import sys
import logging
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

    def __init__(
        self,
        img_fname: str,
        pb_color=image_utils.ANNOT_COLORS["GREEN"],
        width: int = 750,
        height: int = 750,
    ):
        tk.Tk.__init__(self)
        self.img_fname = img_fname
        img = image_utils.load_img(img_fname)
        self.height, self.width, _channels = img.shape
        self.rgb_color = pb_color
        self.win_width = width
        self.win_height = height

        self.recorded_points = []
        self.tkinter_lines = []
        # List of tuples, each tuple is 4 values decribing a line
        self.pil_draw_queue = []
        self.canvas = tk.Canvas(
            # self, width=self.width, height=self.height, cursor="cross"
            self,
            width=width,
            height=height,
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
        self.canvas.bind("<d>", self.clearlast)
        self.canvas.bind("<D>", self.clearall)
        self.canvas.bind("<m>", self.open_minimap)

    def _get_loc_of_event(self, event) -> Tuple[int, int]:
        """Get real location of event"""
        pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        return pos

    def open_minimap(self, event):
        """
        Open a new window to display a minimap of where we are
        """
        win = tk.Toplevel(self)
        win.title("Minimap")
        win.geometry("400x400")

        # Determine currrent viewport
        top_left = (self.canvas.canvasx(0), self.canvas.canvasy(0))
        top_right = (self.canvas.canvasx(self.win_width), self.canvas.canvasy(0))
        bottom_right = (
            self.canvas.canvasx(self.win_width),
            self.canvas.canvasy(self.win_height),
        )
        bottom_left = (self.canvas.canvasx(0), self.canvas.canvasy(self.win_height))

        # Open the image and draw viewport
        img = Image.open(self.img_fname)  # PIL PngImageFile
        img_draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        stroke_width = 2 * int(max(img_width, img_height) / 400)
        stroke_color = (0, 255, 0)
        img_draw.line((*top_left, *top_right), fill=stroke_color, width=stroke_width)
        img_draw.line(
            (*top_right, *bottom_right), fill=stroke_color, width=stroke_width
        )
        img_draw.line(
            (*bottom_right, *bottom_left), fill=stroke_color, width=stroke_width
        )
        img_draw.line((*bottom_left, *top_left), fill=stroke_color, width=stroke_width)
        # img.show()  # Alternative presentation
        # Resize and display
        photo_img = ImageTk.PhotoImage(img.resize((400, 400), Image.ANTIALIAS))
        lbl2 = tk.Label(win, image=photo_img)
        lbl2.image = photo_img
        lbl2.pack()
        win.mainloop()

    def initialize_paintbrush(self, event):
        """Initialize paintbrush on click"""
        # Each new mouse click event starts a new list of points
        # This allows for drawing multiple shapes for a single mask
        pos = self._get_loc_of_event(event)
        self.recorded_points.append([pos])
        self.tkinter_lines.append([])
        self.pil_draw_queue.append([])

        assert len(self.tkinter_lines) == len(self.pil_draw_queue)

    def paintbrush(self, event):
        """Draw paintbrush line"""
        pos = self._get_loc_of_event(event)
        self.recorded_points[-1].append(pos)
        line_coords = [
            *self.recorded_points[-1][-2],
            *self.recorded_points[-1][-1],
        ]
        assert len(line_coords) == 4
        line_id = self.canvas.create_line(line_coords, fill=_from_rgb(self.rgb_color))
        self.tkinter_lines[-1].append(line_id)
        self.pil_draw_queue[-1].append(line_coords)

    def close_paintbrush(self, event):
        """Close the paintbrush shape on click release"""
        pos = self._get_loc_of_event(event)
        self.recorded_points[-1].append(pos)

        line_coords = [  # Connect first and last point
            *self.recorded_points[-1][-1],  # Last point
            *self.recorded_points[-1][0],  # First point
        ]
        assert len(line_coords) == 4
        line_id = self.canvas.create_line(*line_coords, fill=_from_rgb(self.rgb_color))
        self.tkinter_lines[-1].append(line_id)
        self.pil_draw_queue[-1].append(line_coords)

    def save_mask(self, _event):
        # First create the mask
        logging.info(f"Creating underlying mask image")
        pil_image = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        pil_draw = ImageDraw.Draw(pil_image)
        for line_group in self.pil_draw_queue:
            for line in line_group:
                assert len(line) == 4
                pil_draw.line(line, fill=self.rgb_color)

        try:  # Try to save the mask
            fname = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                initialfile=os.path.splitext(os.path.basename(self.img_fname))[0]
                + "_mask.png",
                title="Save to file mask",
                filetypes=(("png files", "*.png"), ("all files", "*.*")),
            )
            filled_image = image_utils.lift_masks_from_img(
                np.array(pil_image), color_rgb=self.rgb_color,
            )
            image_utils.write_img(filled_image, fname)
        except ValueError:
            pass

    def clearall(self, _event):
        """Clear all strokes"""
        for line_id_group in self.tkinter_lines:
            for line_id in line_id_group:
                self.canvas.delete(line_id)
        # Reset record of points
        self.tkinter_lines = []
        self.recorded_points = []
        self.pil_draw_queue = []

    def clearlast(self, _event):
        """Clear the last stroke"""
        if self.pil_draw_queue:
            self.pil_draw_queue.pop(-1)
            self.recorded_points.pop(-1)

            for line_id in self.tkinter_lines.pop(-1):
                self.canvas.delete(line_id)


class ImageBBoxLabeller(ImageLabeller):
    """
    Draws bounding boxes on images.

    Programmatic strategy here is to use recorded_points to maintain the outer
    vertices of the rectangle. When mouse is released, the final rectangle
    is then saved to the buffer of lines we need to draw on the final output
    pil_draw_queue.
    """

    def initialize_paintbrush(self, event):
        """Initialize the rectangle tool"""
        pos = self._get_loc_of_event(event)
        self.recorded_points.append(
            [pos, pos]
        )  # Each list in recorded points stores a pair of points
        self.tkinter_lines.append([])  # Grows and shrinks with mouse drag

    def _get_box_lines(self, vertices: Tuple[Tuple[int, int], Tuple[int, int]]):
        """Given a single pair of points, draw the corresponding box"""
        (i_x, i_y), (j_x, j_y) = vertices
        min_x, max_x = min(i_x, j_x), max(i_x, j_x)
        min_y, max_y = min(i_y, j_y), max(i_y, j_y)

        left_edge = min_x, min_y, min_x, max_y
        top_edge = min_x, max_y, max_x, max_y
        right_edge = max_x, max_y, max_x, min_y
        bottom_edge = max_x, min_y, min_x, min_y
        return left_edge, top_edge, right_edge, bottom_edge

    def paintbrush(self, event):
        """Get updated position of cursor and draw the new bounding box"""
        pos = self._get_loc_of_event(event)
        self.recorded_points[-1][-1] = pos  # Update outer corner of the current box

        self.clearlast(None, still_dragging=True)
        pair = self.recorded_points[-1]
        assert len(pair) == 2
        box_lines = self._get_box_lines(pair)
        assert len(box_lines) == 4
        for line in box_lines:
            line_id = self.canvas.create_line(line, fill=_from_rgb(self.rgb_color))
            self.tkinter_lines[-1].append(line_id)

    def close_paintbrush(self, event):
        """
        Close paintbrush on click release, writing into the queue of lines we write
        to output file
        """
        pos = self._get_loc_of_event(event)
        self.recorded_points[-1][-1] = pos

        pair = self.recorded_points[-1]
        assert len(pair) == 2
        box_lines = self._get_box_lines(pair)
        assert len(box_lines) == 4

        self.pil_draw_queue.append(box_lines)

    def save_mask(self, _event):
        logging.info(f"Creating underlying mask image")
        pil_image = Image.open(self.img_fname)
        pil_draw = ImageDraw.Draw(pil_image)
        for line_group in self.pil_draw_queue:
            for line in line_group:
                assert len(line) == 4
                pil_draw.line(line, fill=self.rgb_color)

        try:  # Try to save the mask
            fname = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                initialfile=os.path.splitext(os.path.basename(self.img_fname))[0]
                + "_bbox.png",
                title="Save to file mask",
                filetypes=(("png files", "*.png"), ("all files", "*.*")),
            )
            image_utils.write_img(np.array(pil_image), fname)
        except ValueError:
            pass

    def clearall(self, _event):
        """Clear all drawn boxes"""
        for line_id in self.tkinter_lines:
            self.canvas.delete(line_id)
        self.pil_draw_queue = []
        self.tkinter_lines = []

    def clearlast(self, _event, still_dragging: bool = False):
        """Clear the last stroke"""
        for line_id in self.tkinter_lines[-1]:
            self.canvas.delete(line_id)
        self.tkinter_lines[-1] = []  # Clear out the last item
        if not still_dragging:
            self.pil_draw_queue.pop(-1)


@functools.lru_cache(maxsize=32)
def _from_rgb(rgb: Tuple[int, int, int]) -> str:
    """
    translates an rgb tuple of int to a tkinter friendly color code
    https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
    """
    return "#%02x%02x%02x" % rgb
