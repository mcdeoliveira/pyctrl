===================
More advanced usage
===================

The next sections describe tasks that are better suited to advanced
users, such as working with the provided Client-Server architecture,
extending Controllers, or writing your own Blocks. Make sure you have
gone through the :ref:`Tutorial` and have a good understanding of the
concepts discussed there before reading this chapter.

------------------------------
Qualified names and containers
------------------------------

Instances of the class :py:class:`pyctrl.block.container.Container`
can hold and execute *signals*, *sources*, *filters*, *sinks*, and
*timers*, just like an instance of
:py:class:`pyctrl.Controller`. Indeed :py:class:`pyctrl.Controller`
inherits most of its functionality from
:py:class:`pyctrl.block.container.Container`. An instance of
:py:class:`pyctrl.block.container.Container` works as a *filter*,
which can be installed using :py:class:`pyctrl.Controller.add_filter`
or :py:class:`pyctrl.Controller.add_device` or as a timer using
:py:class:`pyctrl.Controller.add_timer`.

As the name suggests, a :py:class:`pyctrl.block.container.Container`
can contain other blocks, just like a :py:class:`pyctrl.Controller`
does. In order to access elements inside a container one uses a
*qualified name* involving the special character forward slash
(`/`). For example, consider the following code::

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.system import Gain
    from pyctrl.block.container import Container, Input, Output

    # initialize controller
    controller = Controller(period = 1)

    controller.add_signals('s1','s2','s3')
  
    controller.add_filter('gain',
                          Gain(gain = 2),
                          ['s1'], ['s2'])

    # add container
    controller.add_filter('container',
                          Container(),
                          ['s1'], ['s3'])

    # add elements inside the container
    controller.add_signals('container/s1', 'container/s2')
    
    controller.add_source('container/input',
                          Input(),
                          ['s1'])
    
    controller.add_filter('container/gain',
                          Gain(gain = 3),
                          ['s1'],['s2'])
    
    controller.add_sink('container/output1',
                        Output(),
                        ['s2'])

The command::

    controller.add_filter('container',
                          Container(),
                          ['s1'], ['s3'])

adds a *filter* called :samp:`container` with input :samp:`s1` and
output :samp:`s3`. Once an instance of
:py:class:`pyctrl.block.container.Container` has been added to a
controller, its elements can be accessed by using a qualified name
which is preceded by the name of the container separated by a forward
slash (`/`). For example, the code::

    controller.add_signals('container/s1', 'container/s2')

adds two signals, :samp:`s1` and :samp:`s2`, to the container
:samp:`container`. Note that names inside containers are local,
:samp:`s1` and :samp:`container/s1` refer to different signals!

Likewise, the command::
      
    controller.add_filter('container/gain',
                          Gain(gain = 3),
                          ['s1'],['s2'])

adds a *filter* called :samp:`gain` to the container
:samp:`container`. Note that the *inputs* and *outputs* above refer to
signals which are *local* to :samp:`container`, that is the signals
:samp:`container/s1` and :samp:`container/s2`. In fact, the parameters
*inputs* and *outputs* in :py:class:`pyctrl.Controller.add_filter` as
well as :py:class:`pyctrl.Controller.add_source`,
:py:class:`pyctrl.Controller.add_sink`, and
:py:class:`pyctrl.Controller.add_device`, must all be local
symbols. In order to connect the inputs and output of the container
with signals of the controller we use two special blocks:
:py:class:`pyctrl.block.container.Input` and
:py:class:`pyctrl.block.container.Output`. For example::
      
    controller.add_source('container/input',
                          Input(),
                          ['s1'])

connects the single input of the container, the signal :samp:`s1` to
the local container signal :samp:`container/s1`, and::

    controller.add_sink('container/output1',
                        Output(),
                        ['s2'])

connects the local container signal :samp:`container/s2` to the single
output of the container, the signal :samp:`s3`.

The above controller corresponds to the following configuration:

