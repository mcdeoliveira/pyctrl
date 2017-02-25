#ifndef IMU_H
#define IMU_H

#define SAMPLE_RATE 200	      // inner loop sample frequency
#define DT 0.01       		  // sample time

#define DEG_TO_RAD 		0.0174532925199
#define RAD_TO_DEG 	 	57.295779513
#define PI				3.141592653
#define MAX_BUF 64

//// MPU9150 IMU
#define ORIENTATION_UPRIGHT {1,0,0, 0,0,-1, 0,1,0}; // Ethernet pointing up for BeagleMIP
#define ORIENTATION_FLAT    {1,0,0, 0,1,0, 0,0,1} // BB flat on table for BealgeQuad

//// MPU-9150 defs
#define MPU_ADDR 0x68

// Calibration File Locations
#define CONFIG_DIRECTORY "/root/robot_config/"
#define DSM2_CAL_FILE	"dsm2.cal"
#define GYRO_CAL_FILE 	"gyro.cal"
#define IMU_CAL_FILE	"imu.cal"

int initialize_imu(int sample_rate, signed char orientation[9]);

#endif /* MPU9150_H */

