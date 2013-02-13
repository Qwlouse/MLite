#!/usr/bin/python
# coding=utf-8
import inspect


class Signature:
    """
    Contains information about the signature of a function.
    name : the functions name
    arguments : list of all arguments
    vararg_name : name of the *args variable
    kw_wildcard_name : name of the **kwargs variable
    positional_args : list of all positional-only arguments
    kwargs : dict of all keyword arguments mapped to their default
    """
    def __init__(self, f):
        self.name = f.__name__
        args, vararg_name, kw_wildcard_name, defaults = inspect.getargspec(f)
        self.arguments = args
        self.vararg_name = vararg_name
        self.kw_wildcard_name = kw_wildcard_name
        defaults = defaults or []
        self.positional_args = args[:len(args) - len(defaults)]
        self.kwargs = dict(zip(args[-len(defaults):], defaults))

    def _assert_no_unexpected_kwargs(self, kwargs):
        if self.kw_wildcard_name is None:
            wrong_kwargs = [v for v in kwargs if v not in self.arguments]
            if wrong_kwargs:
                raise TypeError("{} got unexpected kwarg(s): {}".format(
                    self.name, wrong_kwargs))

    def _assert_no_duplicate_args(self, args, kwargs):
        positional_arguments = self.arguments[:len(args)]
        duplicate_arguments = [v for v in positional_arguments if v in kwargs]
        if duplicate_arguments:
            raise TypeError("{} got multiple values for argument(s) {}".format(
                self.name, duplicate_arguments))

    def construct_arguments(self, args, kwargs, options):
        """
        construct a dictionary of arguments for this signature such that:
          - the original explicit call arguments (args, kwargs) are preserved
          - missing arguments are filled in by name using options (if possible)
          - default arguments are overridden by options
          - TypeError is thrown if:
            * kwargs contains one or more unexpected keyword arguments
            * conflicting values for a parameter in both args and kwargs
            * there is an unfilled parameter at the end of this process
        """
        self._assert_no_unexpected_kwargs(kwargs)
        self._assert_no_duplicate_args(args, kwargs)
