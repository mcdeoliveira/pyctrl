from distutils.core import setup, Extension
import numpy.distutils.misc_util

gettime = Extension("gettime", 
                    sources = ["_gettime.c", "gettime.c"],
                    libraries = ['rt'])

setup(
      ext_modules=[gettime])
