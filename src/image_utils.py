"""
Code for working with images

When executed as a script, pull out masks from all images

Useful links:
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.binary_closing.html
- https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_grabcut/py_grabcut.html#grabcut
"""

import os
import sys
import logging
import argparse
from typing import *

import numpy as np

from PIL import Image
import skimage.segmentation
import scipy.ndimage
import cv2  # opencv

Image.MAX_IMAGE_PIXELS = None

ANNOT_COLORS = {
    "BLUE": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
}


def load_img(fname: str, channel_dedup: bool = True, mask: bool = False) -> np.ndarray:
    """
    Load the image as a numpy array
    If channel_dedup is True, we drop channel dims that are homogenous
    """
    # https://stackoverflow.com/questions/3803888/how-to-load-png-images-with-4-channels
    assert os.path.isfile(fname), f"Cannot find {fname}"
    retval = cv2.imread(
        fname, cv2.IMREAD_UNCHANGED
    )  # Returns np.uint8 for normal images
    assert len(retval.shape) <= 3, f"Got image with anomalous dimensions: {fname}"
    if not mask:
        assert len(retval.shape) == 3
    if channel_dedup and len(retval.shape) == 3:
        drop_channels = []
        for c_dim in range(retval.shape[2]):
            if np.all(retval[:, :, c_dim] == retval[0, 0, c_dim]):
                drop_channels.append(c_dim)
        for c in drop_channels[::-1]:
            retval = np.delete(retval, c, axis=2)
    # Convert to binary mask
    if mask:
        retval = retval.astype(np.bool)
        assert np.sometrue(retval), f"Got mask that is all False: {fname}"
        assert len(retval.shape) == 2
    return retval


def write_img(img: np.ndarray, fname: str) -> str:
    """Write image"""
    Image.fromarray(img).save(fname)
    return fname


def lift_masks_from_img(
    img: np.ndarray,
    color_rgb: Tuple[int, int, int] = ANNOT_COLORS["GREEN"],
    connect_iters: int = 0,
    method: str = "outinvert",
) -> np.ndarray:
    """
    Given an image lift out a mask of regions of interest, returning a binary 2d image
    Heavily inspired by code from Bryan He
    """
    height, width, channels = img.shape
    # mask = np.all(np.abs(img - np.array(color_rgb)) <= 5, axis=2).astype(np.bool)
    # PNG is lossless so we can get away with this
    mask = np.all(img == np.array(color_rgb), axis=2).astype(bool)
    if connect_iters:
        # mask = scipy.ndimage.binary_closing(mask, iterations=connect_iters)  # Up down left right
        # mask = scipy.ndimage.binary_closing(mask, np.ones((1, 3), np.bool), iterations=connect_iters)
        # mask = scipy.ndimage.binary_closing(mask, np.eye(3, dtype=np.bool), iterations=connect_iters)
        mask = scipy.ndimage.binary_closing(
            mask, structure=np.ones((connect_iters, connect_iters), np.bool)
        )

    # Without connectivity = 1 we end up bleeding through aliased single-pixel edges
    if (
        method == "direct"
    ):  # Find centroid and flood fill. Works for single polygons and is faster
        i, j = mask.nonzero()
        assert len(i) > 0 and len(j) > 0
        i = int(round(i.mean()))
        j = int(round(j.mean()))
        mask = skimage.segmentation.flood_fill(
            mask, seed_point=(i, j), new_value=1, connectivity=1
        )
    elif (
        method == "outinvert"
    ):  # Invert image and flood fill. Works for multiple polygons. More general but slower
        mask = skimage.segmentation.flood_fill(
            ~mask, seed_point=(0, 0), new_value=0, connectivity=1
        )
    elif method == "skip" or method == "pass":  # Skip and directly output the outlines
        pass
    else:
        raise ValueError(f"Unrecognized masking method: {method}")

    assert np.sum(mask) > 0
    return mask


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser"""
    retval = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    retval.add_argument("image", nargs="+", type=str, help="Images to lift masks from")
    retval.add_argument(
        "-c",
        "--color",
        type=str,
        choices=ANNOT_COLORS.keys(),
        default="GREEN",
        help="Color to extract mask from",
    )
    retval.add_argument(
        "-o",
        "--outdir",
        type=str,
        default=os.getcwd(),
        help="Directory to output files to",
    )
    return retval


def main():
    """on the fly testing"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        logging.info(f"Creating output dir: {args.outdir}")
        os.makedirs(args.outdir)

    connection_strength = 0
    for img_path in args.image:
        logging.info(f"Lifting mask from {img_path}")
        fname_no_ext, extension = os.path.splitext(os.path.basename(img_path))
        assert extension == ".png", f"Unsupported extension: {extension}"
        fname_out = fname_no_ext + "_mask.png"

        img = load_img(img_path)
        mask = lift_masks_from_img(
            img,
            ANNOT_COLORS[args.color],
            method="outinvert",
            connect_iters=connection_strength,
        )
        logging.info(f"Saving lifted mask to {os.path.join(args.outdir, fname_out)}")
        write_img(mask, os.path.join(args.outdir, fname_out))


if __name__ == "__main__":
    main()
