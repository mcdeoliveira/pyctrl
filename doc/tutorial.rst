========
Tutorial
========

In this tutorial you will learn how to use Controllers, work with *signals* and the various *blocks* available with the package `ctrl`.

--------------
Hello World!
--------------

Start with the following simple *Hello World!* example::

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl import Controller
    from ctrl.block import Printer
    from ctrl.block.clock import TimerClock

    # initialize controller
    hello = Controller()
    
    # add the signal clock
    hello.add_signal('clock')
    
    # add a TimerClock as a source
    hello.add_source('clock',
		     TimerClock(period = 1),
		     ['clock'])

    # add a Printer as a sink
    hello.add_sink('message',
		   Printer(message = 'Hello World!'),
		   ['clock'])

    try:
        # run the controller
        with hello:
	    # do nothing for 5 seconds
	    time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        # disable Printer and TimerClock
        hello.set_sink('message', enabled = False)
        hello.set_source('clock', enabled = False)

This program will print the message *Hello World!* on the screen 4
times. The complete program is in :ref:`hello_world.py`.

----------------
What's going on?
----------------

Let's now analyze each part of the above code to make sense of what is
going on. The first couple lines import the modules to be used from
the standard python's `time` and various `ctrl` libraries::

    import time
    from ctrl import Controller
    from ctrl.block import Printer
    from ctrl.block.clock import TimerClock

After importing :py:class:`Controller` you can initialize the variable
:py:data:`hello` as being a :py:class:`Controller`::
    
    hello = Controller()

A :py:class:`Controller` by itself does nothing useful, so let's add some
*signals* and *blocks* that you can interact with. The line::

    hello.add_signal('clock')

adds the *signal* :py:data:`clock`.

A *signal* holds a numeric scalar or vector value and is used to
communicate between *blocks*. The next lines::
    
    hello.add_source('clock',
		     TimerClock(period = 1),
		     ['clock'])

add a :py:class:`TimerClock` as a *source*. A *source* is a type of
block that takes produces at least one *output* and has *no inputs*.

The parameters to :py:meth:`ctrl.Controller.add_source` are a *label*,
in this case :py:data:`clock`, a :py:mod:`ctrl.block` object, in this
case :py:class:`ctrl.block.clock.TimerClock`, and a *list of signal outputs*, in this
case the *signal* :py:data:`['clock']`.

:py:class:`ctrl.block.clock.TimerClock` is a clock based on python's
:py:class:`Timer`. The parameter :py:attr:`period = 1` passed to
:py:class:`TimerClock` means that the *source* :py:data:`clock` will
write to the *signal* :py:data:`clock` a time stamp every `1` second.

The following line::

    hello.add_sink('message',
		   Printer(message = 'Hello World!'),
		   ['clock'])

add a `Printer` as a *sink*. A *sink* is a type of block that takes at
least one *input* but produces *no output*.

The parameters to :py:meth:`ctrl.Controller.add_sink` are a *label*,
in this case :py:data:`'message'`, a :py:mod:`ctrl.block` object, in this
case :py:class:`Printer`, and a *list of inputs*, in this case
:py:data:`['clock']`.
		   
:py:class:`ctrl.block.Printer` is a *sink* that prints signals provide
as inputs. The parameter :py:attr:`message = 'Hello World!'` is the
message to be printed.

Having created a *source* and a *sink* you are ready to run the controller::

  with hello:
      # do nothing for 5 seconds
      time.sleep(5)

Python's :py:obj:`with` statement automatically start and stop the
controller. Inside the :py:obj:`with` statement :samp:`time.sleep(5)`
pauses the program for 5 seconds to let the controller run its loop
and print `Hello World!` 5 times.

Secretly behind the statement :samp:`with hello` is a call to the
pair of methods :py:meth:`ctrl.Controller.start` and
:py:meth:`ctrl.Controller.stop`. In fact, alternatively, one could have
written the not so clean::

    hello.start()
    # do nothing for 5 seconds
    time.sleep(5)
    hello.stop()

