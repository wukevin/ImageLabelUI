"""
Classes for GUI elements

Useful references:
https://stackoverflow.com/questions/40604233/draw-on-python-tkinter-canvas-using-mouse-and-obtain-points-to-a-list
"""

import tkinter as tk


class ImageLabeller(tk.Tk):
    def __init__(self, img_fname: str = ""):
        tk.Tk.__init__(self)

        self.recorded_points = []
        self.canvas = tk.Canvas(width=400, height=400, bg="white", cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<B1-Motion>", self.paintbrush)

    def paintbrush(self, event):
        x, y = event.x, event.y
        print(x, y)

    def clearall(self):
        self.canvas.delete("all")
