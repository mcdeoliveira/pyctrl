import pyctrl.block as block
import sys
import contextlib
import time
import cv2
import numpy as np

# This class is for Camera class for all (Ubuntu, Windows...etc)
class Camera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):

        # process parameters
        self.resolution = kwargs.pop('resolution', None)
        self.flip = kwargs.pop('flip', 0)
        self.transpose = kwargs.pop('transpose', True)
        self.reverse = kwargs.pop('reverse', False)
        
        # call super
        super().__init__(**kwargs)

        # openCV Camera start
        self.cap = cv2.VideoCapture(0)

        print("Initatied the camera")

    def set(self, **kwargs):

        if 'resolution' in kwargs:
            self.resolution = kwargs.pop('resolution')

        if 'flip' in kwargs:
            self.flip = kwargs.pop('flip')
            
        if 'transpose' in kwargs:
            self.transpose = kwargs.pop('transpose')
            
        if 'reverse' in kwargs:
            self.reverse = kwargs.pop('reverse')
            
        # call super
        super().set(**kwargs)

    def read(self):

        if self.enabled:
            ret, frame = self.cap.read()
            if self.resolution:
                frame = cv2.resize(frame, self.resolution)
            if self.reverse:
                if self.transpose:
                    frame = cv2.transpose(frame)
                if self.flip:
                    frame = cv2.flip(frame, self.flip)
            else:
                if self.flip:
                    frame = cv2.flip(frame, self.flip)
                if self.transpose:
                    frame = cv2.transpose(frame)
            self.buffer = (frame, )
        return self.buffer

    def __del__(self, **kwargs):
        self.cap.release()
        cv2.destroyAllWindows()


# This class is for show frame
class Screen(block.Sink, block.Block):
    
    def write(self, *values):

        if self.enabled:
            cv2.imshow('image', values[0])
            cv2.waitKey(1)


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
            cv2.imwrite(self.filename.format(self.counter), image)
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
            cv2.imwrite(image_filename, image)

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


class SharpenFrame(block.Filter, block.BufferBlock):

    def read(self):

        if self.enabled:
            # print(' > read in SharpenFrames')
            kernel_sharpen = np.array([[0, -1, 0],
                                       [-1, 5, -1],
                                       [0, -1, 0]])
            frame= cv2.filter2D(self.buffer[0], -1, kernel_sharpen)

            self.buffer = (frame, )

        return self.buffer


class BlurFrame(block.Filter, block.BufferBlock):

    def read(self):

        if self.enabled:
            # print(' > read in SharpenFrames')
            kernel_blur = np.ones((5,5), np.float32) / 25
            frame= cv2.filter2D(self.buffer[0], -1, kernel_blur)

            self.buffer = (frame, )

        return self.buffer


class denoiseFrame(block.Filter, block.BufferBlock):

    def read(self):
        pass
        #if self.enabled:
            # print(' > read in SharpenFrames')
        #    kernel_sharpen = np.array([[0, -1, 0],
        #                               [-1, 5, -1],
        #                               [0, -1, 0]])
        #    frame= cv2.filter2D(self.buffer[0], -1, kernel_sharpen)

        #    self.buffer = (frame, )

        # return self.buffer
            
if __name__ == "__main__":
     
    print("> Testing Camera")

    camera = Camera()
    screen = Screen()

    (values, ) = camera.read()
    #print(values)
    #time.sleep(2)
    screen.write(values)
    #ime.sleep(2)
