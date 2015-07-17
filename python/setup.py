from distutils.core import setup, Extension
import platform

LIBS = []
if platform.system() == 'linux':
    LIBS.append('rt')

gettime = Extension("gettime", 
                    sources = ["_gettime.c", "gettime.c"],
                    libraries = LIBS)

setup(
      ext_modules=[gettime])
