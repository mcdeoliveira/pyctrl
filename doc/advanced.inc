===================
More advanced usage
===================

The next sections describe tasks that are better suited to advanced
users, such as working with the provided Client-Server architecture,
extending Controllers, or writing your own Blocks. Make sure you have
gone through the :ref:`Tutorial` and have a good understanding of the
concepts discussed there before reading this chapter.

--------------------------------------
Client-Server Application Architecture
--------------------------------------

Since the beginnings of the development of this package one goal was
to be able to deploy and run controllers on embedded systems. With
that goal in mind we provide two special classes of controllers:
:py:class:`ctrl.server.Controller` and
:py:class:`ctrl.client.Controller`, and two scripts:
:samp:`ctrl_start_server` and :samp:`ctrl_stop_server` to start and
stop a controller server. Those scripts and classes can be combined to
run applications remotely.

Starting the server
-------------------

Start by using the script :samp:`ctrl_start_server` to create a server
for you. In this tutorial, you will create a server on the same
machine you will be running the client. The process of initializing a
server on a remote machine is virtually identical. Type::

    ctrl_start_server

which start the server and produces the following output:

.. code-block:: none
  
    ctrl_start_server (version 1.0)
    > Options:
       Hostname[port]: localhost[9999]
      Sampling period: ---
        Verbose level: 1
    
    Type 'ctrl_start_server -h' for more options
    
    <class 'ctrl.Controller'> with:
      1 device(s), 0 timer(s), 3 signal(s),
      1 source(s), 0 filter(s), and 0 sink(s)
    > devices
      1. clock[source]
    > timers
    > signals
      1. clock
      2. duty
      3. is_running
    > sources
      1. clock[Clock, enabled] >> clock
    > filters
    > sinks

    > Starting server... done
    > Hit Ctrl-C or use 'ctrl_stop_server' to exit the server

showing that a server has been started at the :py:data:`localhost` at
the port :py:data:`9999`. Those are the default values for `host` and
`port`. It also shows that the server is running a controller which is
an instance of the basic :py:class:`ctrl.Controller` class.

The attribute :py:data:`host` is qualified name or valid IP address of
the machine you're connecting to and :py:data:`port` is the port you
would like to connect. The connection is established using a `TCP
network socket <https://en.wikipedia.org/wiki/Network_socket>`_. See
:ref:`Options available with ctrl_start_server` for how to set these
options.


Connecting your client
----------------------

Start a new console and a new python shell. Proceed as in
Section :ref:`Hello World!` and create a controller::

    from ctrl.client import Controller
    hello = Controller()

The only difference is that you imported :py:obj:`Controller` from the
class :py:class:`ctrl.client.Controller`, as opposed to from
:py:class:`ctrl.Controller`. Once you have initialized a controller as
a *client* and you have a controller running as a server,the flow is
very much like before. For example, we can query the controller using
:samp:`print(hello.info('all'))`, which in this case should reproduce
the exact same configuration of the controller running on the server:

.. code-block:: none
  
    ctrl_start_server (version 1.0)
    > Options:
       Hostname[port]: localhost[9999]
      Sampling period: ---
	Verbose level: 1

    <class 'ctrl.Controller'> with:
      1 device(s), 0 timer(s), 3 signal(s),
      1 source(s), 0 filter(s), and 0 sink(s)
    > devices
      1. clock[source]
    > timers
    > signals
      1. clock
      2. duty
      3. is_running
    > sources
      1. clock[Clock, enabled] >> clock
    > filters
    > sinks
	
Programming a client controller is, for the most part, just like
programming a local controller. However, there are some important caveats you should be aware of. For instance, attempting to install an instance :py:class:`ctrl.block.clock.TimerClock` as a *source*  by typing::
    
    from ctrl.block.clock import TimerClock
    hello.add_source('myclock',
		     TimerClock(period = 1),
		     ['myclock'])
		     
will fail. The reason for the failure is because an instance of the
class :py:class:`ctrl.block.clock.TimerClock` cannot be transported
from your hardware to another, that is from the *client* to the
*server*. Here is where the notion of a *device* comes in
handy. Instead of instantiating
:py:class:`ctrl.block.clock.TimerClock` on the client, you can use
:py:meth:`ctrl.Controller.add_device` to have the remote controller
instantiate it directly on the server hardware! That can be done
easily. As in Section :ref:`Devices and Controllers` type::

    hello.add_device('myclock',
                     'ctrl.block.clock', 'TimerClock',
		     type = 'source', 
		     outputs = ['myclock'],
		     enable = True,
		     period = 1)

