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
    def __init__(self, img, folder):
        self.img = cv.imread(img[0])
        self.images = img
        self.save_folder = folder
        # Resize so max width is 800, preserving aspect ratio
        self.img = cv.resize(self.img, (800, int(800 * self.img.shape[0] / self.img.shape[1])))
        self.corrected = self.img
        self.colour_corrected = self.img
        self.contrast_adjusted = self.img
        self.contast_value = 0
        self.brightness_value = 0
        self.white_balance = [0, 0, 0]
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

        # Create brightness trackbar, fit to window
        cv.createTrackbar("Brightness", "Underwater Correction", 0, 100, self.adjustBrightness)

        # Create contrast trackbar, fit to window
        cv.createTrackbar("Contrast", "Underwater Correction", 0, 100, self.adjustContrast)

        # Create red, green, blue trackbars [0-255]
        cv.createTrackbar("Red", "Underwater Correction", 50, 100, self.whiteBalanceRed)
        cv.setTrackbarMin("Red", "Underwater Correction", 0)
        cv.createTrackbar("Green", "Underwater Correction", 50, 100, self.whiteBalanceGreen)
        cv.setTrackbarMin("Green", "Underwater Correction", 0)
        cv.createTrackbar("Blue", "Underwater Correction", 50, 100, self.whiteBalanceBlue)
        cv.setTrackbarMin("Blue", "Underwater Correction", 0)

        # Resize trackbar to width=800
        cv.resizeWindow("Underwater Correction", 1600, 600)
        
        while True:
            # Get the contrast value
            self.contrast_value = cv.getTrackbarPos("Contrast", "Underwater Correction")

            # Get the brightness value
            self.brightness_value = cv.getTrackbarPos("Brightness", "Underwater Correction")

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

            if k == ord('a'):
                self.applyCorrection()

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
                         "u     undo white balance",
                         "a     apply correction to all images"]
            for i, text in enumerate(help_text):
                cv.putText(self.corrected, text, (20, 50 + 50 * i), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

    def applyCorrection(self):
        for i, img in enumerate(self.images):
            print("Applying correction to image ({}): {}".format(i, os.path.basename(img)))
            self.img = cv.imread(img)
            self.colour_corrected = self.img
            self.contrast_adjusted = self.img
            self.corrected = self.img

            self.colour_corrected = self.whiteBalance(self.white_balance)
            self.adjustContrast(self.contrast_value)
            
            # Save corrected image to save folder            
            cv.imwrite(os.path.join(self.save_folder, os.path.basename(img)), self.corrected)

    def resetWhiteBalance(self):
        self.colour_corrected = self.img
        self.adjustContrast(self.contrast_value)
        self.white_balance = [50, 50, 50]

    def mouseCallback(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            x = x - 800
            if x < 0:
                x = 0
            # Get the pixel value
            self.white_balance = self.samplePixel(self.img[y, x])
            self.colour_corrected = self.whiteBalance(self.white_balance)
            self.adjustContrast(self.contrast_value)
            cv.setTrackbarPos("Red", "Underwater Correction", int((self.white_balance[2] + 127) * 100 / 255))
            cv.setTrackbarPos("Green", "Underwater Correction", int((self.white_balance[1] + 127) * 100 / 255))
            cv.setTrackbarPos("Blue", "Underwater Correction", int((self.white_balance[0] + 127) * 100 / 255))

    def samplePixel(self, pixel):
        # Get mean value of pixel
        avg = pixel.mean()

        # Get the difference between the average and the pixel value
        diff = avg - pixel
        # Diff should be integer
        diff = diff.astype(int)

        return diff

    def whiteBalanceRed(self, x):
        self.white_balance[2] = 255 * x / 100 - 127
        self.colour_corrected = self.whiteBalance(self.white_balance)
        self.adjustContrast(self.contrast_value)

    def whiteBalanceGreen(self, x):
        self.white_balance[1] = 255 * x / 100 - 127
        self.colour_corrected = self.whiteBalance(self.white_balance)
        self.adjustContrast(self.contrast_value)

    def whiteBalanceBlue(self, x):
        self.white_balance[0] = 255 * x / 100 - 127
        self.colour_corrected = self.whiteBalance(self.white_balance)
        self.adjustContrast(self.contrast_value)

    def whiteBalance(self, diff):
        self.white_balance = diff

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
        self.adjustBrightness(self.brightness_value)

    def adjustBrightness(self, x):
        self.brightness_value = x
        # Apply brightness
        self.brightness = cv.convertScaleAbs(self.contrast, alpha=1, beta=x)
        self.corrected = self.brightness


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python underwater_correction.py <image>")
        sys.exit(1)

    img_files = []
    save_path = None

    if len(sys.argv) == 3:
        # Save path
        save_path = sys.argv[2]
    else:
        save_path = os.path.dirname(sys.argv[1]) + "/corrected"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    if sys.argv[1].endswith(".jpg") or sys.argv[1].endswith(".png"):
        img_files.append(sys.argv[1])
    else:
        # Open directory and get all image files
        for file in os.listdir(sys.argv[1]):
            if file.endswith(".jpg") or file.endswith(".png"):
                img_files.append(sys.argv[1] + "/" + file)

    if img_files is None:
        print("Could not read the image.")
        sys.exit(1)

    underwater = UnderwaterCorrection(img_files, save_path)
    underwater.showEditWindow()

    sys.exit(0)
