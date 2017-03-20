========
Tutorial
========

In this tutorial you will learn how to use `Controller`s, work with
*signals* and the various *blocks* available with the package `ctrl`.

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
times.
	
What's going on?
^^^^^^^^^^^^^^^^

Let's now analyze each part of the above code to make sense of what is
going on. The first couple lines import the modules to be used from
the standard python's `time` and various `ctrl` libraries::

    import time
    from ctrl import Controller
    from ctrl.block import Printer
    from ctrl.block.clock import TimerClock

After importing :py:class:`Controller` we can initialize the variable
:py:data:`hello` as being a :py:class:`Controller`::
    
    hello = Controller()

A :py:class:`Controller` by itself does nothing useful, so let's add some
*signals* and *blocks* that we can interact with. The line::

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
case :py:class:`TimerClock`, and a *list of signal outputs*, in this
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
in this case :py:data:`message`, a :py:mod:`ctrl.block` object, in this
case :py:class:`Printer`, and a *list of inputs*, in this case
:py:data:`['clock']`.
		   
:py:class:`ctrl.block.Printer` is a *sink* that prints signals provide
as inputs. The parameter :py:attr:`message = 'Hello World!'` is the
message to be printed.

Having created a *source* and a *sink* we are ready to run the controller::

  with hello:
      # do nothing for 5 seconds
      time.sleep(5)

We use the python's :py:obj:`with` statement, which will automatically
start and stop the controller. Inside the :py:obj:`with` statement we
pause for `5` seconds to let the controller run its loop and print
`Hello World!` 5 times.

Secretly behind the statement :samp:`with hello` is a call to the
pair of methods :py:meth:`ctrl.Controller.start` and
:py:meth:`ctrl.Controller.stop`. In fact, alternatively, one could have
written the not so clean::

    hello.start()
    # do nothing for 5 seconds
    time.sleep(5)
    hello.stop()

Note that we enclosed the controller action inside a :py:func:`try` block::

    try:
        # run the controller and do other things
    
    except KeyboardInterrupt:
        pass

    finally:
        # disable Printer and TimerClock
        hello.set_sink('message', enabled = False)
        hello.set_source('clock', enabled = False)
	
This construction allows the controller to be stopped in a controlled
way. In this case we need to stop the :py:data:`clock` or the
controller would continue to run even as the program terminates, which
is not the desired behavior in this first example.


The controller loop
^^^^^^^^^^^^^^^^^^^

In order to understand what is going on on behind the scenes we shall
probe the contents of the controller variable :py:data:`hello`. For
example::

    print(hello)

produces the output:

.. code-block::none

    > Controller with 0 device(s), 2 signal(s), 1 source(s), 1 sink(s), and 0 filter(s)

For more information we use the method :py:meth:`ctrl.info`. For
example::

      print(hello.info('all'))

produces the output:

.. code-block::none

    > Controller with 0 device(s), 2 signal(s), 1 source(s), 1 sink(s), and 0 filter(s)
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

which details the *devices*, *signals*, *sources*, *filters* and
*sinks* present in the controller :py:data:`hello`. Of course the
*signals*, *sources* and *sinks* correspond to the ones we have added
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
is useful to have a default controller with a clock. The method
:py:meth:`ctrl.add_device` automates the process of adding blocks to a
controller. For example, the following code::

  from ctrl import Controller

  controller = Controller()
  clock = controller.add_device('clock',
                                'ctrl.block.clock', 'TimerClock',
				type = 'source', 
				outputs = ['clock'],
				enable = True,
				period = self.period)

automatically creates a :py:class:`ctrl.block.clock.TimerClock` which
is add to :py:data:`controller` as a :py:data:`source` with output
:py:data:`clock`. Setting the attribute :py:data:`enable` equal to
`True` makes sure the device is *enabled* at every call to
:py:meth:`ctrl.start` and *disabled* at every call to
:py:meth:`ctrl.stop`.

A controller with a clock is so common that the above construction is
provided as a module in :py:mod:`ctrl.timer`. Using
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

Note that we no longer have to disable the `clock` *source*, which is
handled automatically when exiting the :py:obj:`with` statement by
calling :py:meth:`ctrl.stop`. Note however that disabling the clock
causes clock to be read, which would print one additional message on
the screen. This is avoided by calling::

  hello.set_sink('message', enabled = False)

to disable the sink `message` before exiting the :py:obj:`with` statement.

A call to :samp:`print(hello.info('all'))`:

.. code-block:: none
	       
    > Controller with 1 device(s), 3 signal(s), 1 source(s), 1 sink(s), and 0 filter(s)
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

reveals the presence of the signal :py:data:`clock` and the *device*
:py:class:`ctrl.block.clock.TimeClock` as a *source*.

The notion of *device* is much more than a simple convenience
though. By having the controller initialize dynamically initialize the
Block by providing the module and class as strings to
:py:meth:`ctrl.add_device`, the arguments
:py:data:`'ctrl.block.clock'` and :py:data:`'TimerClock'` above, we
can initialize blocks that rely on specific hardware remotely using
our :ref:`Client Server Architecture`, as you learn later.

A call to :samp:`print(hello.info('all'))`:

.. code-block:: none
	       
    > Controller with 1 device(s), 3 signal(s), 1 source(s), 0 sink(s), and 0 filter(s)
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


------------------
Signals and Blocks
------------------

In this section you will learn more about *signals* and
*blocks*. There is no limit on the number of *signals* and *blocks*
one can add to a controller other than the ability of your computer to
process the loop in time before the next clock cycle.

    
--------------------------
Client Server Architecture
--------------------------
