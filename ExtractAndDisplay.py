#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

def extractFrames(fileName, outputBuffer):
    # Initialize frame count
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()

    print("Reading frame {} {} ".format(count, success))
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        outputBuffer.put(jpgAsText)

        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")

def convertFrames(inputBuffer, outputBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while not inputBuffer.empty():
        # get the next frame
        frameAsText = inputBuffer.get()

        # decode the frame
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

        # get a jpg encoded frame
        img = cv2.imdecode(jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Converting frame {}".format(count))

        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # get a jpg encoded frame
        success, img = cv2.imencode('.jpg', grayscaleFrame)

        #encode the frame as base 64 to make debugging easier
        grayscaleJpgAsText = base64.b64encode(img)

        # add the frame to the buffer
        outputBuffer.put(grayscaleJpgAsText)

        count += 1

    print("Finished converting all frames")


def displayFrames(inputBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while not inputBuffer.empty():
        # get the next frame
        frameAsText = inputBuffer.get()

        # decode the frame
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Displaying frame {}".format(count))

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print("Finished displaying all frames")
    # cleanup the windows
    cv2.destroyAllWindows()

# filename of clip to load
filename = 'clip.mp4'

# shared queue
extractionQueue = queue.Queue()
grayscaleQueue = queue.Queue()

# extract the frames
extractFrames(filename, extractionQueue)

# convert the frames
convertFrames(extractionQueue, grayscaleQueue)

# display the frames
displayFrames(grayscaleQueue)
