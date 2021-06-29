# This example shows how to add the "self" parameter to the body of a function, as if it were a class method.
# Also this decorator adds attributes described in kwargs to the function object.

from functools import wraps


def selfie(**kwargs):
    def _(f):
        print('assigning')
        for k, v in kwargs.items():
            if hasattr(f, k):
                raise AttributeError(f"Attribute `{k}` already exist on the object `{f}`!")
            setattr(f, k, v)

        @wraps(f)
        def __(*args, **kwargs):
            return f(f, *args, **kwargs)

        return __

    return _


# Example usage

@selfie(cache=2)
def function(self):
    self.cache = self.cache * 2

    return self.cache


print(function())
print(function())
print(function())
