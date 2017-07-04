def test_webserver():

    # initiate server
    print('> Starting server')

    import subprocess
    import time
    from pyctrl.util.json import JSONDecoder, JSONEncoder
    
    server = subprocess.Popen(["python3",
                               "pyctrl/webserver.py"],
                              stdout = subprocess.PIPE)

    time.sleep(1)

    try:

        # check index page
        answer = b"<div><p>&lt;class 'pyctrl.Controller'&gt; with: 0 timer(s), 3 signal(s), 1 source(s), 0 filter(s), and 0 sink(s)</p><h2>timers</h2><ol></ol><h2>signals</h2><ol><li>clock</li><li>duty</li><li>is_running</li></ol><h2>sources</h2><ol><li>clock[Clock, disabled] &Gt; clock</li></ol><h2>filters</h2><ol></ol><h2>sinks</h2><ol></ol></div>"

        url = "http://127.0.0.1:5000"
        output = subprocess.check_output(["curl", url])
        assert output == answer
        
        # check info page
        url = "http://127.0.0.1:5000/info"
        output = subprocess.check_output(["curl", url])
        assert output == answer

        # sink methods
        
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
        
    except Exception as e:
        
        print('** EXCEPTION RAISED **')
        print(e)
        raise e
    
    finally:
        
        # stop server
        print('> Terminating server')
        server.terminate()
