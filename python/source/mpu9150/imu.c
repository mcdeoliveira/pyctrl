#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "c_i2c.h"		// i2c lib
#include "mpu9150.h"	// general DMP library
#include "MPU6050.h" 	// gyro offset registers

#include "imu.h"

// local function declarations
int loadGyroCalibration();

//// MPU9150 IMU ////
int initialize_imu(int sample_rate, signed char orientation[9]){
  printf("Initializing IMU\n");

  linux_set_i2c_bus(1);

	
  if (mpu_init(NULL)) {
    printf("\nmpu_init() failed\n");
    return -1;
  }
 
  //mpu_set_sensors(INV_XYZ_GYRO | INV_XYZ_ACCEL | INV_XYZ_COMPASS);
  mpu_set_sensors(INV_XYZ_GYRO | INV_XYZ_ACCEL);
  mpu_set_sample_rate(sample_rate);
	
  // compass run at 100hz max. 
  if(sample_rate > 100){
    // best to sample at a fraction of the gyro/accel
    mpu_set_compass_sample_rate(sample_rate/2);
  }
  else{
    mpu_set_compass_sample_rate(sample_rate);
  }
  mpu_set_lpf(188); //as little filtering as possible

  // set fsrs
  mpu_set_gyro_fsr(1000);
  mpu_set_accel_fsr(2);
  
  if (0)
    {
	    
      dmp_load_motion_driver_firmware(sample_rate);
	    
      dmp_set_orientation(inv_orientation_matrix_to_scalar(orientation));
      dmp_enable_feature(DMP_FEATURE_6X_LP_QUAT 
			 | DMP_FEATURE_SEND_RAW_ACCEL 
			 | DMP_FEATURE_SEND_CAL_GYRO);
	    
      dmp_set_fifo_rate(sample_rate);
	    
      if (mpu_set_dmp_state(1)) {
	printf("\nmpu_set_dmp_state(1) failed\n");
	return -1;
      }
	    
    }
	
  if(loadGyroCalibration()){
    printf("\nGyro Calibration File Doesn't Exist Yet\n");
    printf("Use calibrate_gyro example to create one\n");
    printf("Using 0 offset for now\n");
  };
	
  return 0;
}

int setXGyroOffset(int16_t offset) {
	uint16_t new = offset;
	const unsigned char msb = (unsigned char)((new&0xff00)>>8);
	const unsigned char lsb = (new&0x00ff);//get LSB
	//printf("writing: 0x%x 0x%x 0x%x \n", new, msb, lsb);
	linux_i2c_write(MPU_ADDR, MPU6050_RA_XG_OFFS_USRH, 1, &msb);
	return linux_i2c_write(MPU_ADDR, MPU6050_RA_XG_OFFS_USRL, 1, &lsb);
}

int setYGyroOffset(int16_t offset) {
	uint16_t new = offset;
	const unsigned char msb = (unsigned char)((new&0xff00)>>8);
	const unsigned char lsb = (new&0x00ff);//get LSB
	//printf("writing: 0x%x 0x%x 0x%x \n", new, msb, lsb);
	linux_i2c_write(MPU_ADDR, MPU6050_RA_YG_OFFS_USRH, 1, &msb);
	return linux_i2c_write(MPU_ADDR, MPU6050_RA_YG_OFFS_USRL, 1, &lsb);
}

int setZGyroOffset(int16_t offset) {
	uint16_t new = offset;
	const unsigned char msb = (unsigned char)((new&0xff00)>>8);
	const unsigned char lsb = (new&0x00ff);//get LSB
	//printf("writing: 0x%x 0x%x 0x%x \n", new, msb, lsb);
	linux_i2c_write(MPU_ADDR, MPU6050_RA_ZG_OFFS_USRH, 1, &msb);
	return linux_i2c_write(MPU_ADDR, MPU6050_RA_ZG_OFFS_USRL, 1, &lsb);
}

int loadGyroCalibration(){
	FILE *cal;
	char file_path[100];

	// construct a new file path string
	strcpy (file_path, CONFIG_DIRECTORY);
	strcat (file_path, GYRO_CAL_FILE);
	
	// open for reading
	cal = fopen(file_path, "r");
	if (cal == 0) {
		// calibration file doesn't exist yet
		return -1;
	}
	else{
		int xoffset, yoffset, zoffset;
		fscanf(cal,"%d\n%d\n%d\n", &xoffset, &yoffset, &zoffset);
		if(setXGyroOffset((int16_t)xoffset)){
			printf("problem setting gyro offset\n");
			return -1;
		}
		if(setYGyroOffset((int16_t)yoffset)){
			printf("problem setting gyro offset\n");
			return -1;
		}
		if(setZGyroOffset((int16_t)zoffset)){
			printf("problem setting gyro offset\n");
			return -1;
		}
	}
	fclose(cal);
	return 0;
}