to add a *device* :py:class:`ctrl.block.clock.TimerClock` by letting
the remote server instantiate the object. From this point on, just
proceed as in :ref:`Hello World!` to add a
:py:class:`ctrl.block.Printer`::
		     
    from ctrl.block import Printer
    hello.add_sink('message',
		   Printer(message = 'Hello World!'),
		   ['myclock'])

and run the controller::

    import time
    with hello:
        # do nothing for 5 seconds
        time.sleep(5)
        # disable Printer
        hello.set_sink('message', enabled = False)

If you can't see anything happening for five seconds, look again. This
time not on the console running the *client*, but on the console
running the *server*. You should see the message `Hello World!`
printed there a couple of times. What you have accomplished is running
a task on the remote server controller by programming it on the client
controller. Effectively, and appart from some subtleties concerning
devices, the only difference was importing from
:py:class:`ctrl.client.Controller` rather than from
:py:class:`ctrl.Controller`.

What's under the hood?
----------------------
    
Before moving forward, a bit of a technical note. You might be
wondering why :py:class:`ctrl.block.clock.TimerClock` could not be
added as a *source* but it is fine to add
:py:class:`ctrl.block.Printer` as a *sink*. The difference has to do
with the ability of the client controller to *transfer* a block to the
remote controller. In order for that to process to happen, the block
:py:class:`ctrl.block.Printer` has to be safely deconstructed, packed,
transmitted over the network socket, unpacked and then reconstructed
at the server controller.

As mentioned earlier, the transmission part is done using a `TCP
network socket <https://en.wikipedia.org/wiki/Network_socket>`_. The
packing and unpacking bit is done using a technique called
`serialization <https://en.wikipedia.org/wiki/Serialization>`_. We
rely on Python's `pickle module
<https://docs.python.org/3/library/pickle.html>`_ to handle the
dirtiest parts of this job. In a nutshell, if an object cannot be
serialized by `pickle`, that is it cannot be *pickled*, then it cannot
be installed remotely as a *source*, *filter*, *sink*, or *timer*. In
this case, it needs to be installed as a *device*.

If you are curious why :py:class:`ctrl.block.clock.TimerClock` could
not be serialized, it is because
:py:class:`ctrl.block.clock.TimerClock` runs on a separate process
thread, and there is no way to simply transfer the thread information
over the network. As for :py:class:`ctrl.block.Printer`, it is
possible to use its attributes to reconstruct it on the server
side.

Note however that what decides is an object can be *pickled* or not is
not its base class but the contents of its attributes *at the time one
attempts to pickle it*. For example, a :py:class:`ctrl.block.Printer`
in which you have setup the attribute :py:attr:`file` to redirect its
output to a local file will fail to install as a *sink*. You could
instead install it as a *device*, but in this case, the output would
be redirected to a file that lives in the remote server rather than
the local client.

A final note about serialization and `pickle` is that this process is
inherently unsafe from a security standpoint. Code that is embedded in
a serialized object can be used to take control of or damage the
server host by running malicious code. If security is a concern, it
must be addressed at the network level, before a client is allowed to
connect to a server, for example by setting up a firewall that
restricts connection to a know number of potential client addresses
combined with some strong form of authentication.


Options available with :samp:`ctrl_start_server`
------------------------------------------------

Starting :samp:`ctrl_start_server` with the :py:data:`-h` flag displays
the options available:

.. code-block:: none

    usage: ctrl_start_server [-h] [-m MODULE] [-c CONTROLLER] [-H HOST] [-p PORT]
			     [-v VERBOSE] [-t PERIOD]

    ctrl_start_server (version 1.0)
    
    optional arguments:
      -h, --help            show this help message and exit (default: False)
      -m MODULE, --module MODULE
			    controller module (default: ctrl)
      -c CONTROLLER, --controller CONTROLLER
			    controller class (default: Controller)
      -H HOST, --host HOST  host name or IP address (default: localhost)
      -p PORT, --port PORT  port number (default: 9999)
      -v VERBOSE, --verbose VERBOSE
			    level of verbosity (default: 1)
      -t PERIOD, --period PERIOD
			    sampling period in seconds (default: 0.01)
			
Besides getting help one can initialize a server with any arbitrary
controller using the :py:data:`-m`, :py:data:`--module` and
:py:data:`-c`, :py:data:`--controller` options as in::

    ctrl_start_server -m ctrl.timer

which initializes the server controller to be an instance of
:py:class:`ctrl.timer.Controller` instead of the default
:py:data:`ctrl.Controller`.

Another useful pair of options is :py:data:`-H`, :py:data:`--host` and
:py:data:`-p`, :py:data:`--port`, which can be used to change the
current host name or IP address and port. For example::

    ctrl_start_server -m ctrl.rc.mip -H 192.168.0.132 -p 9090

would initialize the server using an instance of
:py:class:`ctrl.rc.mip.Controller` at the local network IP address
`192.168.0.132` at the port `9090`.
    
