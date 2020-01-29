import numpy

from .. import system


class DTSS(system.System):
    r"""
    *DTSS* implements a discrete-time state-space model of the form:

    .. math::

      x_{k+1} &= A x_k + B u_k \\
          y_k &= C x_k + D u_k

    :param numpy.array A: state space matrix :math:`A` (Default = [])
    :param numpy.array B: state space matrix :math:`B` (Default = [[0]])
    :param numpy.array C: state space matrix :math:`C` (Default = [])
    :param numpy.array D: state space matrix :math:`D` (Default = [[1]])
    :param numpy.array state: initial value of the state vector
    """

    def __init__(self,
                 # A = numpy.array([[]]),
                 A=numpy.zeros((0, 0)),
                 B=numpy.array([[0]]),
                 # C = numpy.array([[]]),
                 C=numpy.zeros((0, 0)),
                 D=numpy.array([[1]]),
                 state=None):

        # print('A = {} ({})'.format(A, A.shape))
        # print('B = {} ({})'.format(B, B.shape))
        # print('C = {} ({})'.format(C, C.shape))
        # print('D = {} ({})'.format(D, D.shape))

        # check dimensions
        n, _n = numpy.shape(A)
        # assert A.shape == (1, 0) or A.shape[0] == A.shape[1]
        assert n == _n

        _n, m = numpy.shape(B)
        # assert A.shape[0] == B.shape[0]
        assert n == _n

        p, _n = numpy.shape(C)
        # assert A.shape[1] == C.shape[1]
        assert n == _n

        _p, _m = numpy.shape(D)
        # assert C.shape[0] == D.shape[0]
        assert m == _m
        # assert B.shape[1] == D.shape[1]
        assert p == _p

        self.A = A
        self.B = B
        self.C = C
        self.D = D

        if state is None:
            self.state = numpy.zeros(n, dtype=numpy.float_)
        elif numpy.size(state) == n:
            self.state = numpy.array(state, dtype=numpy.float_)
        else:
            raise system.SystemException('Order of state must match order of denominator')

        # print('num = {}'.format(self.num))
        # print('den = {}'.format(self.den))
        # print('state = {}'.format(self.state))

    def set_output(self, yk):
        r"""
        Sets the internal state of the :py:class:`pyctrl.system.DTSS` so that a call to `update` with `uk = 0` yields `yk`.
        
        It is calculated as follows:

        .. math::

            x_{k} = C^\dag y_{k}

        where :math:`C^\dag` is the pseudo-inverse of :math:`C`, which leads to 

        .. math::

            y_k &= C x_k = y_k
        
        when :math:`u_k = 0`

        :param numpy.array yk: desired `yk`
        """

        # y = C x
        assert isinstance(yk, numpy.ndarray)
        assert numpy.shape(yk)[0] == numpy.shape(self.C)[0]
        xk = numpy.linalg.lstsq(self.C, yk)[0]
        self.set_state(xk)

    def get_state(self):
        return self.state

    def set_state(self, xk):
        assert len(xk) == len(self.state)
        self.state = xk

    def shape(self):
        return self.B.shape[1], self.C.shape[0], self.A.shape[0]

    def update(self, uk):
        r"""
        Update :py:class:`pyctrl.system.SSTF` model. Calculates:

        .. math::
        
            y_k &= C x_k + D u_k

        then updates

        .. math::
        
            x_{k+1} &= A x_k + B u_k

        :param numpy.array uk: input at time k
        """

        if not isinstance(uk, numpy.ndarray):
            # make sure uk is an numpy array
            uk = numpy.array((uk,), dtype=numpy.float_)
            print('> uk = {}'.format(uk))

        # yk = C xk + D uk
        # xk+1 = A xk + B uk
        if numpy.size(self.state) > 0:
            print('> x = {}'.format(self.state))
            print(self.state)
            print(self.C)
            print(self.D)
            print(uk)
            yk = numpy.dot(self.C, self.state) + numpy.dot(self.D, uk)
            print('> yk = {}'.format(yk))
            print('> A.x = {}'.format(self.A.dot(self.state)))
            print('> B.u = {}'.format(self.B.dot(uk)))
            self.state = numpy.dot(self.A, self.state) + numpy.dot(self.B, uk)
            print('< x = {}'.format(self.state))
        else:
            yk = numpy.dot(self.D, uk)

        return yk
