import pyctrl.block as block

import sys, tty, termios
import threading

# read key stuff
ARROW_UP    = "\033[A"
ARROW_DOWN  = "\033[B"
ARROW_RIGHT = "\033[C"
ARROW_LEFT  = "\033[D"
DEL         = "."
END         = "/"
SPACE       = " "

def read_key():

    key = sys.stdin.read(1)
    if ord(key) == 27:
        key = key + sys.stdin.read(2)
    elif ord(key) == 3:
        raise KeyboardInterrupt
    
    return key


class Keyboard(block.Source, block.BufferBlock):

    def __init__(self, **kwargs):

        self.angle = kwargs.pop('angle', 0.0)
        self.throttle = kwargs.pop('throttle', 0.0)
        self.thread = None
        self.running = False
        
        super().__init__(**kwargs)

    def set_enabled(self, enabled=True):

        # call super
        super().set_enabled(enabled)
        
        if enabled:

            if not self.running:
                self.thread = threading.Thread(target=self.get_arrows,
                                                   args=())
                self.thread.daemon = False
                self.thread.start()
                
        else:

            if self.running:
                
                # wait for thread to finish
                self.running = False
                
                # restore terminal settings
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.old_settings)
                
                print("Press any key to exit")
                self.thread.join()
                self.thread = None
                
                
    def get_arrows(self):

        fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(fd)
        self.running = True
        tty.setcbreak(fd)
        while self.running:
            
            print('\rthrottle = {:+5.2f} deg/s'
                  '  steering = {:+5.2f} %'
                  .format(self.throttle,
                          self.angle),
                  end='')
            
            key = read_key()
            if key == ARROW_LEFT:
                self.angle = max(self.angle - 20/360, -1)
            elif key == ARROW_RIGHT:
                self.angle = min(self.angle + 20/360, 1)
            elif key == ARROW_UP:
                self.throttle = self.throttle + 0.05
            elif key == ARROW_DOWN:
                self.throttle = self.throttle - 0.05
            elif key == SPACE:
                self.throttle = 0
                self.angle = 0
            elif key == DEL:
                self.angle = 0
            elif key == END:
                self.throttle = 0
                
            self.buffer = (self.angle, self.throttle)

    
if __name__ == "__main__":

    keyboard = Keyboard()

    keyboard.set_enable(True)