Finally :py:data:`-t`, :py:data:`--period` lets one set the controller
sampling period and :py:data:`-v`, :py:data:`--verbose` control how
much messages you would see coming out of the server
controller. Setting verbose to a number higher than `2` produces an
enormous amount of information that could be useful for debugging.

Out of all these options, :py:data:`-v`, :py:data:`--verbose`,
:py:data:`-H`, :py:data:`--host` and :py:data:`-p`, :py:data:`--port`,
are the ones that cannot be changed by a client connected to the
controller server after it's been initialized.

Working with :py:class:`ctrl.client.Controller`
-----------------------------------------------

As shown above, working with an instance of
:py:class:`ctrl.client.Controller` is for the most part identical to
working with any other instance of :py:class:`ctrl.Controller`. In
this section you will learn a couple of useful practices when using a
client controller.

A first issue is setting the client to talk to the server at the right
address and port. This can be done by initializing the client with
attributes :py:attr:`host` and :py:attr:`port`. For example::
	
    from ctrl.client import Controller
    client = Controller(host = '192.168.0.132', port = 9090)

would connect the client to a local network server at address
`192.168.0.132` and port `9090`.

Once connected, an usual mistake is to make assumptions about the
current state of a server controller. Since another client could have
connected to the server earlier and changed settings in unpredictable
ways, it might be useful to call
:py:meth:`ctrl.client.Controller.reset` to *reset* the remote
controller at the server before doing anything::

    client.reset()

For the same reason, one might make sure the sampling period is the
one desired by calling::

    client.set_source('clock', period = 0.1)

which in this case would make sure the remote controller clock is
running at 10 Hz.

--------------
Error Handling
--------------

---------------------
Extending Controllers
---------------------

One can take advantage of python's object oriented features to extend
the functionality of the basic :py:class:`ctrl.Controller`. All that
is necessary is to inherit from
:py:class:`ctrl.Controller`.

Inheritance is an easy way to equip controllers with special
hardware capabilities. That was the case, for example, with the class
:py:class:`ctrl.timer.Controller` described in :ref:`Devices and
Controllers`. In fact, this new class is so simple that its entire
code easily fits here:

.. literalinclude:: ../ctrl/timer.py
   :pyobject: Controller

Virtually all functionality is provided by the base class
:py:class:`ctrl.Controller`. The only methods overloaded are
:py:meth:`ctrl.Controller.__init__` and
:py:meth:`ctrl.Controller.__reset`.

The method :py:meth:`ctrl.timer.Controller.__init__` is the standard
python constructor, which in this case parses the new attribute
:py:attr:`period` before calling the base class
:py:meth:`ctrl.Controller.__init__` using::
      
      super().__init__(**kwargs)

Most of the action is in the method
:py:meth:`ctrl.Controller.__reset`. In fact, a closer look at
:py:meth:`ctrl.Controller.__init__`:

.. literalinclude:: ../ctrl/__init__.py
   :pyobject: Controller.__init__

reveals that :py:meth:`ctrl.Controller.__init__` calls
:py:meth:`ctrl.Controller.__reset__` after a couple of definitions.
	      
If you overload :py:meth:`ctrl.Controller.__reset` make sure to call::

    super().__reset()

before doing any other task. This will make sure that whatever tasks
that need to be performed by the base class have already taken place
and won't undo any of your own initialization.

The method :py:meth:`ctrl.Controller.__reset` is also called by the
method :py:meth:`ctrl.Controller.reset`. In fact, one rarely needs to
:py:overload any method other than :py:meth:`ctrl.Controller.__init__`
and :py:meth:`ctrl.Controller.__reset`.

A typical reason for extending :py:class:`ctrl.Controller` is to
provide the user with a set of devices that continue to exist even
after a call to :py:meth:`ctrl.Controller.reset`. For example, the
following code is from :py:meth:`ctrl.rc.mip.Controller`:

.. literalinclude:: ../ctrl/rc/mip.py
   :pyobject: Controller

which adds a number of devices to the base class
:py:meth:`ctrl.rc.Controller` that can be used with the Robotics Cape
and the Educational MIP as described in :ref:`Interfacing with Hardware`.

------------------------
Writting your own Blocks
------------------------

The package :py:mod:`ctrl` is designed so that you can easily extend
its functionality by writing simple python code for your own
blocks. You can write blocks to support your specific hardware or
implement an algorithm that is currently not available in
:ref:`Package-ctrl.block`.

Your blocks should inherit from :py:class:`ctrl.block.Block` or one of
its derived class, such as :py:class:`ctrl.block.BufferBlock`, which
are described next.

Extending :py:class:`ctrl.block.Block`
--------------------------------------

