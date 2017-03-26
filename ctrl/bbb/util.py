import time
import glob

def load_device_tree(name):

    slots = glob.glob("/sys/devices/bone_capemgr.?/slots")[0]
    #print('name = {}'.format(name))
    #print('slots = {}'.format(slots))
    
    retval = -1
    with open(slots, 'r+') as file:
        for line in file:
            #print('line = {}'.format(line))
            if line.find(name) >= 0:
                # return true if device is already loaded
                return 0

        # reached end of file: device is not loaded
        file.write(name)
        retval = 1
        
    # take a break
    time.sleep(1)

    return retval
