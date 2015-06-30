from time import sleep
from ControllerClient import ControllerClient

with ControllerClient() as client:
    client.vector('1,2,3')
    #client.echo('Echo this message')
    #client.help()
    #client.get_status()
    #client.read_sensor()
    #client.set_encoder()
    #client.set_period(10)
    #client.set_echo_divisor(2)
    #client.run_loop(0)
    #client.set_motor_gain(3)
    #client.reverse_motor_direction()
    #client.set_PWM_frequency(1)
    #client.set_motor_curve(0)
    #client.start_stop_motor()
    #client.set_target(1)
    #client.set_target_zero(0)
    #client.read_target_potentiometer()
    #client.set_target_mode(1)
    #client.set_proportional_gain(4.1)
    #client.set_integral_gain(4.2)
    #client.set_derivative_gain(4.3)
    #client.control_mode(3)
    #client.start_stop_controller()
    #client.read_values()
    