Note that you enclosed the controller action inside a :py:func:`try` block::

    try:
        # run the controller and do other things
    
    except KeyboardInterrupt:
        pass

    finally:
        # disable Printer and TimerClock
        hello.set_sink('message', enabled = False)
        hello.set_source('clock', enabled = False)
	
This construction allows the controller to be stopped in a controlled
way. In this case you need to manually stop the :py:data:`clock` or
the controller would continue to run even as the program terminates,
which is not the desired behavior in this first example.

-------------------
The controller loop
-------------------

In order to understand what is going on on behind the scenes you will
probe the contents of the controller variable :py:data:`hello`. For
example, after running the code in :ref:`Hello World!` a call to::

    print(hello)

produces the output:

.. code-block:: none

    > Controller with 0 device(s), 2 signal(s), 1 source(s), 1 sink(s), and 0 filter(s)

For more information you can use the method
:py:meth:`ctrl.Controller.info`. For example::

    print(hello.info('all'))

produces the output:

.. code-block:: none

    > Controller with 0 device(s), 2 signal(s), 1 source(s), 0 filter(s), 1 sink(s), and 0 timer(s)
    > devices
    > signals
      1. clock
      2. duty
      3. is_running
    > sources
      1. clock[TimerClock, enabled] >> clock
    > filters
    > sinks
      1. clock >> message[Printer, enabled]
    > timers

which details the *devices*, *signals*, *sources*, *filters* and
*sinks* present in the controller :py:data:`hello`. Of course the
*signals*, *sources* and *sinks* correspond to the ones you have added
earlier. Note the two additional signals :py:data:`duty` and
:py:data:`is_running` that are always present and will be described
later.

Note also that the relationship between *sources* and *sinks* with
*signals* is indicated by the arrow :samp:`>>`. In this case, the
*source* :py:data:`clock` outputs to the *signal* :py:data:`clock` and
the *sink* :py:data:`message` has as input the same *signal*
:py:data:`clock`.

Starting the controller :py:data:`hello` with the statement
:py:obj:`with` or :py:meth:`ctrl.Controller.start` fires up the
following sequence of events:

1. Every *source* is *read* and its outputs are copied to the *signals*
   connected to the *output* of the *source*. This process is repeated
   sequentially for every *source* which is in the state
   :py:data:`enabled` until all *sources* have run once.

2. The input signals of every *filter* are *written* to the *filter*
   that is then *read* and its outputs are copied to the *signals*
   connected to the *output* of the *filter*. This process is repeated
   sequentially for every *filter* which is in the state
   :py:data:`enabled` until all *filter* have run once.

3. The input signals of every *sink* are *written* to the *sink*. This
   process is repeated sequentially for every *filter* which is in the
   state :py:data:`enabled` until all *filter* have run once.

4. If the *signal* :py:data:`is_running` is still `True` go back to
   step 1, otherwise stop.

The *signal* :py:data:`is_running` can be set to `False` by calling 
:py:meth:`ctrl.Controller.stop` or exiting the :py:obj:`with`
statement. In the `Hello World!` example this is done after doing
nothing for 5 seconds inside the :py:obj:`with` statement.

Note that the *flow* of *signals* is established by adding *sources*,
*filters*, and *sinks*, which are processed according to the above
loop.

Note also that the content of the input signals is made available to
the *filters* and *sinks*. To see this replace the sink
:py:data:`message` by::

    hello.add_sink('message',
		   Printer(message = 'Hello World @ {:3.1f} s'),
		   ['clock'])

and run the controller to see a message that now prints the *signal*
:py:data:`clock` along with `Hello World` message. The format
`{:3.1f}` is used as in python's :py:func:`format`. More
than one *signal* can be printed by specifying multiple placeholders
in the attribute :py:attr:`message`.

-----------------------
Devices and Controllers
-----------------------

