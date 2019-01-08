import pyctrl.block as block
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


    def saveImageToArray(self, frame):
        self.array.append(frame)


    def __del__(self, **kwargs):
        self.cap.release()
        cv2.destroyAllWindows()
        
# This class is for Camera class for RaspberryPi (Ubuntu, Windows...etc)
class ComputerCamera(block.Source, block.BufferBlock):
    from picamera.array import PiRGBArray
    from picamera import PiCamera

    def __init__(self, **kwargs):
        
        # call super
        super().__init__(**kwargs)

if __name__ == "__main__":
    
    print("> Testing Camera")

    camera = ComputerCamera()
    camera.run(False)
