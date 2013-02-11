#!/usr/bin/python
# coding=utf-8
import unittest
from mlite.signature_spells import Signature


##############  function definitions to test on ################################
def foo():
    return


def bariza(a, b, c):
    return a, b, c


def complex_function_name(a=1, b='foo', c=20):
    return a, b, c


def FunCTIonWithCAPItals(a, b, c=3, **kwargs):
    return a, b, c, kwargs


def _name_with_underscore_(foo, bar, *baz):
    return foo, bar, baz


def __double_underscore__(man, o, *men, **OO):
    return man, o, men, OO


def old_name(verylongvariablename):
    return verylongvariablename


renamed = old_name

functions = [foo, bariza, complex_function_name, FunCTIonWithCAPItals,
             _name_with_underscore_, __double_underscore__, old_name, renamed]


########################  Tests  ###############################################
class SignatureSpellsTest(unittest.TestCase):
    def test_Signature_constructor_extract_function_name(self):
        names = ['foo', 'bariza', 'complex_function_name',
                 'FunCTIonWithCAPItals', '_name_with_underscore_',
                 '__double_underscore__', 'old_name', 'old_name']
        for f, name in zip(functions, names):
            s = Signature(f)
            self.assertEqual(s.name, name,
                             " on %s expect %s but was %s" % (
                                 f.__name__, name, s.name))

    def test_Signature_constructor_extracts_all_arguments(self):
        arguments = [[], ['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c'],
                         ['foo', 'bar'], ['man', 'o'], ['verylongvariablename'],
                         ['verylongvariablename']]
        for f, args in zip(functions, arguments):
            s = Signature(f)
            self.assertSequenceEqual(s.arguments, args,
                                     " on %s expect %s but was %s" % (
                                         f.__name__, args, s.arguments))

    def test_Signature_constructor_extract_vararg_name(self):
        vararg_names = [None, None, None, None, 'baz', 'men', None, None]
        for f, varg in zip(functions, vararg_names):
            s = Signature(f)
            self.assertEqual(s.vararg_name, varg,
                             " on %s expect %s but was %s" % (
                                 f.__name__, varg, s.vararg_name))

    def test_Signature_constructor_extract_kwargs_wildcard_name(self):
        kw_wc_names = [None, None, None, 'kwargs', None, 'OO', None, None]
        for f, kw_wc in zip(functions, kw_wc_names):
            s = Signature(f)
            self.assertEqual(s.kw_wildcard_name, kw_wc,
                             " on %s expect %s but was %s" % (
                                 f.__name__, kw_wc, s.kw_wildcard_name))

    def test_Signature_constructor_extract_positional_arguments(self):
        pos_args = [[], ['a', 'b', 'c'], [], ['a', 'b'], ['foo', 'bar'],
                    ['man', 'o'], ['verylongvariablename']]
        for f, pargs in zip(functions, pos_args):
            s = Signature(f)
            self.assertEqual(s.positional_args, pargs,
                             " on %s expect %s but was %s" % (
                                 f.__name__, pargs, s.positional_args))

    def test_Signature_constructor_extract_kwargs(self):
        kwarg_list = [{}, {}, {'a': 1, 'b': 'fo', 'c': 9}, {'c': 3}, {}, {}, {}]
        for f, kwargs in zip(functions, kwarg_list):
            s = Signature(f)
            self.assertEqual(s.kwargs, kwargs,
                             " on %s expect %s but was %s" % (
                                 f.__name__, kwargs, s.kwargs))

    def test_construct_arguments_with_unexpected_kwargs_raises_TypeError(self):
        kwargs = {'unexpected': 23}
        self.assertRaises(
            TypeError,
            Signature(foo)._assert_no_unexpected_kwargs,
            kwargs)
        self.assertRaises(
            TypeError,
            Signature(bariza)._assert_no_unexpected_kwargs,
            kwargs)
        self.assertRaises(
            TypeError,
            Signature(complex_function_name)._assert_no_unexpected_kwargs,
            kwargs)
        self.assertRaises(
            TypeError,
            Signature(_name_with_underscore_)._assert_no_unexpected_kwargs,
            kwargs)
        self.assertRaises(
            TypeError,
            Signature(old_name)._assert_no_unexpected_kwargs,
            kwargs)
        self.assertRaises(
            TypeError,
            Signature(renamed)._assert_no_unexpected_kwargs,
            kwargs)

    def test_construct_arguments_with_kwargs_and_kwargswildcard_does_not_raise(
            self):
        Signature(FunCTIonWithCAPItals)._assert_no_unexpected_kwargs(
            {'unexpected': 23})
        Signature(__double_underscore__)._assert_no_unexpected_kwargs(
            {'unexpected': 23})

    def test_construct_arguments_with_expected_kwargs_does_not_raise(self):
        Signature(complex_function_name)._assert_no_unexpected_kwargs(
            {'a': 4, 'b': 3, 'c': 2})
        Signature(FunCTIonWithCAPItals)._assert_no_unexpected_kwargs(
            {'c': 5})

    def test_construct_arguments_with_kwargs_for_positional_args_does_not_raise(
            self):
        Signature(bariza)._assert_no_unexpected_kwargs(
            {'a': 4, 'b': 3, 'c': 2})
        Signature(FunCTIonWithCAPItals)._assert_no_unexpected_kwargs(
            {'a': 4, 'b': 3, 'c': 2, 'd': 6})