A :py:class:`ctrl.block.Block` needs to know how to do two things:
respond to calls to :py:meth:`ctrl.block.Block.read` and/or
:py:meth:`ctrl.block.Block.write`. If a block is to be used as a *source*
then it needs to respond to :py:meth:`ctrl.block.Block.read`, if it is to be
used as a *sink* it needs to respond to :py:meth:`ctrl.block.Block.write`,
and it if is to be used as a *filter* it needs to respond to both.

For example consider the following code for a simple block::

    import ctrl.block
  
    class MyOneBlock(ctrl.block.Block):

        def read(self):
	    return (1,)

that can be used as a *source* whose output *signal* is the constant
`1`. If you try to use :py:class:`MyOneBlock` as a *sink* an exception
will be raised since :py:class:`MyOneBlock` does not overload
:py:meth:`ctrl.block.Block.write`. Note that the return value of
:py:meth:`ctrl.block.Block.read` must be a tuple with numbers or numpy
1D-arrays. You could use your block in a controller like this::
  
    # add a MyOneBlock as a source
    controller.add_source('mysource',
                          MyOneBlock(),
			  ['signal'])

which would write `1` to the *signal* :py:data:`signal` every time the
controller loop is run.

Consider now the slightest more sophisticated block::

    import ctrl.block
    
    class MySumBlock(ctrl.block.Block):

        def __init__(self, **kwargs):

	    # you must call super().__init__
            super().__init__(**kwargs)

	    # create local buffer
	    self.buffer = ()
    
        def write(self, *values):

            # copy values to buffer
	    self.buffer = values
	    
        def read(self):

	    # return sum of all values as first entry
	    return (sum(self.buffer), )

Because :py:class:`MySumBlock` overloads both
:py:meth:`ctrl.block.Block.write` and :py:meth:`ctrl.block.Block.read`
it can be used a *filter*. For instance::
  
    # add a MySumBlock as a filter
    controller.add_filter('myfilter',
	                  MySumBlock(),
			  ['signal1','signal2','signal3'],
			  ['sum'])
		     
would set the *signal* :py:data:`sum` to be equal to the sum of the
three input *signals* :py:data:`signal1`, :py:data:`signal2`, and
:py:data:`signal3`. When placed in a controller loop, the loop will
first call :py:meth:`MySumBlock.write` then :py:meth:`MySumBlock.read`
as if running a code similar to the following::

    myfilter = MySymBlock()
    signal1 = 1
    signal2 = 2
    signal3 = 3

    myfilter.write(signal1, signal2, signal3)
    (sum, ) = myfilter.read()

At the end of a loop iteration the variable :py:data:`sum` would
contain the sum of the three variables :py:data:`signal1`,
:py:data:`signal2`, and :py:data:`signal3`. Of course the code run by
:py:class:`ctrl.Controller` is never explicitly expanded as above.
    
A couple of important details here. First
:py:meth:`MySumBlock.__init__` calls
:py:meth:`ctrl.block.Block.__init__` then proceeds to create its own
attribute :py:obj:`buffer`. Note that :py:meth:`ctrl.block.Block` does
not accept positional arguments, only keyword arguments. As you will
learn soon, this facilitates handling errors in the
constructor. Second the method :py:meth:`MySumBlock.write` should
always take a variable number of arguments, represented by the python
construction :samp:`*values`. Inside :py:meth:`MySumBlock.write` the
variable :py:data:`values` is a *tuple*. Third, because
:py:meth:`ctrl.block.Block.write` and :py:meth:`ctrl.block.Block.read`
are called separately, it is often the case that one needs an internal
variable to store values to be carried from
:py:meth:`ctrl.block.Block.write` to
:py:meth:`ctrl.block.Block.read`. This is so common that
:py:mod:`ctrl.block` provides a specialized class
:py:class:`ctrl.block.BufferBlock`, which you will learn about in the
next section.
    
Extending :py:class:`ctrl.block.BufferBlock`
--------------------------------------------

The class :py:class:`ctrl.block.BufferBlock` has several features that
can facilitate the implementation of blocks. First,:
py:meth:`ctrl.block.BufferBlock.buffer_read` and
:py:meth:`ctrl.block.BufferBlock.buffer_write` work with a an internal
attribute :py:obj:`buffer`, which can be used to carry values from
:py:meth:`ctrl.block.BufferBlock.buffer_write` to
:py:meth:`ctrl.block.BufferBlock.buffer_read`. Second, it support
*multiplexing* and *demultiplexing* of inputs. You will learn about
that later.


.. literalinclude:: ../ctrl/block/__init__.py
   :pyobject: Constant

.. literalinclude:: ../ctrl/rc/encoder.py
   :pyobject: Encoder

.. literalinclude:: ../ctrl/block/system.py 
   :pyobject: Sum



