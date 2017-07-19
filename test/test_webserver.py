start_server = True
#start_server = False

def test_webserver():

    import subprocess
    import time
    import numpy
    from pyctrl.flask.server import JSONDecoder, JSONEncoder
        
    if start_server:
        
        # initiate server
        print('> Starting server')

        server = subprocess.Popen(["python3",
                                   "pyctrl/flask/server.py"],
                                  stdout = subprocess.PIPE)
        
        time.sleep(2)

    try:

        # reset controller
        url = "http://127.0.0.1:5000/reset"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer
        
        # check index page
        answer = b"<div><p>&lt;class 'pyctrl.timer.Controller'&gt; with: 0 timer(s), 3 signal(s), 1 source(s), 0 filter(s), and 0 sink(s)</p><h2>timers</h2><ol></ol><h2>signals</h2><ol><li>clock</li><li>duty</li><li>is_running</li></ol><h2>sources</h2><ol><li>clock[TimerClock, disabled] &Gt; clock</li></ol><h2>filters</h2><ol></ol><h2>sinks</h2><ol></ol></div>"

        # check info page
        url = "http://127.0.0.1:5000/info"
        output = subprocess.check_output(["curl", url])
        assert output == answer

        # S I N K S
        
        # add sink
        url = r'"http://127.0.0.1:5000/add/sink/printer/pyctrl.block/Printer?inputs=\[\"clock\",\"is_running\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get sink
        url = "http://127.0.0.1:5000/get/sink/printer"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)

        from pyctrl.block import Printer
        assert result['printer'].get() == Printer().get()

        # get attribute/sink
        url = r'"http://127.0.0.1:5000/get/sink/printer?keys=\"enabled\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True}

        assert result == answer

        # get attribute/sink (multiple)
        url = '"http://127.0.0.1:5000/get/sink/printer?keys=\[\\"enabled\\",\\"endln\\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'endln': '\n'}

        assert result == answer
        
        # set attribute/sink
        url = 'http://127.0.0.1:5000/set/sink/printer?enabled=false'
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/sink
        url = '"http://127.0.0.1:5000/get/sink/printer?keys=\\"enabled\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': False}

        assert result == answer
        
        # set attribute/sink
        url = '"http://127.0.0.1:5000/set/sink/printer?endln=\\"\\r\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/sink
        url = '"http://127.0.0.1:5000/get/sink/printer?keys=\\"endln\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'endln': '\r'}

        assert result == answer
        
        # set attribute/sink (multiple)
        url = '"http://127.0.0.1:5000/set/sink/printer?enabled=true&endln=\\"\\r\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/sink (multiple)
        url = '"http://127.0.0.1:5000/get/sink/printer?keys=\[\\"enabled\\",\\"endln\\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'endln': '\r' }

        assert result == answer
        
        # add sink with parameter
        url = r'"http://127.0.0.1:5000/add/sink/printer/pyctrl.block/Printer?inputs=\[\"clock\",\"is_running\"\]&kwargs=\{\"endln\":\"\\r\"\}"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/sink (multiple)
        url = '"http://127.0.0.1:5000/get/sink/printer?keys=\[\\"enabled\\",\\"endln\\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'endln': '\r' }

        assert result == answer
        
        # S O U R C E
        
        # add source
        url = r'"http://127.0.0.1:5000/add/source/constant/pyctrl.block/Constant?outputs=\[\"signal\"\]&kwargs=\{\"value\":3\}"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get source
        url = "http://127.0.0.1:5000/get/source/constant"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)

        from pyctrl.block import Constant
        assert result['constant'].get() == Constant(value = 3).get()

        # get attribute/source
        url = r'"http://127.0.0.1:5000/get/source/constant?keys=\"enabled\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True}

        assert result == answer

        # get attribute/source (multiple)
        url = r'"http://127.0.0.1:5000/get/source/constant?keys=\[\"enabled\",\"value\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'value': 3}

        assert result == answer
        
        # set attribute/source
        url = 'http://127.0.0.1:5000/set/source/constant?enabled=false'
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/source
        url = '"http://127.0.0.1:5000/get/source/constant?keys=\\"enabled\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': False}

        assert result == answer
        
        # set attribute/source
        url = '"http://127.0.0.1:5000/set/source/constant?value=4"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/source
        url = '"http://127.0.0.1:5000/get/source/constant?keys=\\"value\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'value': 4}

        assert result == answer
        
        # set attribute/source (multiple)
        url = '"http://127.0.0.1:5000/set/source/constant?enabled=true&value=5"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/source (multiple)
        url = '"http://127.0.0.1:5000/get/source/constant?keys=\[\\"enabled\\",\\"value\\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'value': 5 }

        assert result == answer

        # F I L T E R
        
        # add filter
        url = r'"http://127.0.0.1:5000/add/filter/gain/pyctrl.block.system/Gain?inputs=\[\"inp\"\]&outputs=\[\"out\"\]&kwargs=\{\"gain\":3\}"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get filter
        url = "http://127.0.0.1:5000/get/filter/gain"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)

        from pyctrl.block.system import Gain
        assert result['gain'].get() == Gain(gain = 3).get()

        # get attribute/filter
        url = r'"http://127.0.0.1:5000/get/filter/gain?keys=\"enabled\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True}

        assert result == answer

        # get attribute/filter (multiple)
        url = r'"http://127.0.0.1:5000/get/filter/gain?keys=\[\"enabled\",\"gain\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'gain': 3}

        assert result == answer
        
        # set attribute/filter
        url = 'http://127.0.0.1:5000/set/filter/gain?enabled=false'
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/filter
        url = '"http://127.0.0.1:5000/get/filter/gain?keys=\\"enabled\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': False}

        assert result == answer
        
        # set attribute/filter
        url = '"http://127.0.0.1:5000/set/filter/gain?gain=4"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/filter
        url = '"http://127.0.0.1:5000/get/filter/gain?keys=\\"gain\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'gain': 4}

        assert result == answer
        
        # set attribute/filter (multiple)
        url = '"http://127.0.0.1:5000/set/filter/gain?enabled=true&gain=5"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/filter (multiple)
        url = '"http://127.0.0.1:5000/get/filter/gain?keys=\[\\"enabled\\",\\"gain\\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'gain': 5 }

        assert result == answer
        
        # T I M E R
        
        # add timer
        url = r'"http://127.0.0.1:5000/add/timer/gain/pyctrl.block.system/Gain?inputs=\[\"inp\"\]&outputs=\[\"out\"\]&kwargs=\{\"gain\":3\}&period=1"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get timer
        url = "http://127.0.0.1:5000/get/timer/gain"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)

        from pyctrl.block.system import Gain
        assert result['gain'].get() == Gain(gain = 3).get()

        # get attribute/timer
        url = r'"http://127.0.0.1:5000/get/timer/gain?keys=\"enabled\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True}

        assert result == answer

        # get attribute/timer (multiple)
        url = r'"http://127.0.0.1:5000/get/timer/gain?keys=\[\"enabled\",\"gain\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'gain': 3}

        assert result == answer
        
        # set attribute/timer
        url = 'http://127.0.0.1:5000/set/timer/gain?enabled=false'
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/timer
        url = '"http://127.0.0.1:5000/get/timer/gain?keys=\\"enabled\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': False}

        assert result == answer
        
        # set attribute/timer
        url = '"http://127.0.0.1:5000/set/timer/gain?gain=4"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/timer
        url = '"http://127.0.0.1:5000/get/timer/gain?keys=\\"gain\\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'gain': 4}

        assert result == answer
        
        # set attribute/timer (multiple)
        url = '"http://127.0.0.1:5000/set/timer/gain?enabled=true&gain=5"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer

        # get attribute/timer (multiple)
        url = '"http://127.0.0.1:5000/get/timer/gain?keys=\[\\"enabled\\",\\"gain\\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'enabled': True, 'gain': 5 }

        assert result == answer

        answer = b"<div><p>&lt;class 'pyctrl.timer.Controller'&gt; with: 1 timer(s), 6 signal(s), 2 source(s), 1 filter(s), and 1 sink(s)</p><h2>timers</h2><ol><li>inp &Gt; gain[Gain, period = 1, repeat, enabled] &Gt; out</li></ol><h2>signals</h2><ol><li>clock</li><li>duty</li><li>inp</li><li>is_running</li><li>out</li><li>signal</li></ol><h2>sources</h2><ol><li>clock[TimerClock, disabled] &Gt; clock</li><li>constant[Constant, enabled] &Gt; signal</li></ol><h2>filters</h2><ol><li>inp &Gt; gain[Gain, enabled] &Gt; out</li></ol><h2>sinks</h2><ol><li>clock, is_running &Gt; printer[Printer, enabled]</li></ol></div>"
        
        # check info page
        url = "http://127.0.0.1:5000/info"
        output = subprocess.check_output(["curl", url])

        assert output == answer
        
        # reset controller
        
        url = "http://127.0.0.1:5000/set/controller/pyctrl/Controller"
        output = subprocess.check_output(["curl", url]).decode("utf-8")

        answer = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="/">/</a>.  If not click the link.'
        
        assert output == answer
        
        # check info page
        url = "http://127.0.0.1:5000/info"
        output = subprocess.check_output(["curl", url])

        answer = b"<div><p>&lt;class 'pyctrl.Controller'&gt; with: 0 timer(s), 3 signal(s), 1 source(s), 0 filter(s), and 0 sink(s)</p><h2>timers</h2><ol></ol><h2>signals</h2><ol><li>clock</li><li>duty</li><li>is_running</li></ol><h2>sources</h2><ol><li>clock[Clock, disabled] &Gt; clock</li></ol><h2>filters</h2><ol></ol><h2>sinks</h2><ol></ol></div>"
        
        assert output == answer
        
        # reset controller
        url = "http://127.0.0.1:5000/set/controller/pyctrl.timer/Controller?kwargs=\{\"period\":1\}"
        output = subprocess.check_output(["curl", url]).decode("utf-8")

        answer = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="/">/</a>.  If not click the link.'

        assert output == answer

        # get attribute/timer
        url = r'"http://127.0.0.1:5000/get/source/clock?keys=\"period\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'period': 1}
        
        assert result == answer

        # add logger
        url = r'"http://127.0.0.1:5000/add/sink/logger/pyctrl.block/Logger?inputs=\[\"clock\",\"is_running\"\]"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer
       
        # start
        url = "http://127.0.0.1:5000/start"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer

        time.sleep(3)
        
        # stop
        url = "http://127.0.0.1:5000/stop"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer

        # get log
        url = r'"http://127.0.0.1:5000/get/sink/logger?keys=\"log\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)['log']

        assert isinstance(result['clock'], numpy.ndarray)
        assert isinstance(result['is_running'], numpy.ndarray)
        assert result['is_running'].shape == result['clock'].shape
        assert result['clock'].shape[0] >= 3
        assert result['clock'].shape[1] == 1
        assert result['clock'][-1,0] - result['clock'][0,0] < 4
        
        # start
        url = "http://127.0.0.1:5000/start"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer

        time.sleep(3)
        
        # stop
        url = "http://127.0.0.1:5000/stop"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer
        
        # get log
        url = r'"http://127.0.0.1:5000/get/sink/logger?keys=\"log\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)['log']

        assert isinstance(result['clock'], numpy.ndarray)
        assert isinstance(result['is_running'], numpy.ndarray)
        assert result['is_running'].shape == result['clock'].shape
        assert result['clock'].shape[0] > 6
        assert result['clock'].shape[1] == 1
        assert result['clock'][-1,0] - result['clock'][0,0] > 6
        
        # add logger with auto_reset
        url = r'"http://127.0.0.1:5000/add/sink/logger/pyctrl.block/Logger?inputs=\[\"clock\",\"is_running\"\]&kwargs=\{\"auto_reset\":true\}"'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}

        assert result == answer
       
        # start
        url = "http://127.0.0.1:5000/start"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer

        time.sleep(3)
        
        # stop
        url = "http://127.0.0.1:5000/stop"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer

        # get log
        url = r'"http://127.0.0.1:5000/get/sink/logger?keys=\"log\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)['log']

        print('log = {}'.format(result))
        
        assert isinstance(result['clock'], numpy.ndarray)
        assert isinstance(result['is_running'], numpy.ndarray)
        assert result['is_running'].shape == result['clock'].shape
        assert result['clock'].shape[0] >= 3
        assert result['clock'].shape[1] == 1
        assert result['clock'][-1,0] - result['clock'][0,0] < 4
        
        # start
        url = "http://127.0.0.1:5000/start"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer

        time.sleep(3)
        
        # stop
        url = "http://127.0.0.1:5000/stop"
        output = subprocess.check_output(["curl", url]).decode("utf-8")
        result = JSONDecoder().decode(output)
        answer = {'status': 'success'}
        
        assert result == answer
        
        # get log
        url = r'"http://127.0.0.1:5000/get/sink/logger?keys=\"log\""'
        output = subprocess.check_output('curl ' + url, shell=True).decode("utf-8")
        result = JSONDecoder().decode(output)['log']

        print('log = {}'.format(result))
        
        assert isinstance(result['clock'], numpy.ndarray)
        assert isinstance(result['is_running'], numpy.ndarray)
        assert result['is_running'].shape == result['clock'].shape
        assert result['clock'].shape[0] >= 3
        assert result['clock'].shape[1] == 1
        assert result['clock'][-1,0] - result['clock'][0,0] < 4
        
    except Exception as e:
        
        print('** EXCEPTION RAISED **')
        print(e)
        raise e
    
    finally:
        
        if start_server:
            
            # stop server
            print('> Terminating server')
            server.terminate()