As you suspect after going through the :ref:`Hello World!` example, it
is useful to have a default controller with a clock. In fact, as you
will learn later in :ref:`Timers`, every :py:class:`ctrl.Controller`
comes equipped with some kind of clock. The method
:py:meth:`ctrl.Controller.add_device` automates the process of adding
blocks to a controller. For example, the following code::

  from ctrl import Controller

  controller = Controller()
  clock = controller.add_device('clock',
                                'ctrl.block.clock', 'TimerClock',
				type = 'source', 
				outputs = ['clock'],
				enable = True,
				period = self.period)

automatically creates a :py:class:`ctrl.block.clock.TimerClock` which
is added to :py:data:`controller` as the *source* labeled
:py:data:`clock` with *output signal* :py:data:`clock`. Setting the
attribute :py:data:`enable` equal to `True` makes sure that the device
is *enabled* at every call to :py:meth:`ctrl.Controller.start` and *disabled* at
every call to :py:meth:`ctrl.Controller.stop`.

A controller with a timer based clock is so common that the above
construction is provided as a module in :py:mod:`ctrl.timer`. Using
:py:mod:`ctrl.timer` the `Hello World!` example can be simplified to::

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl.timer import Controller
    from ctrl.block import Printer

    # initialize controller
    hello = Controller(period = 1)
    
    # add a Printer as a sink
    hello.add_sink('message',
		   Printer(message = 'Hello World @ {:3.1f} s'),
		   ['clock'])

    try:
        # run the controller
        with hello:
	    # do nothing for 5 seconds
	    time.sleep(5)
            hello.set_sink('message', enabled = False)

    except KeyboardInterrupt:
        pass

The complete code is in :ref:`hello_timer_1.py`. Note that you no
longer have to disable the `clock` *source*, which is handled
automatically when exiting the :py:obj:`with` statement by calling
:py:meth:`ctrl.Controller.stop`. However, disabling the clock causes
an additional clock read, which would print one extra message on the
screen. This is avoided by calling::

  hello.set_sink('message', enabled = False)

to disable the *sink* :py:data:`message` right before exiting the
:py:obj:`with` statement.

A call to :samp:`print(hello.info('all'))`:

.. code-block:: none
	       
    > Controller with 1 device(s), 3 signal(s), 1 source(s), 0 filter(s), 1 sink(s), and 0 timer(s)
    > devices
      1. clock[source]
    > signals
      1. clock
      2. duty
      3. is_running
    > sources
      1. clock[TimerClock, enabled] >> clock
    > filters
    > sinks
      1. clock >> message[Printer, enabled]
    > timers

reveals the presence of the signal :py:data:`clock` and the *device*
:py:class:`ctrl.block.clock.TimerClock` as a *source*.

The notion of *device* is much more than a simple convenience
though. By having the controller dynamically initialize a block by
providing the module and class as strings to
:py:meth:`ctrl.Controller.add_device`, the arguments
:py:data:`'ctrl.block.clock'` and :py:data:`'TimerClock'` above, you
can initialize blocks that rely on specific hardware remotely using
our :ref:`Client Server Architecture`, as you will learn later.

---------------------
Extending Controllers
---------------------

One can take advantage of python's object oriented features to extend
the functionality of a :py:class:`ctrl.Controller`. All that is
necessary is to inherit from :py:class:`ctrl.Controller`. Inheritance
is an easy way to equip controllers with special hardware
capabilities. That was the case, for example, with the class
:py:class:`ctrl.timer.Controller` described in :ref:`Devices and
Controllers`. In fact, this new class is so simple that its entire
code fits here::

    import ctrl
    import ctrl.block.clock as clock

    class Controller(ctrl.Controller):
    
        def __init__(self, **kwargs):

	    # period
	    self.period = kwargs.pop('period', 0.01)

	    # Initialize controller (this will call __reset)
	    super().__init__(**kwargs)

	def __reset(self):

	    # call super first to reset controller
	    super().__reset()

	    # add device clock
	    self.add_device('clock',
	                    'ctrl.block.clock', 'TimerClock',
                            type = 'source', 
                            outputs = ['clock'],
                            enable = True,
                            period = self.period)
			    
	    # reset clock
	    self.set_source('clock', reset=True)

