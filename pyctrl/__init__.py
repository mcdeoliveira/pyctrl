import warnings
from threading import Thread, Timer, Condition
import numpy
import importlib
from enum import Enum

from .block import Block, BlockType

# alternative perf_counter
import sys
from time import perf_counter

class ControllerWarning(Warning):
    pass

class ControllerException(Exception):
    pass

# state
IDLE = 0
RUNNING = 1
EXITING = 2

from .block.container import Container
            
class Controller(Container):
    """
    :py:class:`pyctrl.Controller` provides functionality for running
    signal flow tasks.

    A Controller can be in one of three states:

    1. IDLE
    2. RUNNING
    3. EXITING

    Upon initialization a Controller state is set to IDLE.

    :param kwargs: should be left empty
    :raises: :py:class:`pyctrl.ControllerException` if any parameters are passed to py:data`**kwargs`

    """

    def __init__(self, **kwargs):

        # noclock
        self.noclock = kwargs.pop('noclock', False)
        
        # call super
        super().__init__(**kwargs)

    def _reset(self):

        # call super
        super()._reset()
        
        # state
        self.state = IDLE
        
        # real-time loop
        self.is_running = False

        # duty
        self.duty = 0

        # running thread
        self.thread = None

        # signals
        self.signals.update({ 'is_running': self.is_running, 
                              'duty': self.duty })
                            

        # no clock?
        if not self.noclock:

            # add signal clock
            self.add_signal('clock')

            # add device clock
            self.add_source('clock',
                            ('pyctrl.block.clock', 'Clock'),
                            ['clock'],
                            enable = True)

            # reset clock
            self.set_source('clock', reset=True)
        
    # __str__ and __repr__
    def __str__(self):
        return self.info()

    __repr__ = __str__
    
    # reset
    def reset(self):
        """
        Stop the controller, remove all devices, sources, sinks,
        filters, and all signals except `is_running` and `duty`.

        Objects that inherit from `Controller` can customize `reset()`
        by overloading the private method `_reset()`.
        """
        # call stop
        self.stop()

        # call _reset
        self._reset()

    # get_state
    def get_state(self):
        """
        Return the current state of the Controller.

        :return: the state of the Controller
        """
        return self.state

    # set_state
    def set_state(self, state):
        """
        Set the current state of the Controller.

        :param state: the state of the controller
        """
        self.state = state
    
    def __enter__(self):
        
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        
        self.stop()

    def run(self):

        # Loop
        self.is_running = True
        self.signals['is_running'] = self.is_running

        self.duty = 0
        self.signals['duty'] = self.duty

        # enable devices
        # print('> controller:: ENABLE')
        self.set_enabled(True)

        while self.is_running and self.state != EXITING:

            # call super
            duty = super().run()
            
            # update is_running
            self.is_running = self.signals['is_running']

            # update duty
            self.signals['duty'] = duty
            self.duty = max(self.duty, duty)

        # disable devices
        # print('< controller:: DISABLE')
        self.set_enabled(False)

        return self.duty
            
    def start(self):
        """
        Start Controller loop.
        """

        # stop first if running
        if self.is_running:
            warnings.warn('Controller is already running...')
            return
        
        # Start thread
        self.thread = Thread(target = self.run)
        self.thread.start()

        # change state to running
        self.state = RUNNING

    def stop(self):
        """
        Stop Controller loop.
        """

        # Stop thread
        if self.is_running:
            self.is_running = False
            self.signals['is_running'] = self.is_running

        # Wait for thread to finish
        if self.thread:
            self.thread.join()
            self.thread = None
            
        # change state to idle
        self.state = IDLE

    def join(self):
        """
        Wait for Controller thread to terminate.
        """
        if self.thread:
            self.thread.join()

