#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mpu9150.h"
#include "imu.h"

int main(int argc, char* argv[]){

  signed char orientation[9] = ORIENTATION_UPRIGHT;
  initialize_imu(SAMPLE_RATE, orientation);

  float gs, as;
  mpu_get_gyro_sens(&gs);
  unsigned short _as;
  mpu_get_accel_sens(&_as);
  as = (float) _as;

  printf("> READING DATA\n");

  short accel[3];
  short gyro[3];

  int i;
  for (i = 0; i < 100; i++) {

    mpu_get_accel_reg(accel, 0);
    mpu_get_gyro_reg(gyro, 0);
    
    printf("> ACCEL %f %f %f\t", accel[0]/as, accel[1]/as, accel[2]/as);
    printf("GIRO: %f %f %f\r", gyro[0]/gs, gyro[1]/gs, gyro[2]/gs);
    
  }

  printf("\n> EXITING\n");

  return 0;

}
