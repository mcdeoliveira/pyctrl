from distutils.core import setup, Extension
import platform

LIBS = []
if platform.system().lower() == 'linux':
    LIBS.append('rt')

gettime = Extension("ctrl.gettime", 
                    sources = ["source/_gettime.c", "source/gettime.c"],
                    libraries = LIBS)

setup(
      ext_modules=[gettime])
