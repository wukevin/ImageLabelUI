# ImageLabelUI
UI for loading in images and allowing user to draw on them.

## Installation

1. Clone the repository
2. Create the conda environment

```bash
conda env create -f environment.yml
```
## Usage
To run the program, make sure you have activated the `imagelabel` conda environment, then run the following, replacing `FILENAME.png` with the image file that you wish to label.

```bash
python bin/imagelabel.py FILENAME.png
```

Draw an outline by clicking and dragging the mouse. The program will show the outline in real time. When you release the mouse, the program will link the original and last points to create a closed polygon for you. You may create multiple outlines.

Note that the program does not fill in the closed polygons in real time, but the saved files will be filled in. This is done for performance reasons.

If you would like to start over, hit `BACKSPACE` to clear all drawn outlines.

When you are finished, hit `ENTER` to save the mask. You will be prompted for a filename to save. 
