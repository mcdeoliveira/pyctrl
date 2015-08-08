import numpy

from . import block

class Logger(block.Block):

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

    def read(self):

        if self.page == 0:
            return self.data[:self.current,:]
        else:
            return numpy.vstack((self.data[self.current:,:],
                                 self.data[:self.current,:]))
    
    def write(self, values):

        # Log data
        self.data[self.current, :] = values

        if self.current < self.data.shape[0] - 1:
            # increment current pointer
            self.current += 1
        else:
            # reset current pointer and increment page counter
            self.current = 0
            self.page += 1

