# (c) Crown Owned Copyright, 2016. Dstl.

import warnings
import functools


def testing_depreceated(replacement=None):
    """
    For marking your testing-related functions as being depreciated in such a
    way that will show up during tests.

    Example:

    >>>from testing import common
    ...
    ...@testing_depreceated(common.create_organisation)
    ...def create_organisation():
    >>>    return common.create_organisation()
    """
    def outer(fun):
        if hasattr(fun, '__package__'):
            name = "%s.%s" % (fun.__package__, fun.__name__)
        elif hasattr(fun, '__module__'):
            name = "%s.%s" % (fun.__module__, fun.__name__)
        else:
            name = "%s" % fun.__name__

        msg = "%s is deprecated" % name
        if replacement is not None:
            if hasattr(fun, '__package__'):
                rep_name = "%s.%s" % (fun.__package__, fun.__name__)
            elif hasattr(fun, '__module__'):
                rep_name = "%s.%s" % (fun.__module__, fun.__name__)
            else:
                rep_name = "%s" % fun.__name__
            msg += "; use %s instead" % rep_name

        @functools.wraps(fun)
        def inner(*args, **kwargs):
            warnings.warn(msg, category=Warning, stacklevel=2)
            return fun(*args, **kwargs)

        return inner
    return outer
