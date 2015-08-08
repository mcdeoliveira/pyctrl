import numpy

from . import block

class Logger(block.Block):
    """Logger(number_of_rows, number_of_columns) implements a logger.
    """

    def __init__(self, *vars, **kwargs):

        number_of_rows = kwargs.pop('number_of_rows', 12000)

        labels = kwargs.pop('labels', ())
        assert isinstance(labels, (list, tuple))

        number_of_columns = len(labels)

        self.set(number_of_rows, number_of_columns)

        super().__init__(*vars, **kwargs)

    def set(self, number_of_rows, number_of_columns):

        self.data = numpy.zeros((number_of_rows, number_of_columns), float)
        self.reset()

    def reset(self):

        self.page = 0
        self.current = 0

    def get_current_page(self):
        return self.page

    def get_current_index(self):
        return self.page * self.data.shape[0] + self.current

    def get_log(self):

        if self.page == 0:
            return self.data[:self.current,:]
        else:
            return numpy.vstack((self.data[self.current:,:],
                                 self.data[:self.current,:]))
    
    read = get_log
        
    def write(self, values):

        # convert to list
        values = list(values)

        # reshape?
        if self.data.shape[1] != len(values):
            # reshape log
            self.set(self.data.shape[0], len(values))
        
        # Log data
        self.data[self.current, :] = values

        if self.current < self.data.shape[0] - 1:
            # increment current pointer
            self.current += 1
        else:
            # reset current pointer and increment page counter
            self.current = 0
            self.page += 1
