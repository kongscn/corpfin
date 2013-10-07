from abc import ABCMeta, abstractmethod

class Strategy():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__
        self.result = None

    # def config(self, **kwargs):
    #     for key in kwargs.keys():
    #         if key in self.__class__.CONFIGKEYS:
    #             self.__dict__[key] = kwargs[key]
    #         else:
    #             raise AttributeError(key + ' not allowed.')
    #     self.result = None  #clear analyze result

    @abstractmethod
    def analyze(self, *args):
        pass

    @abstractmethod
    def summary(self):
        pass

    @abstractmethod
    def plot(self):
        pass

    @abstractmethod
    def apply(self, *args):
        pass