.. code-block:: none
		
    <class 'pyctrl.timer.Controller'> with:
      0 timer(s), 6 signal(s),
      1 source(s), 2 filter(s), and 0 sink(s)
    > timers
    > signals
      1. clock
      2. duty
      3. is_running
      4. s1
      5. s2
      6. s3
    > sources
      1. clock[TimerClock, disabled] >> clock
    > filters
      1. s1 >> gain[Gain, enabled] >> s2
      2. s1 >> container[Container, disabled] >> s3
	 <class 'pyctrl.block.container.Container'> with:
	   0 timer(s), 2 signal(s),
	   1 source(s), 1 filter(s), and 1 sink(s)
	 > timers
	 > signals
	   1. s1
	   2. s2
	 > sources
	   1. input[Input, enabled] >> s1
	 > filters
	   1. s1 >> gain[Gain, enabled] >> s2
	 > sinks
	   1. s2 >> output1[Output, enabled]
    > sinks

Note how the contents of the container is shown indented. Executing::

    import time
    controller.set_signal('s1', 1)  
    with controller:
        time.sleep(1.1)

    print('s1 = {}'.format(controller.get_signal('s2')))
    print('s2 = {}'.format(controller.get_signal('s3')))

will produce:

.. code-block:: none

    s1 = 2
    s2 = 3

-------------------------------
Multiplexing and demultiplexing
-------------------------------

Blocks that are instances of :py:class:`pyctrl.block.BufferBlock`
support *multiplexing of inputs* and *demultiplexing of
outputs*.

*Multiplexing* means that all the inputs of a
:py:class:`pyctrl.block.BufferBlock` are collected into a single numpy
1D-array before the block is evaluated.

*Demultiplexing* means that the outputs of a
:py:class:`pyctrl.block.BufferBlock` are split into multiple outputs
after the block is evaluated.

For example, the blocks :py:class:`pyctrl.block.system.System` and
:py:class:`pyctrl.block.system.TimeVaryingSystem` always multiplexes
their input. This means that instances of
:py:class:`pyctrl.system.System` can seamlessly handle systems with
multiple inputs.

The attributes :py:attr:`mux` and :py:attr:`demux` can be also used to
modify the behavior of existing blocks. For this reason, you will
rarely need a special block for multiplexing and demultiplexing. If
you do, just use :py:class:`pyctrl.block.BufferBlock`. For example, a
mux-type block can be created by setting :py:obj:`demux = True` in a
:py:class:`pyctrl.block.BufferBlock` as in::

   from pyctrl.block import BufferBlock
   controller.add_filter('mux',
                         BufferBlock(mux = True),
			 ['input1','input2'],
			 ['muxout'])

Likewise, you could modify an existing block, such as
:py:class:`pyctrl.block.system.Gain` to demultiplex its outputs as in::
			 
   from pyctrl.block.system import Gain
   controller.add_filter('gain',
                         Gain(demux = True),
			 ['muxout'],
			 ['output1','output2'])

Because blocks can arbitrarily manipulate signals, it is not possible
to detect inconsistencies in the sizes of inputs and output until
execution time. Even then some blocks might simply ignore
discrepancies without generating any errors! For example, a block like::
		 
   controller.add_filter('gain',
                         Gain(),
			 ['input1'],
			 ['output1','output2'])

is not only valid but also does not generate any runtime
error. However, only the output :py:data:`output1` contains a multiple
of :py:data:`output2`. Since :py:data:`output2` does not match any
input it is simply ignored. Likewise, in::
			 			 
   controller.add_filter('gain',
                         Gain(),
			 ['input1','input2'],
			 ['output1'])

only the input :py:data:`intput1` gets passed on to the output
:py:data:`output1`. Again, no runtime errors are ever generated.

Finally, the block::
    		 
   controller.add_filter('gain',
                         Gain(gain = numpy.array([-1,2]), demux = True),
			 ['input1'],
			 ['output1','output2'])

