===================
More advanced usage
===================

The next sections describe tasks that are better suited to advanced
users, such as extending Controllers or writing your own Blocks. Make
sure you have gone through the :ref:`Tutorial` and have a good
understanding of the concepts discussed there before reading this
chapter.

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

.. literalinclude:: ../python/ctrl/timer.py
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

.. literalinclude:: ../python/ctrl/__init__.py
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

.. literalinclude:: ../python/ctrl/rc/mip.py
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


.. literalinclude:: ../python/ctrl/block/__init__.py
   :pyobject: Constant

.. literalinclude:: ../python/ctrl/rc/encoder.py
   :pyobject: Encoder

    
.. literalinclude:: ../python/ctrl/block/system.py 
   :pyobject: Sum



