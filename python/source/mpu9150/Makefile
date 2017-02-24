TARGET = libmpu9150.so

CC = gcc
LINKER   := gcc
TOUCH 	 := $(shell touch *)
CFLAGS := -Wall -fsingle-precision-constant -fPIC
LFLAGS	:= -lm -lrt -lpthread -shared -lprussdrvd
CLFLAGS	:= -lm -lrt -lmpu9150

# add -DI2C_DEBUG for debugging
DEFS = -DEMPL_TARGET_LINUX -DMPU9150 -DAK8975_SECONDARY

SOURCES  := $(wildcard *.c)
INCLUDES := $(wildcard *.h)
OBJECTS  := $(SOURCES:$%.c=$%.o)
OBJECTS  := vector3d.o quaternion.o linux_glue.o c_i2c.o inv_mpu.o inv_mpu_dmp_motion_driver.o mpu9150.o imu.o
RM := rm -f
CP := cp
INSTALL_DIR = /usr/lib/
INCLUDE_DIR = /usr/include

all:$(TARGET)

test: test.c
	$(CC) $(CFLAGS) $(DEFS) $(CLFLAGS) $< -o $(@)

# linking Objects
$(TARGET): $(OBJECTS)
	@$(LINKER) $(LFLAGS) -o $(TARGET) $(OBJECTS)
	@echo
	@echo "Linking Complete"

$(OBJECTS): %.o : %.c
# @$(TOUCH)
	@$(CC) $(CFLAGS) $(DEFS) -c $< -o $(@)
	@echo "Compiled "$<" successfully!"

# install to /usr/bin
$(phony all) : $(TARGET)
.PHONY: install

install:
	$(MAKE)
#	@install -m 0755 $(INCLUDES) $(INCLUDE_DIR)
	@install -m 0755 $(TARGET) $(INSTALL_DIR)
#	@install -m 0755 $(OBJECTS) $(INSTALL_DIR)
#@install -m 0755 pru/libprussdrv.so $(INSTALL_DIR)
#	cp pru/prussdrv.h $(INCLUDE_DIR)
#	cp pru/pruss_intc_mapping.h $(INCLUDE_DIR)
#	cp -r mavlink/ $(INCLUDE_DIR)
#	cp $(INSTALL_DIR)/$(TARGET) $(INSTALL_DIR)/lib$(TARGET)
	ldconfig
	@echo "$(TARGET) installed to $(INSTALL_DIR)"
	@echo

clean:
	@$(RM) test *.o
	@$(RM) *.so
	@echo "Cleanup complete!"