leverages demultiplexing and the use of a numpy array as a gain to
produce a signal :py:data:`output1` which is :py:data:`input1`
multiplied by `-1` and a signal :py:data:`output2` which is
:py:data:`input1` multiplied by `2`.

			 
--------------------------------------
Client-Server Application Architecture
--------------------------------------

Since the beginnings of the development of this package one goal was
to be able to deploy and run controllers on embedded systems. With
that goal in mind we provide two special classes of controllers:
:py:class:`pyctrl.server.Controller` and
:py:class:`pyctrl.client.Controller`, and two scripts:
:samp:`pyctrl_start_server` and :samp:`pyctrl_stop_server` to start and
stop a controller server. Those scripts and classes can be combined to
run applications remotely.

Starting the server
-------------------

Start by using the script :samp:`pyctrl_start_server` to create a server
for you. In this tutorial, you will create a server on the same
machine you will be running the client. The process of initializing a
server on a remote machine is virtually identical. Type::

    pyctrl_start_server

which start the server and produces the following output:

.. code-block:: none
  
    pyctrl_start_server (version 1.0)
    > Options:
       Hostname[port]: localhost[9999]
      Sampling period: ---
        Verbose level: 1
    
    Type 'pyctrl_start_server -h' for more options
    
    <class 'pyctrl.Controller'> with:
      0 timer(s), 3 signal(s),
      1 source(s), 0 filter(s), and 0 sink(s)
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
    > Hit Ctrl-C or use 'pyctrl_stop_server' to exit the server

showing that a server has been started at the :py:data:`localhost` at
the port :py:data:`9999`. Those are the default values for `host` and
`port`. It also shows that the server is running a controller which is
an instance of the basic :py:class:`pyctrl.Controller` class.

The attribute :py:data:`host` is qualified name or valid IP address of
the machine you're connecting to and :py:data:`port` is the port you
would like to connect. The connection is established using a `TCP
network socket <https://en.wikipedia.org/wiki/Network_socket>`_. See
:ref:`Options available with pyctrl_start_server` for how to set these
options.


Connecting your client
----------------------

Start a new console and a new python shell. Proceed as in
Section :ref:`Hello World!` and create a controller::

    from pyctrl.client import Controller
    hello = Controller()

The only difference is that you imported :py:obj:`Controller` from the
class :py:class:`pyctrl.client.Controller`, as opposed to from
:py:class:`pyctrl.Controller`. Once you have initialized a controller as
a *client* and you have a controller running as a server,the flow is
very much like before. For example, we can query the controller using
:samp:`print(hello.info('all'))`, which in this case should reproduce
the exact same configuration of the controller running on the server:

.. code-block:: none
  
    pyctrl_start_server (version 1.0)
    > Options:
       Hostname[port]: localhost[9999]
      Sampling period: ---
	Verbose level: 1

    <class 'pyctrl.Controller'> with:
      0 timer(s), 3 signal(s),
      1 source(s), 0 filter(s), and 0 sink(s)
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
programming a local controller. However, there are some important caveats you should be aware of. For instance, attempting to install an instance :py:class:`pyctrl.block.clock.TimerClock` as a *source*  by typing::
    
    from pyctrl.block.clock import TimerClock
    hello.add_source('myclock',
		     TimerClock(period = 1),
		     ['myclock'])
		     
will fail. The reason for the failure is because an instance of the
class :py:class:`pyctrl.block.clock.TimerClock` cannot be safely
*transferred* from your hardware to another, that is from the *client*
to the *server*. Here is where the notion of a *device* comes in
handy. Instead of instantiating
:py:class:`pyctrl.block.clock.TimerClock` on the client, you can use
:py:meth:`pyctrl.Controller.add_device` to have the remote controller
instantiate it directly on the server hardware! As in Section
:ref:`Devices` type::

    hello.add_device('myclock',
                     'pyctrl.block.clock', 'TimerClock',
		     outputs = ['myclock'],
		     kwargs = {'period': 1},
		     enable = True)

