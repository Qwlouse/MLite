#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
from collections import OrderedDict
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
        self.kwargs = OrderedDict(zip(args[-len(defaults):], defaults))

    def get_free_parameters(self, args, kwargs):
        return [a for a in self.arguments[len(args):] if a not in kwargs]

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
        self._assert_no_unexpected_args(args)
        self._assert_no_unexpected_kwargs(kwargs)
        self._assert_no_duplicate_args(args, kwargs)
        args, kwargs = self._fill_in_options(args, kwargs, options)
        self._assert_no_missing_args(args, kwargs)
        return args, kwargs

    def __unicode__(self):
        args = self.positional_args
        vararg = ("*" + self.vararg_name) if self.vararg_name else ""
        kwargs = ["%s=%s" % (n, v.__repr__()) for n, v in self.kwargs.items()]
        kw_wc = ("**" + self.kw_wildcard_name) if self.kw_wildcard_name else ""
        return "{name}({args}{sep1}{vararg}{sep2}{kwargs}{sep3}{kw_wc})".format(
            name=self.name,
            args=", ".join(args),
            sep1=", " if vararg and args else "",
            vararg=vararg,
            sep2=", " if kwargs and (args or vararg) else "",
            kwargs=", ".join(kwargs),
            sep3=", " if kw_wc and (args or vararg or kwargs) else "",
            kw_wc=kw_wc
        )

    def __repr__(self):
        return "<Signature at 0x{1:x} for '{0}'>".format(self.name, id(self))

    def _assert_no_unexpected_args(self, args):
        if self.vararg_name is not None:
            return
        if len(args) > len(self.arguments):
            unexpected_args = args[len(self.arguments):]
            raise TypeError("{} got unexpected argument(s): {}".format(
                self.name, unexpected_args))

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
        free_params = self.get_free_parameters(args, kwargs)
        for f in free_params:
            if f in options:
                kwargs[f] = options[f]
        return args, kwargs

    def _assert_no_missing_args(self, args, kwargs):
        free_params = self.get_free_parameters(args, kwargs)
        missing_args = [m for m in free_params if m not in self.kwargs]
        if missing_args:
            raise TypeError("{} is missing value(s) for {}".format(
                self.name, free_params))