Virtually all functionality is provided by the base class
:py:class:`ctrl.Controller`. The only methods overloaded are
:py:meth:`ctrl.Controller.__init__` and
:py:meth:`ctrl.Controller.__reset`. The first is the standard python
constructor, which in this case just allows for the new attribute
:py:attr:`period`. The method :py:meth:`ctrl.Controller.__reset` is
called by :py:meth:`super().__init__` to set up the basic resources
available when the controller is initialized. It is also called by the
method :py:meth:`ctrl.Controller.reset`. In fact, one rarely needs to
overload any method other than :py:meth:`ctrl.Controller.__init__` and
:py:meth:`ctrl.Controller.reset`.

For example, after initialization or a call to
:py:meth:`ctrl.timer.Controller.reset`,
:samp:`print(hello.info('all'))` returns:

.. code-block:: none
	       
    > Controller with 1 device(s), 3 signal(s), 1 source(s), 0 filter(s), 0 sink(s), and 0 timer(s)
    > devices
      1. clock[source]
    > signals
      1. clock
      2. duty
      3. is_running
    > sources
      1. clock[TimerClock, enabled] >> clock
    > filters
    > sinks
    > timers

which shows the presence of the *source* and *signal* :py:data:`clock`.

------
Timers
------

As you have learned so far, all *sources*, *filters*, and *sinks* are
continually processed in a loop. In the above example you have equipped
the controller with a :py:class:`ctrl.block.timer.TimerClock`, either
explicitly, as in :ref:`Hello World!`, or implicitly, by loading
:py:class:`ctrl.timer.Controller`. Note that the controller itself has
no notion of time and that events happen periodically simply because
of the presence of a :py:class:`ctrl.block.timer.TimerClock`, which
will stop processing until the set period has elapsed. In fact, the
base class :py:class:`ctrl.timer.Controller` is also equipped with a
clock *source* except that this clock that does not attempt to
interrupt processing, but simply writes the current time into the
*signal* :py:data:`clock` every time the controller loop is
restarted. A controller with such clock runs as fast as possible.

For example, the code::

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl import Controller
    from ctrl.block import Printer

    # initialize controller
    hello = Controller()

    # add a Printer as a sink
    hello.add_sink('message',
		    Printer(message = 'Current time {:5.3f} s',
		            endln = '\r'),
		    ['clock'])
    
    try:

        # run the controller
        with hello:
	    # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

will print the current time with 3 decimals as fast as possible on the
screen. The additional parameter :py:data:`endl = '\\r'` introduces a
carriage return without a line-feed so that the printing happens in a
single terminal line. Now suppose that you still want to print the
:ref:`Hello World!` message every second. You can achieve this using
*timers*. Simply add the following snippet before running the
controller::
	
    
    # add a Printer as a timer
    hello.add_timer('message',
		    Printer(message = 'Hello World @ {:3.1f} s '),
		    ['clock'], None,
                    period = 1, repeat = True)

to see the `Hello World` message printing every second as the main
loop prints the `Current time` message as fast as possible. The
parameters of the method :py:meth:`ctrl.Controller.add_timer` are the
*label* and *block*, in the case :py:data:`'message'` and the
:py:class:`Printer` object, followed by a *list of signal inputs*, in
this case :py:data:`['clock']`, and a *list of signal outputs*, in
this case :py:data:`None`, then the *timer* period in seconds, and a
flag to tell whether the execution of the *block* should repeat
periodically, as opposed to just once.

An example of a useful *timer* event to be run only once is the following::

    from ctrl.block import Constant
    
    # Add a timer to stop the controller
    hello.add_timer('stop',
		    Constant(value = 0),
		    None, ['is_running'],
                    period = 5, repeat = False)