to add a *device* :py:class:`pyctrl.block.clock.TimerClock` by letting
the remote server instantiate the object.

Alternatively, you can provide the optional parameters `module` and
`kwargs`::

    # initialize controller
    hello = Controller(host = 'localhost', port = 9999,
                       module = 'pyctrl.timer',
                       kwargs = {'period': 1})

which will install the controller of class
:py:class:`pyctrl.timer.Controller`, which already contains a
:py:class:`pyctrl.block.clock.TimerClock` clock, directly on the
server.

From this point on, just proceed as in :ref:`Hello World!` to add a
:py:class:`pyctrl.block.Printer`::
		     
    from pyctrl.block import Printer
    hello.add_sink('message',
		   Printer(message = 'Hello World!'),
		   ['myclock'],
		   enable = True)

and run the controller::

    import time
    with hello:
        # do nothing for 5 seconds
        time.sleep(5)

If you can't see anything happening for five seconds, look again. This
time not on the console running the *client*, but on the console
running the *server*. You should see the message `Hello World!`
printed there a couple of times. What you have accomplished is running
a task on the remote server controller by programming it on the client
controller. Effectively, and appart from some subtleties concerning
devices, the only difference was importing from
:py:class:`pyctrl.client.Controller` rather than from
:py:class:`pyctrl.Controller`.

What's under the hood?
----------------------
    
Before moving forward, a bit of a technical note. You might be
wondering why :py:class:`pyctrl.block.clock.TimerClock` could not be
added as a *source* but it is fine to add
:py:class:`pyctrl.block.Printer` as a *sink*. The difference has to do
with the ability of the client controller to *transfer* a block to the
remote controller. In order for that to process to happen, the block
:py:class:`pyctrl.block.Printer` has to be safely deconstructed, packed,
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

If you are curious why :py:class:`pyctrl.block.clock.TimerClock` could
not be serialized, it is because
:py:class:`pyctrl.block.clock.TimerClock` runs on a separate process
thread, and there is no way to simply transfer the thread information
over the network. As for :py:class:`pyctrl.block.Printer`, it is
possible to use its attributes to reconstruct it on the server
side.

Note that what decides if an object can be *pickled* or not is not its
base class but the contents of its attributes *at the time one
attempts to pickle it*. For example, a
:py:class:`pyctrl.block.Printer` in which you have setup the attribute
:py:attr:`file` to redirect its output to a local file will fail to
install as a *sink*. You could instead install it as a *device*, but
in this case, the output would be redirected to a file that lives in
the remote server rather than the local client.

A final note about serialization and `pickle` is that this process is
inherently unsafe from a security standpoint. Code that is embedded in
a serialized object can be used to take control of or damage the
server host by running malicious code. If security is a concern, it
must be addressed at the network level, before a client is allowed to
connect to a server, for example by setting up a firewall that
restricts connection to a know number of potential client addresses
combined with some strong form of authentication.


Options available with :samp:`pyctrl_start_server`
--------------------------------------------------

Starting :samp:`pyctrl_start_server` with the :py:data:`-h` flag displays
the options available:

.. code-block:: none

    usage: pyctrl_start_server [-h] [-m MODULE] [-c CONTROLLER] [-H HOST] [-p PORT]
			     [-v VERBOSE] [-t PERIOD]

    pyctrl_start_server (version 1.0)
    
    optional arguments:
      -h, --help            show this help message and exit (default: False)
      -m MODULE, --module MODULE
			    controller module (default: pyctrl)
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

    pyctrl_start_server -m pyctrl.timer

which initializes the server controller to be an instance of
:py:class:`pyctrl.timer.Controller` instead of the default
:py:data:`pyctrl.Controller`.

Another useful pair of options is :py:data:`-H`, :py:data:`--host` and
:py:data:`-p`, :py:data:`--port`, which can be used to change the
current host name or IP address and port. For example::

    pyctrl_start_server -m pyctrl.rc.mip -H 192.168.0.132 -p 9090

