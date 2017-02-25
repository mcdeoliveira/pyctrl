#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "mpu9150.h"
#include "imu.h"

#define SAMPLE_RATE 200	      // inner loop sample frequencyes

mpudata_t mpu; //struct to read IMU data into
int count = 0;
unsigned long timestamp;
float duty;
float max_duty = 0;
float avg_duty = 0;

int test_func(){

  if (mpu9150_read(&mpu) != 0){
    return -1;
  }
  duty = ((float) (mpu.dmpTimestamp - timestamp))/1000;
  timestamp = mpu.dmpTimestamp;
  if (count++ > 1) {
    max_duty = (duty > max_duty ? duty : max_duty);
    avg_duty = avg_duty*(count-1)/count + duty/count;
  }

  printf("\rmax duty %+06.4f, avg duty %06.4f, duty %+06.4f", 
	 max_duty, avg_duty, duty);

  return 0;
}

int main(int argc, char* argv[]){

  signed char orientation[9] = ORIENTATION_UPRIGHT;
  initialize_imu(SAMPLE_RATE, orientation);

  /* float gs, as; */
  /* mpu_get_gyro_sens(&gs); */
  /* unsigned short _as; */
  /* mpu_get_accel_sens(&_as); */
  /* as = (float) _as; */

  printf("> INSTALL INTERRUPT\n");

  set_imu_interrupt_func(&test_func);

  printf("> READING DATA\n");

  /* short accel[3]; */
  /* short gyro[3]; */

  /* int i; */
  /* for (i = 0; i < 100; i++) { */

  /*   mpu_get_accel_reg(accel, 0); */
  /*   mpu_get_gyro_reg(gyro, 0); */
    
  /*   printf("> ACCEL %f %f %f\t", accel[0]/as, accel[1]/as, accel[2]/as); */
  /*   printf("GIRO: %f %f %f\r", gyro[0]/gs, gyro[1]/gs, gyro[2]/gs); */
    
  /* } */

  usleep(5000000); // just hang in there

  printf("\n> EXITING\n");

  stop_imu();

  return 0;

}
