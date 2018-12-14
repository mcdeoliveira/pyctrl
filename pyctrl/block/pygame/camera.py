import pyctrl.block as block

import pygame
import pygame.camera
import numpy as np

# initialize pygame
pygame.init()

# This class is for Web Camera
class Camera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):

        # process parameters
        self.resolution = kwargs.pop('resolution', (640, 480))
        
        # call super
        super().__init__(**kwargs)

        # Initialize the Camera
        pygame.camera.init()

        # Get the Connected Camera List
        listCamera = pygame.camera.list_cameras()
        if not listCamera:
            raise ValueError("Sorry, no cameras detected.")

        self.cam = pygame.camera.Camera(listCamera[0], self.resolution, "RGB")
        self.cam.start()
        
        print('Camera loaded.')

    def set(self, **kwargs):

        if 'resolution' in kwargs:
            # make sure ratio is a float
            self.resolution = float(kwargs.pop('resolution'))

        # TODO: If changed, reinitialize camera
        
        # call super
        super().set(**kwargs)

    def read(self):

        # print('> read')
        if self.enabled:

            self.buffer = (self.cam.get_image(),)
        
        return self.buffer

# This class is for Web Camera
class Screen(block.Sink, block.Block):

    def __init__(self, **kwargs):

        # process parameters
        self.resolution = kwargs.pop('resolution', (640, 480))
        
        # call super
        super().__init__(**kwargs)

        # Initialize the display
        self.screen = pygame.display.set_mode( self.resolution )

    def write(self, *values):

        if self.enabled:

            assert len(values) == 1
            image = values[0]
            self.screen.blit(image, (0,0))
            pygame.display.update()

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
            pygame.image.save(image, self.filename.format(self.counter))
            self.counter += 1

# This class takes an image and outputs a numpy array
class ImageToArray(block.Filter, block.BufferBlock):

    def read(self):

        # print('> read')
        if self.enabled:

            self.buffer = (np.asarray(pygame.surfarray.array3d(self.buffer[0])), )
        
        return self.buffer
            
# TODO: atexit
# Shutdown the WebCam
def shutdown(self):
    pygame.display.quit()
    pygame.camera.quit()
    pygame.quit()

# Main Method
if __name__ == "__main__":

    print("> Testing Camera")
                
    camera = Camera()
    screen = Screen()

    (values,) = camera.read()
    screen.write(values)
    
