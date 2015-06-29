import sys
from time import sleep
from ControllerClient import ControllerClient

with ControllerClient() as client:

    print('Hi\n')

    for line in sys.stdin:

        # clean line
        line = line.strip()
        print('> line = ', line)

        if line[0] == 'e':
            client.echo(str(line[1:]))
        elif line[0] == 'H':
            client.help()
        elif line[0] == 's':
            client.get_status()
        elif line[0] == 'R':
            client.read_sensor()
        elif line[0] == 'Z':
            client.set_encoder()
        elif line[0] == 'P':
            client.set_period(int(line[1:]))
        elif line[0] == 'E':
            client.set_echo_divisor(int(line[1:]))
        elif line[0] == 'L':
            client.run_loop(int(line[1:]))
        elif line[0] == 'G':
            client.set_motor_gain(int(line[1:]))
        elif line[0] == 'V':
            client.reverse_motor_direction()
        elif line[0] == 'F':
            client.set_PWM_frequency(int(line[1:]))
        elif line[0] == 'Q':
            client.set_motor_curve(int(line[1:]))
        elif line[0] == 'M':
            client.start_stop_motor()
        elif line[0] == 'T':
            client.set_target(int(line[1:]))
        elif line[0] == 'B':
            client.set_target_zero(int(line[1:]))
        elif line[0] == 'O':
            client.read_target_potentiometer()
        elif line[0] == 'D':
            client.set_target_mode(int(line[1:]))
        elif line[0] == 'K':
            client.set_proportional_gain(float(line[1:]))
        elif line[0] == 'I':
            client.set_integral_gain(float(line[1:]))
        elif line[0] == 'N':
            client.set_derivative_gain(float(line[1:]))
        elif line[0] == 'Y':
            client.control_mode(int(line[1:]))
        elif line[0] == 'C':
            client.start_stop_controller()
        elif line[0] == 'r':
            client.read_values()
        elif line[0] == 'u':
            client.array(str(line[1:]))
        elif line[0] == 'X':
            break
            
print('Bye')




