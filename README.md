# ImageLabelUI
UI for loading in images and allowing user to draw on them.

## Installation

1. Clone the repository
2. Create the conda environment

```bash
conda env create -f environment.yml
```
## Usage

A full list of program commandline arguments can be found by running

```bash
python bin/imagelabel.py -h
```
The following describe common use cases.

### Mask creation mode
This mode allows the user to create filled-in "masks" that denote a detailed area (or cells) that corespond with some region of interest or label.

To run the program, make sure you have activated the `imagelabel` conda environment (using `conda activate imagelabel`), then run the following, replacing `FILENAME.png` with the image file that you wish to label.

```bash
python bin/imagelabel.py FILENAME.png
```

Draw an outline by clicking and dragging the mouse. The program will show the outline in real time. When you release the mouse, the program will link the original and last points to create a closed polygon for you. You may create multiple outlines.

Note that the program does not fill in the closed polygons in real time, but the saved files will be filled in. This is done for performance reasons.

If you would like to start over, hit `d` to (iteratively) clear the last drawn outline. Alternatively, hit `D` to clear all drawn outlines. You can also hit `m` (for `m`inimap) to open a new small window that shows where you are globally in the current image.

When you are finished, hit `ENTER` to save the mask. You will be prompted for a filename to save. 

### Bounding box creation mode
This mode allows the user to drag to create rectangles (that may, say, correspond to say regions of interest in the image). The output of this mode is the original image, with teh bounding boxes drawn on top.

The mode for this is nearly the same as for creating masks, save for a modification to the command used to launch the program:

```bash
python --mode bbox bin/imagelabel.py FILENAME.png
```
The keyboard controls are the same as before.
