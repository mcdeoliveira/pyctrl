import pyctrl.block as block
import time
import cv2
import numpy as np

# This class is for Camera class for all (Ubuntu, Windows...etc)
class ComputerCamera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):
        
        # call super
        super().__init__(**kwargs)

        # openCV Camera start
        self.cap = cv2.VideoCapture(0)
        self.array = []
        print("Initatied the camera")


    def read(self):
        print('> read')

        if self.enabled:
            self.ret, self.frame = self.cap.read()
            self.buffer = (self.frame, )
        return self.buffer


    def run(self, saveFile):
        print("Running the Camera")

        img_counter = 0
        while (self.cap.isOpened()):
            ret, frame = self.cap.read()

            if(ret == True):
                frame = cv2.flip(frame, 1)

                # Show the Video
                self.show(frame)
                
                # Append each frame to the npArray
                self.saveImageToArray(frame)        
                
                # Saving Files if self.saveFile is True
                if(saveFile == True):
                    img_name = "img_{}.png".format(img_counter)
                    cv2.imwrite(img_name, self.frame)
                    img_counter += 1

                if (cv2.waitKey(1) & 0xFF == ord('q')):
                    break

            else:
                break


    def show(self, frame):
        # Showing the Frame to the user
        cv2.imshow('frame', frame)
        cv2.waitkey(0)


    def saveImageToArray(self, frame):
        self.array.append(frame)


    def __del__(self, **kwargs):
        self.cap.release()
        cv2.destroyAllWindows()


# This class is for show frame
class Screen(block.Sink, block.Block):
    
    def __init__(self, **kwargs):
        # call super
        super().__init__(**kwargs)
        
    def write(self, *values):

        if self.enabled:
            frame = values[0]
            frame = cv2.flip(frame, 1)
            cv2.imshow('frame', frame)
            cv2.waitKey(1000)


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

    camera = ComputerCamera()
    screen = Screen()

    #camera.run(False)

    print(camera.read())
    (values,) = camera.read()
    print(values)
    time.sleep(2)
    screen.write(values)
    time.sleep(2)