#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

# filename of clip to load
fileName = 'clip.mp4'
BUF_SIZE = 10
#buf = [0] * BUF_SIZE
buf = queue.Queue(BUF_SIZE)
bufGray = queue.Queue(BUF_SIZE)
fill_count = threading.Semaphore(0)
empty_count = threading.Semaphore(BUF_SIZE)
fill_count2 = threading.Semaphore(0)
empty_count2 = threading.Semaphore(BUF_SIZE)

def extractFrames():
    # Initialize frame count
    count = front = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()

    print("Reading frame {} {} ".format(count, success))
    while success:
        jpgAsText = encodeFrame(image)
        # add the frame to the buffer
        empty_count.acquire()
        buf.put(jpgAsText)
        fill_count.release()
        front = (front + 1) % 10
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")
    empty_count.acquire()
    buf.put("end")
    fill_count.release()

def convertFrames():
    # initialize frame count
    count = 0
    frameAsText = ""
    # go through each frame in the buffer until the buffer is empty
    while True:
        # get the next frame
        fill_count.acquire()
        frameAsText = buf.get()
        if(frameAsText == "end"):
            break
        empty_count.release()
        img = decodeFrame(frameAsText)
        print("Converting frame {}".format(count))
        grayscaleJpgAsText = convertToGrayscaleAndEncode(img)
        # add the frame to the buffer
        empty_count2.acquire()
        bufGray.put(grayscaleJpgAsText)
        fill_count2.release()
        count += 1
    print("Finished converting all frames")
    empty_count2.acquire()
    bufGray.put("end")
    fill_count2.release()


def displayFrames():
    # initialize frame count
    count = rear = 0
    frameAsText = ""

    # go through each frame in the buffer until the buffer is empty
    while True:
        # get the next frame
        fill_count2.acquire()
        frameAsText = bufGray.get()
        if(frameAsText == "end"):
            break
        empty_count2.release()
        img = decodeFrame(frameAsText)
        rear = (rear + 1) % 10
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

def decodeFrame(frameAsText):
    # decode the frame
    jpgRawImage = base64.b64decode(frameAsText)
    # convert the raw frame to a numpy array
    jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
    # get a jpg encoded frame
    img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)
    return img

def convertToGrayscaleAndEncode(img):
    # convert the image to grayscale
    grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # encode
    grayscaleJpgAsText = encodeFrame(grayscaleFrame)
    return grayscaleJpgAsText

def encodeFrame(image):
    # get a jpg encoded frame
    success, jpgImage = cv2.imencode('.jpg', image)
    #encode the frame as base 64 to make debugging easier
    jpgAsText = base64.b64encode(jpgImage)
    return jpgAsText

# extract the frames
extractThread = threading.Thread(target=extractFrames)
# convert the frames
convertThread = threading.Thread(target=convertFrames)
# display the frames
displayThread = threading.Thread(target=displayFrames)

extractThread.start()
convertThread.start()
displayThread.start()
