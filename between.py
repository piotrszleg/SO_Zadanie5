import random

class Between(object):
    def __init__(self, start, end):
        if start.__class__!=end.__class__:
            raise ValueError("Start and end need to be of the same type")
        self.start=start
        self.end=end
    @property
    def length(self):
        return self.end-self.start
    def random(self):
        # cast to start class
        return_type=self.start.__class__
        return return_type(self.start+random.random()*self.length)