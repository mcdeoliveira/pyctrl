from setuptools import setup, find_packages

setup(
    
    name="pyctrl",
    version="0.3",
    packages=find_packages(),
    scripts=['scripts/pyctrl_start_server',
             'scripts/pyctrl_stop_server'],

    # metadata
    author = "Mauricio C. de Oliveira",
    author_email = "mauricio@ucsd.edu",
    
    description = "Python Suite for Systems and Control",
    license = "Apache-2.0",
    
    keywords = "feedback control systems beaglebone black Robotics Cape",
    
    url = "https://github.com/mcdeoliveira/pyctrl"
    download_url = "https://github.com/mcdeoliveira/pyctrl/archive/0.3.tar.gz"

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
    ],
    
)