which will stop the controller after 5 seconds. In fact, after adding
the above timer one could run the controller loop by simply waiting
for the controller to terminate using :py:meth:`ctrl.Controller.join`
as in::

    with hello:
        hello.join()

Note that your program will not terminate until all *blocks* and
*timers* terminate, so it is important that you always call
:py:meth:`ctrl.Controller.stop` or use the :py:obj:`with` statement to
exit cleanly.

A complete example with all the ideas discussed above can be found in
:ref:`hello_timer_2.py`.

-------
Filters
-------

So far you have used only *sources*, like
:py:class:`ctrl.block.clock.TimerClock`, and *sinks*, like
:py:class:`ctrl.block.Printer`. *Sources* produce outputs and take no
input and sinks take inputs but produce no output. *Filters* take
inputs *and* produce outputs. Our first filter will be used to
construct a signal which you will later apply to a motor. Consider the
following code, which corresponds to the example ::

    # import Controller and other blocks from modules
    from ctrl.timer import Controller
    from ctrl.block import Interp, Constant, Printer

    # initialize controller
    Ts = 0.1
    hello = Controller(period = Ts)

    # add motor signals
    hello.add_signal('pwm')

    # build interpolated input signal
    ts = [0, 1, 2,   3,   4,   5,   5, 6]
    us = [0, 0, 100, 100, -50, -50, 0, 0]
    
    # add filter to interpolate data
    hello.add_filter('input',
		     Interp(signal = us, time = ts),
		     ['clock'],
		     ['pwm'])

    # add logger
    hello.add_sink('printer',
                   Printer(message = 'time = {:3.1f} s, motor = {:+6.1f} %',
                           endln = '\r'),
                   ['clock','pwm'])

    # Add a timer to stop the controller
    hello.add_timer('stop',
		    Constant(value = 0),
		    None, ['is_running'],
                    period = 6, repeat = False)
    
    try:

        # run the controller
        with hello:
            hello.join()
            
    except KeyboardInterrupt:
        pass

    finally:
        pass

As you learned before, the *sink* :py:data:`printer` will print the
time *signal* :py:data:`clock` and the value of the *signal*
:py:data:`pwm` on the screen, and the *timer* :py:data:`stop` will
shutdown the controller after 6 seconds. The new block here is the
*filter* :py:data:`input`, which uses the block
:py:class:`ctrl.block.Interp`. This block will take as input the time
given by the *signal* :py:data:`clock` and produce as a result a value
that interpolates the values given in the arrays :py:data:`ts` and
:py:data:`us`. Internally it uses :py:func:`numpy.interp`
function. See `the numpy documentation
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html>`_
for details. The reason for the name :py:data:`pwm` will be explained
later in Section :ref:`Simulated motor example`.

The key aspect in this example is how *filters* process
*signals*. This can be visualized by calling
:samp:`print(hello.info('all'))`:

.. code-block:: none
	       
    > Controller with 1 device(s), 4 signal(s), 1 source(s), 1 filter(s), 1 sink(s), and 1 timer(s)
    > devices
      1. clock[source]
    > signals
      1. clock
      2. duty
      3. is_running
      4. motor
    > sources
      1. clock[TimerClock, enabled] >> clock
    > filters
      1. clock >> input[Interp, enabled] >> pwm
    > sinks
      1. clock, pwm >> printer[Printer, enabled]
    > timers
      1. stop[Constant, period = 6, enabled] >> is_running
      
where you can see the relationship between the inputs and outputs
*signals* indicated by a pair of arrows :samp:`>>` coming in *and* out
of the the *filter* :py:data:`input`. The complete code can be found
in :ref:`hello_filter_1.py`.

-----------------
Working with data
-----------------

So far you have been running blocks and displaying the results on your
screen using :py:class:`ctrl.block.Printer`. If you would want to
store the generated data for further processing you should instead use
the block :py:class:`ctrl.block.Logger`. Let us revisit the example
from :ref:`Filters`, this time adding also a
:py:class:`ctrl.block.Logger`. The only difference is the introduction
of the additional *sink*::

    from ctrl.block import logger
    
    # add logger
    hello.add_sink('logger',
                   Logger(),
                   ['clock','pwm'])

