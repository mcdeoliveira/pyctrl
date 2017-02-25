#include <Python.h>
#include "mpu9150/imu.h"
#include "mpu9150/inv_mpu.h"

static char module_docstring[] =
  "This module provides an interface for mpu9150.";
static char mpu9150_docstring[] =
  "Calculate the current time in nanoseconds.";

static PyObject *mpu9150_read(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
  {"read", mpu9150_read, METH_VARARGS, mpu9150_docstring},
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

float gs, as;

PyMODINIT_FUNC PyInit_mpu9150(void)
{

  /* Initialize IMU */
  signed char orientation[9] = ORIENTATION_UPRIGHT;
  initialize_imu(SAMPLE_RATE, orientation);

  mpu_get_gyro_sens(&gs);
  unsigned short _as;
  mpu_get_accel_sens(&_as);
  as = (float) _as;

  return PyModule_Create(&module);
}

static PyObject *mpu9150_read(PyObject *self, PyObject *args)
{
  /* Call the external C function to mpu9150 */
  short accel[3];
  short gyro[3];

  mpu_get_accel_reg(accel, 0);
  mpu_get_gyro_reg(gyro, 0);
    
  /* Build the output tuple */
  PyObject *ret = Py_BuildValue("(ffffff)", 
				accel[0]/as, accel[1]/as, accel[2]/as,
				gyro[0]/gs, gyro[1]/gs, gyro[2]/gs);
  return ret;
}
