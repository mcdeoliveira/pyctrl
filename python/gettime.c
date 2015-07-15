#include "gettime.h"

#include <stdio.h>	/* for printf */
#include <stdint.h>	/* for uint64 definition */
#include <stdlib.h>	/* for exit() definition */
#include <time.h>	/* for clock_gettime */

double gettime(void) {

  double diff;
  struct timespec start;

  /* measure monotonic time */
  clock_gettime(CLOCK_MONOTONIC, &start);

  diff = start.tv_sec + 1e-9 * start.tv_nsec;

  return diff;
  
}