A complete example can be found in :ref:`hello_filter_2.py`. Once the
controller has run, you can then retrieve all generated data by
reading from the *sink* :py:data:`logger`. For example::

    # retrieve data from logger
    data = hello.read_sink('logger')

would retrieve the data stored into :py:data:`logger` and copy it to
the numpy array :py:data:`data`. Data is stored by rows, with each
column represented one of the signals used as inputs to the
:py:class:`ctrl.block.Logger`. In this case, the first column will
contain the signal :py:data:`clock` and the second column will contain
the signal :py:data:`pwm`. One can use the standard numpy indexing
to conveniently access the data::

    clock = data[:,0]
    motor = data[:,1]

But since this is python, you can now do whatever you please with the
data. For example you can use `matplotlib <http://matplotlib.org>`_ to
plot the data::

    # import matplotlib
    import matplotlib.pyplot as plt
    
    # start plot
    plt.figure()
        
    # plot input 
    plt.plot(clock, motor, 'b')
    plt.ylabel('motor (%)')
    plt.xlabel('time (s)')
    plt.ylim((-120,120))
    plt.xlim(0,6)
    plt.grid()
    
    # show plots
    plt.show()

The above snippet should produce a plot like the one below:

.. image:: figures/hello_filter_2.png

from which you can visualize the input signal :py:data:`pwm`
constructed by the :py:class:`ctrl.block.Interp` block. Note that the
sampling period used in :ref:`hello_filter_2.py` is 0.01 s, whereas
one used in :ref:`hello_filter_1.py` was only 0.1 s.
     
-----------------------
Simulated motor example
-----------------------

You will now work on a more sophisticated example, in which you will
combine various filters to produce a simulated model of a
DC-motor. The complete code is in :ref:`simulated_motor_1.py`.

The beginnig of the code is similar to the :ref:`hello_filter_2.py`::
  
    # import Controller and other blocks from modules
    from ctrl.timer import Controller
    from ctrl.block import Interp, Logger, Constant
    from ctrl.system.tf import DTTF, LPF

    # initialize controller
    Ts = 0.01
    simotor = Controller(period = Ts)

    # build interpolated input signal
    ts = [0, 1, 2,   3,   4,   5,   5, 6]
    us = [0, 0, 100, 100, -50, -50, 0, 0]
    
    # add motor signal
    simotor.add_signal('pwm')
    
    # add filter to interpolate data
    simotor.add_filter('input',
		       Interp(signal = us, time = ts),
		       ['clock'],
                       ['pwm'])

Note that you will be simulating this motor with a sampling period of
0.01 seconds, that is, a sampling frequency of 100 Hz. The model you
will use for the DC-motor is based on the diffential equation model:

.. math::

   \tau \ddot{\theta} + \dot{\theta} = g u

where :math:`u` is the motor input voltage, :math:`\theta` is the
motor angular displacement, and :math:`g` and :math:`\tau` are
constants related to the motor physical parameters. The constant
:math:`g` is the *gain* of the motor, which relates the steady-state
velocity achieved by the motor in response to a constant input
voltage, and the constant :math:`\tau` is the time constant of the
motor, which is a measure of how fast the motor respond to changes in
its inputs. **If you have no idea of what's going on here, keep calm
and read on! You do not need to understand all the details in order to
use this model.**

Without getting into details, in order to simulate this differential
equation you will first convert the above model in the following
discrete-time difference equation:

.. math::

   \theta_k - (1 + c) \theta_{k-1} + c \theta_{k-2} = \frac{g T_s (1 - c)}{2} \left ( u_{k-1} + u_{k-2} \right ), \quad c = e^{-\frac{T_s}{\tau}}