would initialize the server using an instance of
:py:class:`pyctrl.rc.mip.Controller` at the local network IP address
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

Working with :py:class:`pyctrl.client.Controller`
-------------------------------------------------

As shown above, working with an instance of
:py:class:`pyctrl.client.Controller` is for the most part identical to
working with any other instance of :py:class:`pyctrl.Controller`. In
this section you will learn a couple of useful practices when using a
client controller.

A first issue is setting the client to talk to the server at the right
address and port. This can be done by initializing the client with
attributes :py:attr:`host` and :py:attr:`port`. For example::
	
    from pyctrl.client import Controller
    client = Controller(host = '192.168.0.132', port = 9090)

would connect the client to a local network server at address
`192.168.0.132` and port `9090`.

Once connected, an usual mistake is to make assumptions about the
current state of a server controller. Since another client could have
connected to the server earlier and changed settings in unpredictable
ways, it might be useful to call
:py:meth:`pyctrl.client.Controller.reset` to *reset* the remote
controller at the server before doing anything::

    client.reset()

:py:meth:`pyctrl.client.Controller.reset` can also be used to install a
completely new controller on the server, as if using the :py:data:`-m`,
:py:data:`--module` and :py:data:`-c`, :py:data:`--controller` options
in :samp:`pyctrl_start_server`. For example::

    client.reset(module = 'pyctrl.timer')

install a new instance of :py:class:`pyctrl.timer.Controller` in the
remote server. You can query the server about its controller class by
using :py:meth:`pyctrl.Controller.info` as in::
    
    client.info('class')

which should then return the string :py:data:`"<class
'pyctrl.timer.Controller'>"`. You can also pass arguments to the
controller constructor. For example::

    client.reset(module = 'pyctrl.timer', kwargs = {'period': 0.1})

will install a new instance of :py:class:`pyctrl.timer.Controller`
running at 10 Hz on the remote server.

For convenience, all these operations can be performed by the
:py:class:`pyctrl.client.Controller` constructor. For example::
	
    from pyctrl.client import Controller
    client = Controller(host = '192.168.0.132', port = 9090,
                        module = 'pyctrl.timer',
			kwargs = {'period': 0.1})

initializes the client and resets the remote controller by installing
a new instance of :py:class:`pyctrl.timer.Controller` running at 10 Hz
on the remote server.

SSH and port forwarding
-----------------------

A common setup is that of a server running on an embedded system, such
as a Beaglebone Black or a Raspberry Pi, controlled remotely by a
computer. In most cases, connections to the server will be established
using `ssh <https://en.wikipedia.org/wiki/Secure_Shell>`_.

The following is a typical session: the user on the client computer,
`user@client`, establishes a connection to the remote server, in this
case a Beaglebone Black as `root@192.168.0.68`, using ssh:

.. code-block:: none
		
    user@client:~$ ssh -L9999:localhost:9999 root@192.168.0.68
    Debian GNU/Linux 8

    BeagleBoard.org Debian Image 2016-11-06

    Support/FAQ: http://elinux.org/Beagleboard:BeagleBoneBlack_Debian

    default username:password is [debian:temppwd]

    Last login: Sat Apr  1 17:06:08 2017 from 192.168.0.1
    root@beaglebone:~#

The important detail here is the argument
:samp:`-L9999:localhost:9999`, which tells ssh to establish a
*tunnel*, that is to `forward the port 9999
<https://www.ssh.com/ssh/tunneling/example>`_ from the server to the
client.
    
Because of that, the user can initiate the server using
:samp:`localhost` as its host name:

.. code-block:: none
		
    root@beaglebone:~# pyctrl_start_server
    pyctrl_start_server (version 1.0)

    Type 'pyctrl_start_server -h' for more options

    > Options:
       Hostname[port]: localhost[9999]
      Sampling period: ---
	Verbose level: 1

    <class 'pyctrl.Controller'> with:
      0 timer(s), 3 signal(s),
      1 source(s), 0 filter(s), and 0 sink(s)
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
    > Hit Ctrl-C or use 'pyctrl_stop_server' to exit the server

