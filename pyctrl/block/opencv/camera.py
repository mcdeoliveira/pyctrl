import pyctrl.block as block
import time
import cv2
import numpy as np

# This class is for Camera class for all (Ubuntu, Windows...etc)
class Camera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):

        # process parameters
        self.resolution = kwargs.pop('resolution', None)
        
        # call super
        super().__init__(**kwargs)

        # openCV Camera start
        self.cap = cv2.VideoCapture(0)

        print("Initatied the camera")

    def set(self, **kwargs):

        if 'resolution' in kwargs:
            self.resolution = kwargs.pop('resolution')

        # call super
        super().set(**kwargs)

    def read(self):

        if self.enabled:
            ret, frame = self.cap.read()
            if self.resolution:
                frame = cv2.resize(frame, self.resolution)
            self.buffer = (frame, )
        return self.buffer

    def __del__(self, **kwargs):
        self.cap.release()
        cv2.destroyAllWindows()


# This class is for show frame
class Screen(block.Sink, block.Block):
    
    def __init__(self, **kwargs):

        # process parameters
        self.flip = kwargs.pop('flip', 1)
        
        # call super
        super().__init__(**kwargs)
        
    def set(self, **kwargs):

        if 'flip' in kwargs:
            self.resolution = kwargs.pop('flip')

        # call super
        super().set(**kwargs)

    def write(self, *values):

        if self.enabled:
            frame = values[0]
            if self.flip:
                frame = cv2.flip(frame, self.flip)
            cv2.imshow('image', frame)
            cv2.waitKey(1)


if __name__ == "__main__":
    
    print("> Testing Camera")

    camera = Camera()
    screen = Screen()

    (values,) = camera.read()
    print(values)
    time.sleep(2)
    screen.write(values)
    time.sleep(2)
