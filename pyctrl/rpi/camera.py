import pyctrl.block as block
import sys
import contextlib
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
from PIL import Image


# This class is for Camera class for the Raspberry pi based on picamera
class Camera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):

        # process parameters
        self.resolution = kwargs.pop('resolution', (120, 160))
        self.framerate = kwargs.pop('framerate', 20)
        # self.flip = kwargs.pop('flip', 0)
        # self.transpose = kwargs.pop('transpose', True)
        # self.reverse = kwargs.pop('reverse', False)
        
        # call super
        super().__init__(**kwargs)

    def start_camera(self):
        
        # openCV Camera start
        self.camera = PiCamera()  # PiCamera gets resolution (height, width)
        self.camera.resolution = self.resolution
        self.camera.framerate = self.framerate
        self.rawCapture = PiRGBArray(self.camera, size=self.resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="rgb",
                                                     use_video_port=True)

    def stop_camera(self):

        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

    def set_enabled(self, enabled=True):

        # call super
        super().set_enabled(enabled)
        
        if self.enabled:
            self.start_camera()
        else:
            self.stop_camera()
        
    def set(self, **kwargs):

        if 'resolution' in kwargs:
            self.resolution = kwargs.pop('resolution')

        if 'framerate' in kwargs:
            self.framerate = kwargs.pop('framerate')

        # reinitialize camera
        self.stop_camera()
        time.sleep(.1)
        self.start_camera()
            
        # call super
        super().set(**kwargs)

    def read(self):

        if self.enabled:
            f = next(self.stream)
            frame = f.array
            self.rawCapture.truncate(0)
            self.buffer = (frame, )
        return self.buffer

    def __del__(self, **kwargs):
        self.stop_camera()


# This class is for show frame
class Screen(block.Sink, block.Block):
    
    def write(self, *values):

        if self.enabled:
            # cv2.imshow('image', values[0])
            # cv2.waitKey(1)
            pass


# This class takes an image and saves it in a file
class SaveFrame(block.Sink, block.Block):

    def __init__(self, **kwargs):

        # process parameters
        self.number_of_digits = int(kwargs.pop('number_of_digits', 4))
        self.filename = kwargs.pop('filename', 'frame') + '{:0' + str(self.number_of_digits) + 'd}.png'
        self.counter = int(kwargs.pop('counter', 0))
        
        # call super
        super().__init__(**kwargs)

    def write(self, *values):

        if self.enabled:

            assert len(values) == 1
            image = values[0]
            im = Image.fromarray(image)
            im.save(self.filename.format(self.counter), image)
            self.counter += 1


# This class takes an image and values and saves them in files
class SaveFrameValues(block.Sink, block.Block):

    def __init__(self, **kwargs):

        # process parameters
        self.endln = kwargs.pop('endln', '\n')
        self.frmt = kwargs.pop('frmt', '{: 12.4f}')
        self.sep = kwargs.pop('sep', ' ')
        self.message = kwargs.pop('message', None)
        self.index = kwargs.pop('index', None)
        
        self.number_of_digits = int(kwargs.pop('number_of_digits', 4))
        self.filename = kwargs.pop('filename', 'frame') + '{:0' + str(self.number_of_digits) + 'd}.png'
        
        self.counter = int(kwargs.pop('counter', 0))

        if self.index is sys.stdout:
            self.index = None

        # call super
        super().__init__(**kwargs)

    def write(self, *values):

        if self.enabled:

            # initialize index
            index = self.index
            if index is None:
                index = sys.stdout
            
            # save input[0] as image
            image = values[0]
            image_filename = self.filename.format(self.counter)
            im = Image.fromarray(image)
            im.save(image_filename)

            # print filename
            print(image_filename, file=index, end=' ')
            
            # print remaining values
            if self.message is not None:
                print(self.message.format(*values[1:]),
                      file=index,
                      end=self.endln)
                
            else:
                @contextlib.contextmanager
                def printoptions(*args, **kwargs):
                    original = np.get_printoptions()
                    np.set_printoptions(*args, **kwargs)
                    yield 
                    np.set_printoptions(**original)

                row = np.hstack(values[1:])
                print(self.sep.join(self.frmt.format(val) for val in row),
                      file=index, end=self.endln)

            self.counter += 1


if __name__ == "__main__":
     
    print("> Testing Camera")

    camera = Camera()
    # screen = Screen()

    (values, ) = camera.read()
    print(values)
