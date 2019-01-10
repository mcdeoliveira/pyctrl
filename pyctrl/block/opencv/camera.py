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


# This class is for Camera class for RaspberryPi (Ubuntu, Windows...etc)
class PiCamera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):
        from picamera.array import PiRGBArray
        from picamera import PiCamera

        # call super
        super().__init__(**kwargs)

        resolution = (160, 120)
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = 20
        self.rawCapture = PiRGBArray(self.camera, size = resolution)

        self.frame = None
        self.running = True

        camera.start_recording('foo.h264')

    
    def run(self):
        if self.running == True:
            self.rawCapture = PiRGBArray(self.camera, size = self.resolution)
            self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
            self.frame=self.rawCapture.array
            return self.frame

    
    def __del__(self, **kwargs):
        self.camera.stop_recording()
        self.running=False
        time.sleep(1.5)
        self.camera.close()
        time.sleep(1.5)


if __name__ == "__main__":
    
    print("> Testing Camera")

    camera = Camera()
    screen = Screen()

    print(camera.read())
    (values,) = camera.read()
    print(values)
    time.sleep(2)
    screen.write(values)
    time.sleep(2)
