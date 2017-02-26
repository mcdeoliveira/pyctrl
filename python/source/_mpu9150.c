#include <Python.h>
#include "mpu9150/mpu9150.h"
#include "mpu9150/imu.h"
#include "mpu9150/inv_mpu.h"

static char module_docstring[] =
  "This module provides an interface for mpu9150.";
static char mpu9150_read_docstring[] =
  "Read accelerometer and gyroscope data.";
static char mpu9150_reset_stats_docstring[] =
  "Reset MPU performance statistics.";
static char mpu9150_get_stats_docstring[] =
  "Read MPU performance statistics.";

static int read_func(void);
static int mpu9150_initialize(void);
static PyObject *mpu9150Error;

static PyObject *mpu9150_pyread(PyObject *self, PyObject *args);
static PyObject *mpu9150_reset_stats(PyObject *self, PyObject *args);
static PyObject *mpu9150_get_stats(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
  {"read", mpu9150_pyread, METH_VARARGS, mpu9150_read_docstring},
  {"reset_stats", mpu9150_reset_stats, METH_VARARGS, mpu9150_reset_stats_docstring},
  {"get_stats", mpu9150_get_stats, METH_VARARGS, mpu9150_get_stats_docstring},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
  PyModuleDef_HEAD_INIT,
  "mpu9150",   /* name of module */
  module_docstring, /* module documentation, may be NULL */
  -1,       /* size of per-interpreter state of the module,
	       or -1 if the module keeps state in global variables. */
   module_methods
};

static mpudata_t mpu; //struct to read IMU data into
static unsigned int count = 0;
static unsigned long timestamp;
static float max_duty = 0;
static float avg_duty = 0;
static int debug_imu = 0;

static
int read_func(void) {

  if (mpu9150_read(&mpu) != 0){
    return -1;
  }
  float duty = ((float) (mpu.dmpTimestamp - timestamp))/1000;
  timestamp = mpu.dmpTimestamp;
  if (count++ > 1) {
    max_duty = (duty > max_duty ? duty : max_duty);
    avg_duty = avg_duty*(count-1)/count + duty/count;
  }

  if (debug_imu)
    printf("\rmax duty %+06.4f, avg duty %06.4f, duty %+06.4f", 
	   max_duty, avg_duty, duty);

  return 0;
}

static float gs, as;
static int flag_initialized = 0;

static int sample_rate = 200;
static unsigned short gyro_fsr = 1000;
static unsigned char accel_fsr = 2;

static
int mpu9150_intialize(void) {
  
  /* Initialize IMU */
  signed char orientation[9] = ORIENTATION_UPRIGHT;
  initialize_imu(sample_rate,
		 orientation,
		 0);
  
  /* setup gyro and accel resolutions */
  mpu_set_gyro_fsr(gyro_fsr);
  mpu_set_accel_fsr(accel_fsr);
  
  /* retrive scaling factor */
  mpu_get_gyro_sens(&gs);
  unsigned short _as;
  mpu_get_accel_sens(&_as);
  as = (float) _as;

  set_imu_interrupt_func(&read_func);

  /* set initialized flag */
  flag_initialized = 1;

  return 0;
}

PyMODINIT_FUNC PyInit_mpu9150(void)
{
  PyObject *m;

  /* create module */
  m = PyModule_Create(&module);
  if (m == NULL)
    return NULL;

  /* create exception */
  mpu9150Error = PyErr_NewException("mpu9150.error", NULL, NULL);
  Py_INCREF(mpu9150Error);
  PyModule_AddObject(m, "error", mpu9150Error);
  
  return m;
}

static
PyObject *mpu9150_pyread(PyObject *self, PyObject *args)
{

  /* initialize */
  if (!flag_initialized)
    mpu9150_intialize();
  
  /* Build the output tuple */
  PyObject *ret = 
    Py_BuildValue("(ffffff)", 
		  mpu.rawAccel[VEC3_X] / as,
		  mpu.rawAccel[VEC3_Y] / as,
		  mpu.rawAccel[VEC3_Z] / as,
		  mpu.rawGyro[VEC3_X] / gs,
		  mpu.rawGyro[VEC3_Y] / gs,
		  mpu.rawGyro[VEC3_Z] / gs);

  return ret;
}

static
PyObject *mpu9150_reset_stats(PyObject *self, PyObject *args)
{
  count = 0;
  avg_duty = max_duty = 0;

  /* Build the output tuple */
  return Py_BuildValue("");
}

static PyObject *mpu9150_get_stats(PyObject *self, PyObject *args)
{
  /* initialize */
  if (!flag_initialized)
    mpu9150_intialize();
  
  /* Build the output tuple */
  return Py_BuildValue("(Iff)", count, avg_duty, max_duty);
}
