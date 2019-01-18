from picamera.array import PiRGBArray
from picamera import PiCamera

# This class is for Camera class for RaspberryPi (Ubuntu, Windows...etc)
class PiCamera(block.Source, block.BufferBlock):
    
    def __init__(self, **kwargs):
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

    
    def shutdown(self, **kwargs):
        self.camera.stop_recording()
        self.running=False
        time.sleep(1.5)
        self.camera.close()
        time.sleep(1.5)


if __name__=="__main__":

    print("> Testing Camera")

    camera = PiCamera()
    time.sleep(.5)
    