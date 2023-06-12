from collections import UserDict
import operator
from copy import deepcopy
import random, string

def simplify(curve):
    j=1
    while j < (len(curve._data)-1):
        kf_prev = curve._data.peekitem(j-1)[1]
        kf_this = curve._data.peekitem(j)[1]
        kf_next = curve._data.peekitem(j+1)[1]
        
        if not (kf_prev.value == kf_this.value == kf_next.value):
            j+=1
            continue
        if not (kf_prev.interpolation_method == kf_this.interpolation_method == kf_next.interpolation_method):
            j+=1
            continue
        if not (kf_prev._interpolator_arguments == kf_this._interpolator_arguments == kf_next._interpolator_arguments):
            j+=1
            continue
        curve._data.popitem(j)
    return curve


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    # via https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    return ''.join(random.choice(chars) for _ in range(size))


class DictValuesArithmeticFriendly(UserDict):
    def __arithmetic_helper(self, operator, other=None):
        outv = deepcopy(self)
        for k,v in self.items():
            if other is not None:
                outv[k] = operator(v, other)
            else:
                outv[k] = operator(v)
        return outv
    def __add__(self, other):
        return self.__arithmetic_helper(operator.add, other)
    #def __div__(self, other):
    def __truediv__(self, other): # oh right
        return self.__arithmetic_helper(operator.truediv, other)
        #return self.__arithmetic_helper(1/other, operator.mul)
    def __rtruediv__(self, other):
        outv = deepcopy(self)
        for k,v in self.items():
                outv[k] = other / v
        return outv
    def __mul__(self, other):
        return self.__arithmetic_helper(operator.mul, other)
    def __neg__(self):
        return self.__arithmetic_helper(operator.neg)
    def __radd__(self, other):
        return self + other
    def __rmul__(self, other):
        return self * other
    def __rsub__(self, other):
        return (self * (-1)) + other
    def __sub__(self, other):
        return self.__arithmetic_helper(operator.sub, other)
