Module `ctrl.rc`
================

This module supports the hardware on the `Robotics Cape
<http://www.strawsondesign.com/>`_ running on a `Beaglebone Black
<https://beagleboard.org/black>`_ or a `Beaglebone Blue
<https://beagleboard.org/blue>`_. It also provides a controller suited
for the configuration of the `Educational MIP (Mobile Inverted
Pendulum) kit <https://github.com/StrawsonDesign/EduMiP>`_. For
installation instructions see Section :ref:`Installation`.

.. py:class:: ctrl.rc.Controller(**kwargs)

   :bases: :py:class:`ctrl.Controller`
	      
   :py:class:`ctrl.rc.Controller` initializes a controller for the Robotics Cape equiped with a clock based on the MPU9250 periodic interrupts.

   :param float period: period in seconds (default 0.01)
   :param kwargs: other keyword parameters

Module `ctrl.rc.encoder`
========================

.. py:class:: ctrl.rc.encoder.Encoder(**kwargs)

   :bases: :py:class:`ctrl.block.Block`
	      
   :py:class:`ctrl.rc.encoder.Encoder` provides an interface to the Beaglebone Black and Beaglebone Blue 3 hardware encoder counters.

   Thanks to the Robotics Cape library a fourth encoder counter is available through one of the PRUs.

   The attribute :py:attr:`ratio` can be used to set to the desired reading units.
   
   :param float ratio: multiplier (default 48 * 172)
   :param int encoder: encoder channel, 1 through 4 (default 2)
   :param kwargs: other keyword parameters

   .. py:method:: reset()

      Reset :py:class:`ctrl.rc.encoder.Encoder`.

      This function writes :py:data:`0` to the current encoder count register.
	
   .. py:method:: write(*values)
	     
      Write to Encoder.

      Set encoder count register to :py:data:`value[0]` multiplied by :py:data:`ratio`.
        
      :param varag values: values

   .. py:method:: read()
	     
      Read from Encoder.

      When encoder is enabled, returns the current encoder count register divided by :py:data:`ratio`.


Module `ctrl.rc.motor`
======================

.. py:class:: ctrl.rc.motor.Motor(**kwargs)

   :bases: :py:class:`ctrl.block.Block`
	      
   :py:class:`ctrl.rc.motor.Motor` provides an interface to the Robotics Cape 4 hardware PWM motor channels.
       
   With the default :py:attr:`ratio`, PWM values are from -100 to 100 but can be changed by modifying the attribute :py:attr:`ratio`.
   
   :param float ratio: ratio factor by which PMW is divided (default 100)
   :param int motor: motor channel, 1 through 4 (default 2)
   :param kwargs: other keyword parameters

   .. py:method:: set_enabled(enabled = True)

      Set *enabled* state.

      This function writes :py:data:`0` to the corresponding PWM channel when :py:data:`enabled` is :py:data:`False`.
	
      :param enabled: :py:data:`True` or :py:data:`False` (default :py:data:`True`)

   .. py:method:: write(*values)
	     
      Write to Motor.

      When motor is enabled, sets motor PWM :py:data:`value[0]` divided by :py:data:`ratio`.
        
      :param varag values: values

		   
Module `ctrl.rc.mpu9250`
========================

.. py:class:: ctrl.rc.mpu9250.MPU9250(**kwargs)

   :bases: :py:class:`ctrl.block.clock.Clock`
	      
   :py:class:`ctrl.rc.mpu9250.MPU9250` provides an interface to the Robotics Cape MPU9250 IMU.

   It inherits from :py:class:`ctrl.block.clock.Clock` and can be used as a clock.
      
   :param int accel_fsr: accelerometer full scale resolution
   :param int gyro_fsr: gyroscope full scale resolution
   :param int accel_dlpf: acellerometer low pass cutoff filter
   :param int gyro_dlpf: gyroscope low pass cutoff filter
   :param int orientation: orientation
   :param float compass_time_constant: compass time constant
   :param int dmp_interrupt_priority: DMP interrupt priority
   :param int period: DMP period in seconds
   :param bool enable_magnetometer: enable magnetometer
   :param bool enable_dmp: enable Digital Motion Processor
   :param bool enable_fusion: enable fusion algorithm
   :param bool show_warnings: show warnings
   :param kwargs: other keyword parameters

   .. py:method:: get_data():

      Return the data read by the IMU.

      :return: the IMU data
      
   .. py:method:: read()

      Read MPU9250.
      
      WARNING: This function does not return any IMU data, just a timestamp. Use :py:meth:`get_data` to get IMU data.
		  
      :return: time

.. py:class:: ctrl.rc.mpu9250.Raw(**kwargs)

   :bases: :py:class:`ctrl.block.BufferBlock`

   :py:class:`ctrl.rc.mpu9250.Raw` reads raw accelerometer and gyroscope angular velocity from the MPU9250 IMU.

   .. py:method:: read()
	     
      Read from IMU.

      When enabled, returns the current IMU linear acceleration and gyroscope angular velocities.

      :return: tuple with IMU acceleration and gyroscope angular velocities.
      
.. py:class:: ctrl.rc.mpu9250.Inclinometer(**kwargs)

   :bases: :py:class:`ctrl.rc.mpu9250.Raw`

   :py:class:`ctrl.rc.mpu9250.Inclinometer` reads the output from `ctrl.rc.mpu9250.Inclinometer` and returns the angle and angualar velocity with respect to the vertical.

   :param int turns: current number of turns (default 0)
   :param float threshold: used to detect that the IMU has been fliped more than 1 turn (360 degrees) (default 0.25 turns (90 deg))

   .. py:method:: read()
	     
      Read inclinometer.

      When enabled, returns the current angle and angular velocity measured with respect to the vertical.

      :return: tuple with angle and angular velocity.

Module `ctrl.rc.mip`
====================

.. py:class:: ctrl.rc.mip.Controller(**kwargs)

   :bases: :py:class:`ctrl.rc.Controller`
	      
   :py:class:`ctrl.rc.Controller` initializes a controller to be used with the Educational MIP connected to a Robotics Cape.

   The following devices are installed:

   1. Clock, :py:data:`clock`, based on interrupts generated by the
      MPU9250; installed as a *source*; output is the
      :py:data:`clock`;
   
   2. Inclinometer, :py:data:`inclinometer`, based on the MPU9250 IMU;
      installed as a *source*; outputs are the *signals*
      :py:data:`theta` and :py:data:`theta_dot`, which correspond to
      the angular position and velocity of the MIP; units are cycles
      and cycles/s;

   3. Two encoders, :py:data:`encoder1`, and :py:data:`encoder2`,
      installed as *sources*; outputs are the *signals*
      :py:data:`encoder1` and :py:data:`encoder2`, which correspond to
      relative angular displacement between the body of MIP and the
      axis of the left and right motors; units are cycles;

   4. Two motors, :py:data:`motor1`, and :py:data:`motor2`; installed
      as *sinks*; inputs are the PWM signals :py:data:`pwm1` and
      `py:data:`pwm2` driving the left and right motors of the MIP;
      range is from -100 to 100.
       
   :param float period: period in seconds (default 0.01)
   :param kwargs: other keyword parameters

