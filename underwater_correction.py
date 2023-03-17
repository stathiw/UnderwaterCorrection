"""
This script is used to correct underwater images.

The script will open a window with the original image on the left and the corrected image on the right.
Clicking on the edited image will adjust the white balance using the sampled pixel.
The script will also show a trackbar to adjust the contrast of the image.
"""

__author__ = "Stathi Weir"

__license__ = "BSD-3-Clause"
__version__ = "0.0.1"
__maintainer__ = "Stathi Weir"
__email__ = "stathi.weir@gmail.com"
__status__ = "Development"

import cv2 as cv

import sys
import os

class UnderwaterCorrection:
    def __init__(self, img):
        self.img = img
        # Resize so max width is 800, preserving aspect ratio
        self.img = cv.resize(self.img, (800, int(800 * self.img.shape[0] / self.img.shape[1])))
        self.corrected = self.img
        self.colour_corrected = self.img
        self.contrast_adjusted = self.img
        self.contast_value = 0
        self.show_help = False

    def showEditWindow(self):
        # Layout:
        # Original image to the left
        # Corrected image to right

        # Create a window
        cv.namedWindow("Underwater Correction", cv.WINDOW_NORMAL)

        # Show the image
        cv.imshow("Underwater Correction", self.img)

        # Get pixel value on mouse click
        cv.setMouseCallback("Underwater Correction", self.mouseCallback)

        # Create trackbar, fit to window
        cv.createTrackbar("Contrast", "Underwater Correction", 0, 100, self.adjustContrast)

        # Resize trackbar to width=800
        cv.resizeWindow("Underwater Correction", 1600, 600)
        
        while True:
            # Get the contrast value
            self.contrast = cv.getTrackbarPos("Contrast", "Underwater Correction")

            # Concatenate the images
            side_by_side = cv.hconcat([self.img, self.corrected])

            # Show the corrected image
            cv.imshow("Underwater Correction", side_by_side)

            # Wait for ESC key
            k = cv.waitKey(1) & 0xFF
            if k == 27:
                break

            # If 'h' is pressed, show the help
            if k == ord('h'):
                self.toggleHelp()

            if k == ord('u'):
                self.resetWhiteBalance()

            # Sleep for 10ms
            cv.waitKey(10)

    def toggleHelp(self):
        if self.show_help:
            self.show_help = False
            self.adjustContrast(self.contrast_value)
        else:
            self.show_help = True
            # Display text in window
            help_text = ["ESC   exit",
                         "h     show help",
                         "u     undo white balance"]
            for i, text in enumerate(help_text):
                cv.putText(self.corrected, text, (20, 50 + 50 * i), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

    def resetWhiteBalance(self):
        self.colour_corrected = self.img
        self.adjustContrast(self.contrast_value)

    def mouseCallback(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            x = x - 800
            if x < 0:
                x = 0
            self.colour_corrected = self.whiteBalance(self.img[y, x])
            self.adjustContrast(self.contrast_value)

    def whiteBalance(self, pixel):
        # Get mean value of pixel
        avg = pixel.mean()

        # Get the difference between the average and the pixel value
        diff = avg - pixel
        # Diff should be integer
        diff = diff.astype(int)

        # Add the difference to each pixel
        corrected = self.img + diff

        # Clip the values to 0-255
        corrected = corrected.clip(0, 255)
        corrected = corrected.astype("uint8")

        return corrected

    def adjustContrast(self, x):
        self.contrast_value = x
        # Apply contrast
        alpha = 1.0 + (self.contrast_value / 100.0)
        beta = 127 * (1.0 - alpha)
        self.contrast = cv.convertScaleAbs(self.colour_corrected, alpha=alpha, beta=beta)
        self.corrected = self.contrast


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python underwater_correction.py <image>")
        sys.exit(1)

    img = cv.imread(sys.argv[1])

    if img is None:
        print("Could not read the image.")
        sys.exit(1)

    underwater = UnderwaterCorrection(img)
    underwater.showEditWindow()

    sys.exit(0)
