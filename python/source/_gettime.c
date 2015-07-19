#include <Python.h>
#include "gettime.h"

static char module_docstring[] =
  "This module provides an interface for gettime.";
static char gettime_docstring[] =
  "Calculate the current time in nanoseconds.";

static PyObject *gettime_gettime(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
  {"gettime", gettime_gettime, METH_VARARGS, gettime_docstring},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
  PyModuleDef_HEAD_INIT,
  "gettime",   /* name of module */
  module_docstring, /* module documentation, may be NULL */
  -1,       /* size of per-interpreter state of the module,
	       or -1 if the module keeps state in global variables. */
   module_methods
};

PyMODINIT_FUNC PyInit_gettime(void)
{
  return PyModule_Create(&module);
}

static PyObject *gettime_gettime(PyObject *self, PyObject *args)
{
  /* Call the external C function to gettime */
  double seconds = gettime();

  /* Build the output tuple */
  PyObject *ret = Py_BuildValue("d", seconds);
  return ret;
}
