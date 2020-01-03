import unittest
import numpy

import pyctrl.block as block


class TestUnittestAssertions(unittest.TestCase):

    def test_BufferBlock(self):

        # no mux, no demux
        obj = block.ShortCircuit()
    
        obj.write()
        self.assertTrue( obj.read() == () )
        
        obj.write(1)
        self.assertTrue( obj.read() == (1,) )
        
        obj.write(1, 2)
        self.assertTrue( obj.read() == (1, 2) )
        
        obj.write(1, numpy.array([2,3]))
        self.assertTrue( len(obj.read()) == 2 )
        self.assertTrue( obj.read()[0] == 1 )

        self.assertTrue( numpy.array_equal(obj.read()[1], numpy.array([2,3])) )

        obj.write(1, numpy.array([2,3]), numpy.array([4,5]))
        self.assertTrue( len(obj.read()) == 3 )
        self.assertTrue( obj.read()[0] == 1 )
        self.assertTrue( numpy.array_equal(obj.read()[1], numpy.array([2,3])) )
        self.assertTrue( numpy.array_equal(obj.read()[2], numpy.array([4,5])) )
        
        # mux, no demux
        obj = block.ShortCircuit(mux = True)
        
        obj.write()
        self.assertTrue( obj.read() == () )
        
        obj.write(1)
        self.assertTrue( len(obj.read()) == 1 )
        self.assertTrue( numpy.array_equal(obj.read()[0], numpy.array([1])) )

        obj.write(1, 2)
                
        self.assertTrue( len(obj.read()) == 1 )
        self.assertTrue( numpy.array_equal(obj.read()[0], numpy.array([1, 2])) )
        
        obj.write(1, [2,3])
        self.assertTrue( len(obj.read()) == 1 )
        self.assertTrue( numpy.array_equal(obj.read()[0], numpy.array([1,2,3])) )

        obj.write(1, numpy.array([2,3]))
        self.assertTrue( len(obj.read()) == 1 )
        self.assertTrue( numpy.array_equal(obj.read()[0], numpy.array([1,2,3])) )
        
        obj.write(1, numpy.array([2,3]), numpy.array([4,5]))
        self.assertTrue( len(obj.read()) == 1 )
        self.assertTrue( numpy.array_equal(obj.read()[0], numpy.array([1,2,3,4,5])) )
        
        # mux, demux
        obj = block.ShortCircuit(mux = True, demux = True)
        
        obj.write()
        self.assertTrue( obj.read() == () )
        
        obj.write(1)
        self.assertTrue( obj.read() == (1,) )
        
        obj.write(1, 2)
        self.assertTrue( len(obj.read()) == 2 )
        self.assertTrue( obj.read() == (1, 2) )
        
        obj.write(1, numpy.array([2,3]))
        self.assertTrue( len(obj.read()) == 3 )
        self.assertTrue( obj.read() == (1,2,3) )
        
        obj.write(1, numpy.array([2,3]), numpy.array([4,5]))
        self.assertTrue( len(obj.read()) == 5 )
        self.assertTrue( obj.read() == (1,2,3,4,5) )
        
        with self.assertRaises(block.BlockException):
            obj = block.ShortCircuit(asd = 1)

            
    def test_Printer(self):

        obj = block.Printer()
        
        obj.write(1.5)
        
        obj.write([1.5, 1.3])
        
        obj.write((1.5, 1.3))
        
        obj.write(*[1.5, 1.3])
        
        obj.write(*(1.5, 1.3))
        
        self.assertTrue( obj.get() == { 'enabled': True, 'endln': '\n', 'frmt': '{: 12.4f}', 'sep': ' ', 'file': None, 'message': None } )
                         
        self.assertTrue( obj.get('enabled') == True )
        self.assertTrue( obj.get('endln', 'frmt') == { 'endln': '\n', 'frmt': '{: 12.4f}' } )
        
        with self.assertRaises(block.BlockException):
            obj = block.Printer(adsadsda = 1)

        with self.assertRaises(TypeError):
            obj = block.Printer(1, "adsadsda")

        with self.assertRaises(block.BlockException):
            obj = block.Printer(par = 1)

        with self.assertRaises(block.BlockException):
            obj = block.Printer(par = "adsadsda")

        with self.assertRaises(block.BlockException):
            obj = block.Printer(par = "adsadsda", sadasd = 1)

        obj = block.Printer(enabled = False)


    def test_set(self):

        blk = block.Printer()

        self.assertTrue( blk.get() == { 'enabled': True, 'endln': '\n', 'frmt': '{: 12.4f}', 'sep': ' ', 'file': None, 'message': None } )
    
        self.assertTrue( blk.get('enabled', 'frmt') == {'frmt': '{: 12.4f}', 'enabled': True} )
    
        self.assertTrue( blk.get('enabled') == True )

        with self.assertRaises(KeyError):
            blk.get('*enabled')

        blk.set(enabled = False)
        self.assertTrue( blk.get('enabled') == False )

        blk.set(enabled = True)
        self.assertTrue( blk.get('enabled') == True )

        with self.assertRaises(block.BlockException):
            blk.set(_enabled = True)
    
        blk.set(sep = '-')
        self.assertTrue( blk.get('sep') == '-' )

        blk = block.BufferBlock()
        self.assertTrue( blk.get() == {'enabled': True, 'demux': False, 'mux': False} )
    
        # test twice to make sure it is copying
        self.assertTrue( blk.get() == {'enabled': True, 'demux': False, 'mux': False} )

        with self.assertRaises(KeyError):
            blk.get('buffer')

        blk.set(demux = True)
        self.assertTrue( blk.get('demux') == True )

        with self.assertRaises(block.BlockException):
            blk.set(buffer = (1,))
    
        with self.assertRaises(block.BlockException):
            blk.set(controller = None)

        with self.assertRaises(KeyError):
            blk.get('buffer')

        with self.assertRaises(KeyError):
            blk.get('controller')
        
    def test_logger(self):

        import pyctrl.block as logger
        import numpy as np

        _logger = logger.Logger()

        # write one entry
        _logger.write(1,2,3)
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log, np.array([[1,2,3]])) )

        # write second entry
        _logger.write(4,5,6)
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log, np.array([[1,2,3],[4,5,6]])) )

        # dynamic reshaping
        _logger.write(1,2,3,5)
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log, np.array([[1,2,3,5]])) )
        
        # vector entries
        _logger.write(1,2,[5,3])
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log, np.array([[1,2,3,5], [1,2,5,3]])) )
        
        # vector entries
        _logger.write([1,2],2,[3,5])
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log, np.array([[1,2,2,3,5]])) )

        self.assertTrue( _logger.get() == { 'auto_reset': False, 'enabled': True, 'current': 1, 'page': 0, 'labels': None, 'index': None } )
        
        # vector entries
        _logger.write([1,3],[2,3,5])
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log, np.array([[1,2,2,3,5],[1,3,2,3,5]])) )
        
        # with labels
        _logger = logger.Logger(labels = ['s1','s2','s3'])
        
        # write one entry
        _logger.write(1,2,3)
        
        self.assertTrue( _logger.get('index') == (0,1,2,3) )
        
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log['s1'], np.array([[1]])) )
        self.assertTrue( np.array_equal(log['s2'], np.array([[2]])) )
        self.assertTrue( np.array_equal(log['s3'], np.array([[3]])) )

        self.assertTrue( _logger.get('index') == (0,1,2,3) )

        # write second entry
        _logger.write(4,5,6)
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log['s1'], np.array([[1],[4]])) )
        self.assertTrue( np.array_equal(log['s2'], np.array([[2],[5]])) )
        self.assertTrue( np.array_equal(log['s3'], np.array([[3],[6]])) )

        self.assertTrue( _logger.get('index') == (0,1,2,3) )
        
        _logger.set(labels = ['s1','s2','s3','s4'])
        
        self.assertTrue( _logger.get('labels') == ['s1','s2','s3','s4'] )
        
        # dynamic reshaping
        _logger.write(1,2,3,5)
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log['s1'], np.array([[1]])) )
        self.assertTrue( np.array_equal(log['s2'], np.array([[2]])) )
        self.assertTrue( np.array_equal(log['s3'], np.array([[3]])) )
        self.assertTrue( np.array_equal(log['s4'], np.array([[5]])) )
        
        self.assertTrue( _logger.get('index') == (0,1,2,3,4) )
        
        # vector entries
        _logger.write(1,2,4,[3,5])
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log['s1'], np.array([[1]])) )
        self.assertTrue( np.array_equal(log['s2'], np.array([[2]])) )
        self.assertTrue( np.array_equal(log['s3'], np.array([[4]])) )
        self.assertTrue( np.array_equal(log['s4'], np.array([[3,5]])) )
        
        self.assertTrue( _logger.get('index') == (0,1,2,3,5) )
        
        # vector entries
        _logger.set(labels = ['s1','s2','s3','s4'])
        _logger.write([1,2],2,4,[3,5])
        
        log = _logger.get_log()
        self.assertTrue( np.array_equal(log['s1'], np.array([[1,2]])) )
        self.assertTrue( np.array_equal(log['s2'], np.array([[2]])) )
        self.assertTrue( np.array_equal(log['s3'], np.array([[4]])) )
        self.assertTrue( np.array_equal(log['s4'], np.array([[3,5]])) )
        
        self.assertTrue( _logger.get('index') == (0,2,3,4,6) )
        
        
        self.assertTrue( _logger.get() == { 'auto_reset': False, 'enabled': True, 'current': 1, 'page': 0, 'labels': ['s1','s2','s3','s4'], 'index': (0,2,3,4,6) } )
        
    def test_Signal(self):

        import numpy as np

        x = np.array([1,2,3])
        obj = block.Signal(signal = x, repeat = True)
        
        k = 0
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        
        k = 0
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        
        x = np.array([1,2,3])
        obj = block.Signal(signal = x, repeat = False)
        
        k = 0
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        
        (y,) = obj.read()
        self.assertTrue( y == 0 )
        
        (y,) = obj.read()
        self.assertTrue( y == 0 )
        
        (y,) = obj.read()
        self.assertTrue( y == 0 )
        
        x = np.array([1,2,3])
        obj = block.Signal(signal = x, repeat = True)
        
        k = 0
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        k += 1
        
        obj.reset()
        
        k = 0
        (y,) = obj.read()
        self.assertTrue( y == x[0] )
        
        k = 0
        obj.set(index = k)
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        
        k = 2
        obj.set(index = k)
        (y,) = obj.read()
        self.assertTrue( y == x[k] )
        
        k = 3
        obj.set(index = k)
        (y,) = obj.read()
        self.assertTrue( y == x[0] )
        
        obj.set(repeat = False)
        
        k = 3
        with self.assertRaises(AssertionError):
            obj.set(index = k)

    def test_apply(self):

        def f(*x):
            return x[0] < 1
    
        obj = block.Apply(function = f)
    
        obj.write(0)
        (y,) = obj.read()
        self.assertTrue( y == True )

        obj.write(1)
        (y,) = obj.read()
        self.assertTrue( y == False )
        
        obj.write(0,1)
        (y,) = obj.read()
        self.assertTrue( y == True )
        
        obj.write(1,2)
        (y,) = obj.read()
        self.assertTrue( y == False )
        
        def g(*x):
            return all(map(lambda y : y < 1, x))
        
        obj = block.Apply(function = g)
        
        obj.write(0)
        (y,) = obj.read()
        self.assertTrue( y == True )
        
        obj.write(0, 0.5)
        (y,) = obj.read()
        self.assertTrue( y == True )
        
        obj.write(1)
        (y,) = obj.read()
        self.assertTrue( y == False )
        
        obj.write(0, 1)
        (y,) = obj.read()
        self.assertTrue( y == False )
        
    def test_map(self):

        def f(i):
            return i + 1

        obj = block.Map(function = f)
        
        obj.write(0)
        (y,) = obj.read()
        self.assertTrue( y == 1 )
        
        obj.write(0,2)
        y = obj.read()
        self.assertTrue( y == (1,3) )
        
        obj.write()
        y = obj.read()
        self.assertTrue( y == () )
        
    def test_html(self):

        obj = block.ShortCircuit()
        
        self.assertEqual( obj.html(), '<dl><dt>mux</dt><dd>False</dd><dt>demux</dt><dd>False</dd><dt>enabled</dt><dd>True</dd></dl>')

