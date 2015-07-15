from distutils.core import setup, Extension
import numpy.distutils.misc_util

setup(
    ext_modules=[Extension("gettime", ["_gettime.c", "gettime.c"])],
)
