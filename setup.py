from setuptools import setup, find_packages

setup(
    
    name="ctrl",
    version="0.2a",
    packages=find_packages(),
    scripts=['scripts/ctrl_start_server',
             'scripts/ctrl_stop_server'],

    # metadata
    author="Mauricio C. de Oliveira",
    author_email="mauricio@ucsd.edu",
    description="Python Suite for Systems and Control",
    license="Apache-2.0",
    keywords="feedback control systems beaglebone black Robotics Cape",
    url="https://github.com/mcdeoliveira/ctrl"
    
)
