import pytest

import time, math

try:
    
    import rcpy
    #rcpy.set_state(rcpy.RUNNING)

    def run_clock(Ts):

        import pyctrl.rc.mpu9250 as mpu9250

        clock = mpu9250.MPU9250()
        clock.set(period = Ts)

        print("\n> Testing Clock @{} Hz".format(1/Ts))

        N = int(5/Ts)
        (t0,) = clock.read()
        avg = 0
        mx = 0
        for k in range(1,N):

            (t1,) = clock.read()
            dt = 1000 * (t1 - t0)
            t0 = t1
            avg = ((k-1)/k) * avg + (1/k) * dt
            mx = max(dt, mx)
            print('\r dt = {:7.3f} ms  average = {:7.3f} ms   max = {:7.3f} ms'.format(dt, avg, mx), end='')

        assert avg < Ts*1000
        assert mx < 2*Ts*1000
        assert avg > 0.8*Ts*1000

    def test_clock():

        run_clock(0.01)
        run_clock(0.25)

        # change period
        import pyctrl.rc.mpu9250 as mpu9250

        clock = mpu9250.MPU9250()

        clock.set(period = 0.02)
        assert clock.get('period') == 0.02
        
        clock.set(period = 0.01)
        assert clock.get('period') == 0.01

        clock.set(period = 0.005)
        assert clock.get('period') == 0.005
        
    def test_controller():

        from pyctrl.rc import Controller

        # initialize controller
        Ts = 0.01
        bbb = Controller(period = Ts)

        assert set(bbb.list_devices()) == set(['clock'])
        assert set(bbb.list_timers()) == set([])
        assert set(bbb.list_signals()) == set(['clock','duty','is_running'])
        assert set(bbb.list_sources()) == set(['clock'])
        assert set(bbb.list_filters()) == set([])
        assert set(bbb.list_sinks()) == set([])

        assert bbb.get_source('clock','period') == 0.01

    def test_mip():

        from pyctrl.rc.mip import Controller

        # initialize controller
        Ts = 0.01
        bbb = Controller(period = Ts)

        assert set(bbb.list_devices()) == set(['clock','inclinometer','encoder1','encoder2','motor1','motor2'])
        assert set(bbb.list_timers()) == set([])
        assert set(bbb.list_signals()) == set(['clock','duty','is_running','encoder1','encoder2','pwm1','pwm2','theta','theta_dot'])
        assert set(bbb.list_sources()) == set(['clock','inclinometer','encoder1','encoder2'])
        assert set(bbb.list_filters()) == set([])
        assert set(bbb.list_sinks()) == set(['motor1','motor2'])
        
        assert bbb.get_source('clock','period') == 0.01

    def test_mpu9500():

        import pyctrl.block as block
        import pyctrl.rc.mpu9250 as mpu9250

        clock = mpu9250.MPU9250()
        clock.set(period = 0.25)

        imu = mpu9250.Raw()
        data = imu.read()
        
        assert len(data) == 2
        assert len(data[0]) == 3
        assert len(data[1]) == 3

        imu = mpu9250.Inclinometer()
        data = imu.read()

        assert len(data) == 2
        assert isinstance(data[0], float)
        assert isinstance(data[1], float)

        # get and set
        imu.set(turns = 1, threshold = 0.1)

        assert imu.get('turns', 'threshold') == {'turns': 1, 'threshold': 0.1}

        with pytest.raises(block.BlockException):
            imu.set(theta = 1)
        
except Exception as e:

    print('Exception raised: {}'.format(e))

    print('> rcpy library not installed, skipping test...')
    
    def test():
        pass
        