where :math:`T_s` is the sampling period. It is this equation that you
will simulate by creating the following *filter*::

    from ctrl.block.system import System
    from ctrl.system.tf import DTTF

    # add motor signal
    simotor.add_signal('pwm')
    
    # Add a step the voltage
    simotor.add_filter('input',
		       Interp(signal = us, time = ts),
		       ['clock'],
                       ['pwm'])

    # Motor model parameters
    tau = 1/17   # time constant (s)
    g = 0.11     # gain (cycles/sec duty)
    c = math.exp(-Ts/tau)
    d = (g*Ts)*(1-c)/2

    # add motor signals
    simotor.add_signal('encoder')

    # add motor filter
    simotor.add_filter('motor',
                       System(model = DTTF( 
                           numpy.array((0, d, d)), 
                           numpy.array((1, -(1 + c), c)))),
                       ['pwm'],
                       ['encoder'])

The input signal to the *filter* :py:data:`motor` is the *signal*
:py:data:`pwm`, which is the signal that receives the interpolated
input data you create earlier. The ouput of the *filter*
:py:data:`motor` is the *signal* :py:data:`encoder`, which corresponds
to the motor angular position :math:`\theta`.
		       
Note that the *block* used in the *filter* :py:data:`motor` is of the
class :py:class:`ctrl.block.system.System`, which allows one to
incorporate a variety of system models into filters. See :ref:`Package
ctrl.system` for other types of system models available. The
particular model you are using is a :py:class:`ctrl.system.DTTF`, in
which DTTF stands for *Discrete-Time Transfer-Function*. This model
corresponds to the difference equation discussed above.

To wrap it up you will add a *sink* :py:class:`ctrl.block.Logger` to
collect the data generated during the simulation and a *timer* to stop
the controller::

    # add logger
    simotor.add_sink('logger',
                     Logger(),
                     ['clock','pwm','encoder'])
    
    # Add a timer to stop the controller
    simotor.add_timer('stop',
		      Constant(value = 0),
		      None, ['is_running'],
                      period = 6, repeat = False)
    
As usual, the simulation is run with::
		      
  # run the controller
  with simotor:
      simotor.join()
            
After running the simulation you can read the data collected by the logger::

    # read logger
    data = simotor.read_sink('logger')
    clock = data[:,0]
    pwm = data[:,1]
    encoder = data[:,2]

and plot the results using `matplotlib <http://matplotlib.org>`_::
  
    # import matplotlib
    import matplotlib.pyplot as plt
    
    # start plot
    plt.figure()
    
    # plot input 
    plt.subplot(2,1,1)
    plt.plot(clock, pwm, 'b')
    plt.ylabel('pwm (%)')
    plt.ylim((-120,120))
    plt.xlim(0,6)
    plt.grid()
    
    # plot position
    plt.subplot(2,1,2)
    plt.plot(clock, encoder,'b')
    plt.ylabel('position (cycles)')
    plt.ylim((0,25))
    plt.xlim(0,6)
    plt.grid()
    
    # show plots
    plt.show()

to obtain a plot similar to the one below:

.. image:: figures/simulated_motor_1.png

where you can visualize both the motor input signal :py:data:`pwm`
and the motor output signal :py:data:`encoder`, which predicts that
the motor will stop at about 13 cycles (revolutions) from its original
position if the input signal :py:data:`pwm` were applied at its
input.

The above setup is one that corresponds to a typical microcontroller
interface to a DC-motor, in which the motor voltage is controlled
through a PWM (Pulse-Width-Modulation) signal ranging from 0-100% of
the pulse duty-cycle (with negative values indicating a reversal in
voltage polarity), and the motor position is read using an encoder. In
this situation, one might need to calculate the motor *velocity* from
the measured position. You will do that now by adding a couple more
filters to the simulated motor model. The complete code can be found
in :ref:`simulated_motor_2.py`.

