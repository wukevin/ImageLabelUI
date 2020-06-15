"""
Main thread
"""

import os
import sys

import tkinter as tk

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
import gui


def main():
    """Main program loop"""
    app = gui.ImageLabeller()
    app.mainloop()


if __name__ == "__main__":
    main()