def test_wrap():

    import numpy as np

    obj = block.Wrap()

    for x in np.arange(0, 4*np.pi, 0.01):
        theta = np.mod(x, 2*np.pi)
        turns = np.floor_divide(x, 2*np.pi)
        #print('theta = {}, turns = {}'.format(theta, turns))
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert obj.turns == turns
        assert y == x

    obj = block.Wrap()
    
    for x in np.arange(0, 4*np.pi, 0.01):
        theta = np.mod(x + np.pi, 2*np.pi) - np.pi
        turns = np.floor_divide(x + np.pi, 2*np.pi)
        #print('x = {}, theta = {}, turns = {}'.format(x, theta, turns))
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert obj.turns == turns
        assert numpy.fabs(y - x) < 1e-4

    obj = block.Wrap()
    
    for x in np.arange(-np.pi, 3*np.pi, 0.01):
        theta = np.mod(x + np.pi, 2*np.pi) - np.pi
        turns = np.floor_divide(x + np.pi, 2*np.pi)
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert obj.turns == turns
        assert numpy.fabs(y - x) < 1e-4
        
    obj = block.Wrap()
    
    for x in np.arange(4*np.pi, 0, -0.01):
        theta = np.mod(x, 2*np.pi)
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert numpy.fabs(y - x + 4*np.pi) < 1e-4
        
    obj.reset()
    
    for x in np.arange(4*np.pi, 0, -0.01):
        theta = np.mod(x + np.pi, 2*np.pi) - np.pi
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert numpy.fabs(y - x + 4*np.pi) < 1e-4

    # degrees
    obj = block.Wrap(scaling = 360)

    for x in np.arange(0, 4*360, 10):
        theta = np.mod(x, 360)
        turns = np.floor_divide(x, 360)
        #print('theta = {}, turns = {}'.format(theta, turns))
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert obj.turns == turns
        assert y == x

    # cycles
    obj = block.Wrap(scaling = 1)

    for x in np.arange(0, 4, 10):
        theta = np.mod(x, 1)
        turns = np.floor_divide(x, 1)
        #print('theta = {}, turns = {}'.format(theta, turns))
        obj.write(theta)
        (y,) = obj.read()
        assert obj.theta == theta
        assert obj.turns == turns
        assert y == x

            

