#include "gettime.h"

#ifdef __MACH__

#include <mach/clock.h>
#include <mach/mach.h>

#else

#include <time.h>

#endif

double gettime(void) {

#ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time

  clock_serv_t cclock;
  mach_timespec_t mts;

  host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &cclock);
  clock_get_time(cclock, &mts);
  mach_port_deallocate(mach_task_self(), cclock);

#else

  struct timespec mts;

  /* measure monotonic time */
  clock_gettime(CLOCK_MONOTONIC, &mts);

#endif

  return mts.tv_sec + 1e-9 * mts.tv_nsec;
  
}