After introducing *filters* to produce the *signals* :py:data:`pwm`
and :py:data:`encoder`, you will add another filter to calculate the
speed by *differentiating* the :py:data:`encoder` *signal*::

    from ctrl.block.system import Differentiator
    
    # add motor speed signal
    simotor.add_signal('speed')
    
    # add motor speed filter
    simotor.add_filter('speed',
                       Differentiator(),
                       ['clock','encoder'],
                       ['speed'])

The *filter* :py:data:`speed` uses a block
:py:class:`ctrl.block.system.Differentiator` that takes as input both
the :py:data:`clock` signal and the *signal* :py:data:`encoder`, which
is the one being differentiated, and produces the output *signal*
:py:data:`speed`.
		       
Differentiating a *signal* is always a risky proposition, and should
be avoided whenever possible. Even in this simulated environment,
small variations in the clock period and in the underlying
floating-point calculations will give rise to noise in the *signal*
:py:data:`speed`. In some cases one can get around by filtering the
*signal*. For example, by introducing a *low-pass filter* as in::
    
    from ctrl.system.tf import LPF
    
    # add low-pass signal
    simotor.add_signal('fspeed')
    
    # add low-pass filter
    simotor.add_filter('LPF',
                       System(model = LPF(fc = 5, period = Ts)),
                       ['speed'],
                       ['fspeed'])

The *filter* :py:data:`LPF` uses a block
:py:class:`ctrl.block.system.System` that takes as input the
:py:data:`speeed` signal and produces the output *signal*
:py:data:`fspeed`, which is the filtered version of the input
:py:data:`speeed`. The model used in
:py:class:`ctrl.block.system.System` is the low-pass filter
:py:class:`ctrl.system.LPF` with cutoff frequency :py:data:`fc` equal
to 5 Hz.

Finally collect all the data in the logger::
		       
    # add logger
    simotor.add_sink('logger',
                     Logger(),
                     ['clock','pwm','encoder','speed','fspeed'])

After all that you should have controller with the following blocks:

.. code-block:: none

    > Controller with 1 device(s), 6 signal(s), 1 source(s), 4 filter(s), 1 sink(s), and 1 timer(s)
    > devices
      1. clock[source]
    > signals
      1. clock
      2. duty
      3. encoder
      4. fspeed
      5. is_running
      6. speed
    > sources
      1. clock[TimerClock, enabled] >> clock
    > filters
      1. clock >> input[Interp, enabled] >> pwm
      2. pwm >> motor[System, enabled] >> encoder
      3. clock, encoder >> speed[Differentiator, enabled] >> speed
      4. speed >> LPF[System, enabled] >> fspeed
    > sinks
      1. clock, pwm, encoder, speed, fspeed >> logger[Logger, enabled]
    > timers
      1. stop[Constant, period = 6, enabled] >> is_running

Note how the order of the *filters* is important. Output that are
needed as inputs for other filters must be computed first if their
results are to be applied in the same iteration of the controller
loop. Otherwise, their update values would only be applied on the next
iteration. That would be the case, for example, if you had inverted
the order of the *filters* :py:data:`motor` and :py:data:`speed` as
in:

.. code-block:: none

    > filters
      1. clock >> input[Interp, enabled] >> pwm
      2. clock, encoder >> speed[Differentiator, enabled] >> speed
      3. pwm >> motor[System, enabled] >> encoder
      4. speed >> LPF[System, enabled] >> fspeed

which would make the *filter* :py:data:`speed` always see the input
*signal* :py:data:`encoder` as calculated in the previous loop
iteration. Note how this would also affect the input to the *filter*
:py:data:`LPF`!

Running :ref:`simulated_motor_2.py` produces a plot of the data
similar to the one shown below:

.. image:: figures/simulated_motor_2.png

where you can simultaneously visualize the *signal* :py:data:`pwm`,
the *signal* :py:data:`speed` as calculated by the
differentiator, and the filtered speed *signal* :py:data:`fspeed`.
	   
-------------------------
Interfacing with Hardware
-------------------------

.. image:: figures/rc_motor_1.png

.. image:: figures/rc_motor_2.png

--------------------------
Client Server Architecture
--------------------------
