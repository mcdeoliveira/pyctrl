from distutils.core import setup, Extension
import platform

GETTIME_LIBS = []
MPU9150_LIBS = ['mpu9150']
if platform.system().lower() == 'linux':
    GETTIME_LIBS.append('rt')
    MPU9150_LIBS.append('rt')

gettime = Extension("ctrl.gettime", 
                    sources = ["source/_gettime.c", "source/gettime.c"],
                    libraries = GETTIME_LIBS)

mpu9150 = Extension("ctrl.bbb.mpu9150", 
                    sources = ["source/_mpu9150.c"],
                    libraries = MPU9150_LIBS)

setup(
      ext_modules=[gettime, mpu9150]
)