After starting the server, on another terminal, the user runs his
application as a client, also connected to :samp:`localhost`. For
example, using the interactive shell:

.. code-block:: none
		
    user@client:~$ python
    Python 3.4.5 |Anaconda 2.3.0 (x86_64)| (default, Jul  2 2016, 17:47:57) 
    [GCC 4.2.1 Compatible Apple LLVM 4.2 (clang-425.0.28)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pyctrl.client import Controller
    >>> hello = Controller()
    >>> print(hello.info('all'))
    <class 'pyctrl.Controller'> with:
      0 timer(s), 3 signal(s),
      1 source(s), 0 filter(s), and 0 sink(s)
    > timers
    > signals
      1. clock
      2. duty
      3. is_running
    > sources
      1. clock[Clock, enabled] >> clock
    > filters
    > sinks

    >>> quit()
    user@client:~$ 

In this way, all network traffic is managed by ssh. An additional
advantage is that this traffic is also `encrypted and potentially
compressed <http://www.linuxjournal.com/article/6602>`_, which adds
efficiency and security to the entire session. With ssh you can also
forward your X graphics terminal using the :samp:`-X` flag. For
example:
        
.. code-block:: none
		
    ssh -X -L9999:localhost:9999 root@192.168.0.68

would forward both the 9999 port and your X terminal session.


--------------------------
Performance considerations
--------------------------

Error Handling
--------------

Since you're using Python, error testing and handling can be kept at a
minimum. Thanks to `duck typing
<https://en.wikipedia.org/wiki/Duck_typing>`_ and other Python
features, anything that could go wrong will be dealt with at execution
time, with errors being propagated using the standard Python
`exception <https://docs.python.org/3/tutorial/errors.html>`_
mechanism. As discussed in Section :ref:`whatsgoingon`, users can
handle errors by enclosing segments of code using the :py:obj:`try`
statement::

    try:
        # do something
        ...
	
    except:
        # do something if exception was raised
	...
	
    finally:
        # always do this 
	...

Most of the time, error checking is limited to operations that could
invalidate your controller. In particular, very few error checking
tests are performed in the methods :py:meth:`pyctrl.block.Block.read`
and :py:meth:`pyctrl.block.Block.write`. Such tests would be repeated in
the main controller loop and could potentially impact performance. If
you need to perform tests in those methods consider using `assertions
<https://wiki.python.org/moin/UsingAssertionsEffectively>`_. This
means that those tests could be completely turned off if they are
impacting performance by invoking Python with the :samp:`-O` flag.


---------------------
Extending Controllers
---------------------

One can take advantage of python's object oriented features to extend
the functionality of the basic :py:class:`pyctrl.Controller`. All that
is necessary is to inherit from
:py:class:`pyctrl.Controller`.

Inheritance is an easy way to equip controllers with special hardware
capabilities. That was the case, for example, with the class
:py:class:`pyctrl.timer.Controller` described in :ref:`Devices`. In
fact, this new class is so simple that its entire code easily fits
here:

.. literalinclude:: ../pyctrl/timer.py
   :pyobject: Controller

Virtually all functionality is provided by the base class
:py:class:`pyctrl.Controller`. The only methods overloaded are
:py:meth:`pyctrl.Controller.__init__` and
:py:meth:`pyctrl.Controller._reset`.

The method :py:meth:`pyctrl.timer.Controller.__init__` is the standard
python constructor, which in this case parses the new attribute
:py:attr:`period` before calling the base class
:py:meth:`pyctrl.Controller.__init__` using::
      
      super().__init__(**kwargs)

Note that this is done using `pop
<https://docs.python.org/3/library/stdtypes.html#dict>`_ as in::

    self.period = kwargs.pop('period', 0.01)

Using :py:meth:`pop` makes sure the keyword :py:data:`period` is
removed from the dictionary :py:data:`kwargs`. Any remaining keywords
need to be valid attributes of the base class or an exception will be
raised.

Most of the action is in the method
:py:meth:`pyctrl.Controller._reset`. In fact, a closer look at
:py:meth:`pyctrl.block.container.Controller.__init__`, which is the
method called by :samp:`super().__init__(**kwargs)` in
:py:meth:`pyctrl.Controller.__init__`, reveals:

.. literalinclude:: ../pyctrl/block/container.py
   :pyobject: Container.__init__

where a call to the method :py:meth:`pyctrl.Controller._reset` can be
spotted after a couple of definitions.
	      
If you overload :py:meth:`pyctrl.Controller._reset` make sure to call::

    super()._reset()

*before* doing any other task. This will make sure that whatever tasks
that need to be performed by the base class have already taken place
and won't undo any of your own initialization.

The method :py:meth:`pyctrl.Controller._reset` is also called by the
method :py:meth:`pyctrl.Controller.reset`. In fact, one rarely needs to
overload any method other than :py:meth:`pyctrl.Controller.__init__` and
:py:meth:`pyctrl.Controller._reset`.

A typical reason for extending :py:class:`pyctrl.Controller` is to
provide the user with a set of devices that continue to exist even
after a call to :py:meth:`pyctrl.Controller.reset`. For example, the
following code is from :py:meth:`pyctrl.rc.mip.Controller`:

.. literalinclude:: ../pyctrl/rc/mip.py
   :pyobject: Controller

which adds a number of devices to the base class
:py:meth:`pyctrl.rc.Controller` that can be used with the Robotics Cape
and the Educational MIP as described in :ref:`Interfacing with Hardware`.

------------------------
Writting your own Blocks
------------------------

The package :py:mod:`pyctrl` is designed so that you can easily extend
its functionality by writing simple python code for your own
blocks. You can write blocks to support your specific hardware or
implement an algorithm that is currently not available in
:ref:`Module pyctrl.block`.

Your blocks should inherit from :py:class:`pyctrl.block.Block` or one of
its derived class, such as :py:class:`pyctrl.block.BufferBlock`, which
are described next.

Extending :py:class:`pyctrl.block.Block`
----------------------------------------

A :py:class:`pyctrl.block.Block` needs to know how to do two things:
respond to calls to :py:meth:`pyctrl.block.Block.read` and/or
:py:meth:`pyctrl.block.Block.write`. If a block is to be used as a *source*
then it needs to respond to :py:meth:`pyctrl.block.Block.read`, if it is to be
used as a *sink* it needs to respond to :py:meth:`pyctrl.block.Block.write`,
and it if is to be used as a *filter* it needs to respond to both.

For example consider the following code for a simple block::

    import pyctrl.block
  
    class MyOneBlock(pyctrl.block.Source, pyctrl.block.Block):

        def read(self):
	    return (1,)

Multiple inheritance is used to make sure this block can only be used
as a *source* by inheriting from :py:class:`pyctrl.block.Source` *and*
:py:class:`pyctrl.block.Block`. The order is important! If you try to
use :py:class:`MyOneBlock` as a *sink* or a *filter* an exception will
be raised since :py:class:`MyOneBlock` does not overload
:py:meth:`pyctrl.block.Block.write`. Likewise, *sinks* must inherit
from :py:class:`pyctrl.block.Sink` and *filters* from
:py:class:`pyctrl.block.Filter`.

All this block does is output a *signal* which is the constant `1`.
Note that the return value of :py:meth:`pyctrl.block.Block.read` must
be a tuple with numbers or numpy 1D-arrays. You could use your block
in a controller like this::
  
    # add a MyOneBlock as a source
    controller.add_source('mysource',
                          MyOneBlock(),
			  ['signal'])

which would write `1` to the *signal* :py:data:`signal` every time the
controller loop is run.

Consider now the slightest more sophisticated block::

    import pyctrl.block
    
    class MySumBlock(pyctrl.block.Filter, pyctrl.block.Block):

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

Because :py:class:`MySumBlock` inherits from
:py:class:`pyctrl.block.Filter` if can be be used a *filter*. It must
therefore overload both :py:meth:`pyctrl.block.Block.write` and
:py:meth:`pyctrl.block.Block.read`. For instance::
  
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

    myfilter.write(signal1, signal2, signal3)
    (sum, ) = myfilter.read()

At the end of a loop iteration the variable :py:data:`sum` would
contain the sum of the three variables :py:data:`signal1`,
:py:data:`signal2`, and :py:data:`signal3`. Of course the code run by
:py:class:`pyctrl.Controller` is never explicitly expanded as above.
    
A couple of important details here. First
:py:meth:`MySumBlock.__init__` calls
:py:meth:`pyctrl.block.Block.__init__` then proceeds to create its own
attribute :py:obj:`buffer`. Note that :py:meth:`pyctrl.block.Block` does
not accept positional arguments, only keyword arguments. As you will
learn soon, this facilitates handling errors in the
constructor. Second the method :py:meth:`MySumBlock.write` should
always take a variable number of arguments, represented by the python
construction :samp:`*values`. Inside :py:meth:`MySumBlock.write` the
variable :py:data:`values` is a `tuple
<https://docs.python.org/3/tutorial/datastructures.html>`_. Third,
because :py:meth:`pyctrl.block.Block.write` and
:py:meth:`pyctrl.block.Block.read` are called separately, it is often
the case that one needs an internal variable to store values to be
carried from :py:meth:`pyctrl.block.Block.write` to
:py:meth:`pyctrl.block.Block.read`. This is so common that
:py:mod:`pyctrl.block` provides a specialized class
:py:class:`pyctrl.block.BufferBlock`, which you will learn about in the
next section.
    
Extending :py:class:`pyctrl.block.BufferBlock`
----------------------------------------------

The class :py:class:`pyctrl.block.BufferBlock` has several features that
can facilitate the implementation of blocks. First,
py:meth:`pyctrl.block.BufferBlock.read` and
:py:meth:`pyctrl.block.BufferBlock.write` work with a an internal
attribute :py:obj:`buffer`, which can be used to carry values from
:py:meth:`pyctrl.block.BufferBlock.write` to
:py:meth:`pyctrl.block.BufferBlock.read`. Second, it support
*multiplexing* and *demultiplexing* of inputs as discussed in Section
:ref:`Multiplexing and demultiplexing`.

Consider as an example the block :py:class:`pyctrl.block.system.Gain`,
which produces an output which correspond to its inputs multiplied by
a fixed *gain*. Because :py:class:`pyctrl.block.system.Gain` does
nothing to its inputs when it is written it does not overload
:py:meth:`pyctrl.block.BufferBlock.write`. All the action is on the
method :py:meth:`pyctrl.block.system.Gain.write`:

.. literalinclude:: ../pyctrl/block/system.py 
   :pyobject: Gain.write

Note that it starts by calling :samp:`super().write(*values)`, which
will take care of any multiplexing at the input, followed by the
actual calculation, which in this case is performed using a `list
comprehension
<https://docs.python.org/3/tutorial/datastructures.html#tut-listcomps>`_::

  self.buffer = tuple(v * self.gain for v in self.buffer)

that produces the desired output tuple.

For another example consider the block
:py:class:`pyctrl.block.system.Sum` and its method
:py:meth:`pyctrl.block.system.Sum.write`:

.. literalinclude:: ../pyctrl/block/system.py 
   :pyobject: Sum.write

The only new detail here is the use of :samp:`super(Gain,
self).write(*values)`. This is because
:py:class:`pyctrl.block.system.Sum` inherits from
:py:class:`pyctrl.block.system.Gain`, and you would like to call
:py:meth:`pyctrl.block.BufferBlock.write` instead of
:py:meth:`pyctrl.block.system.Gain.write`.

