"""
Classes for GUI elements

Useful references:
- https://stackoverflow.com/questions/40604233/draw-on-python-tkinter-canvas-using-mouse-and-obtain-points-to-a-list
- https://stackoverflow.com/questions/30168896/tkinter-draw-one-pixel
"""

import tkinter as tk


class ImageLabeller(tk.Tk):
    def __init__(self, img_fname: str = ""):
        tk.Tk.__init__(self)

        self.recorded_points = []
        self.canvas = tk.Canvas(width=400, height=400, bg="white", cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)

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
            *self.recorded_points[-1][-2], *self.recorded_points[-1][-1]
        )

    def close_paintbrush(self, event):
        """Close the paintbrush shape on click release"""
        pos = event.x, event.y
        self.recorded_points[-1].append(pos)
        self.canvas.create_line(
            *self.recorded_points[-1][-1], *self.recorded_points[-1][0]
        )

    def clearall(self):
        self.canvas.delete("all")