def test_Interp():

    import numpy as np

    t = np.array([0,1,2])
    x = np.array([1,0,1])
    obj = block.Interp(xp = x, fp = t)

    for k in range(len(t)):
        tk = t[k]
        obj.write(tk)
        (y,) = obj.read()
        assert y == x[k]

    obj.reset()
    obj.write(0)
        
    tk = 0.5
    obj.write(tk)
    (y,) = obj.read()
    assert y == 0.5

    tk = 1.5
    obj.write(tk)
    (y,) = obj.read()
    assert y == 0.5

    tk = 1.75
    obj.write(tk)
    (y,) = obj.read()
    assert y == 0.75
    
def test_FadeIn():

    import numpy as np

    t = np.array([0,1,2,3,4])
    yy = np.array([2,2,2,2,2])
    x = np.array([1,0.5,0,0,0]) + (1 - np.array([1,0.5,0,0,0])) * yy
    obj = block.Fade(target = 1, period = 2)

    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]

    obj.reset()

    t = t + 2
    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]

    yy = np.array([2,3,4,1,0])
    x = np.array([1,0.5,0,0,0]) + (1 - np.array([1,0.5,0,0,0])) * yy
    obj = block.Fade(target = 1, period = 2)

    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]

    obj.reset()

    t = t + 2
    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]
        
    obj.reset()
    
    yy = np.array([4,4,4,4,4])
    x = np.array([1,0.5,0,0,0]) + (1 - np.array([1,0.5,0,0,0])) * yy
    t = t + 2
    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]
        
    yy = np.array([2,2,2,2,2])
    x = np.array([0,0,0,0,0]) + (1 - np.array([1,0.5,0,0,0])) * yy
    obj = block.Fade(period = 2)

    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]

    yy = np.array([[2],[4]])
    oo = np.array([[1],[0]])
    x = np.dot(oo, np.array([[1,0.5,0,0,0]])) + np.dot(yy, (1 - np.array([[1,0.5,0,0,0]])))
    obj = block.Fade(target = [1,0], period = 2)

    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, 2, 4)
        y = obj.read()
        assert not np.any(x[:,k] - numpy.array(y))
        
    obj.reset()

    t = t + 2
    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, 2, 4)
        y = obj.read()
        assert not np.any(x[:,k] - numpy.array(y))
        
    yy = np.array([2,3,4,1,0])
    x = (1 - np.array([1,0.5,0,0,0])) + np.array([1,0.5,0,0,0]) * yy
    obj = block.Fade(target = 1, direction = 'out', period = 2)

    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]

    obj.reset()

    t = t + 2
    for k in range(len(t)):
        tk = t[k]
        obj.write(tk, yy[k])
        (y,) = obj.read()
        assert y == x[k]
        
        
if __name__ == '__main__':
    unittest.main()

