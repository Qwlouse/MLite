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
        if self.kw_wildcard_name is not None:
            return
        unexpected_kwargs = [v for v in kwargs if v not in self.arguments]
        if unexpected_kwargs:
            raise TypeError("{} got unexpected kwarg(s): {}".format(
                self.name, unexpected_kwargs))

    def _assert_no_duplicate_args(self, args, kwargs):
        positional_arguments = self.arguments[:len(args)]
        duplicate_arguments = [v for v in positional_arguments if v in kwargs]
        if duplicate_arguments:
            raise TypeError("{} got multiple values for argument(s) {}".format(
                self.name, duplicate_arguments))

    def _fill_in_options(self, args, kwargs, options):
        free_params = [a for a in self.arguments[len(args):] if a not in kwargs]
        for f in free_params:
            if f in options:
                kwargs[f] = options[f]
        return args, kwargs

    def _assert_no_missing_args(self, args, kwargs):
        free_params = [a for a in self.arguments[len(args):] if a not in kwargs]
        if free_params:
            raise TypeError("{} is missing value(s) for {}".format(
                self.name, free_params))

    def construct_arguments(self, args, kwargs, options):
        """
        Construct args list and kwargs dictionary for this signature such that:
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
        args, kwargs = self._fill_in_options(args, kwargs, options)
        self._assert_no_missing_args(args, kwargs)
        return args, kwargs
