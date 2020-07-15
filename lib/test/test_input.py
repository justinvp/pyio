import unittest
import typing
import sys

import pulumi

_PULUMI_INPUT_TYPE = "_pulumi_input_type"
_TO_DICT = "_to_dict"
_TRANSLATE_PROPERTY = "_translate_property"

T = typing.TypeVar('T')

def input_type(cls: typing.Type[T]) -> typing.Type[T]:
    """Input type decorator. TODO"""
    setattr(cls, _PULUMI_INPUT_TYPE, True)
    if not hasattr(cls, _TO_DICT):
        _translate_property = getattr(cls, _TRANSLATE_PROPERTY, None)
        if callable(_translate_property):
            def _to_dict(self) -> dict:
                # Return a copy of `self.__dict__` with translated keys.
                return {_translate_property(self, k): v for k, v in self.__dict__.items()}
        else:
            def _to_dict(self) -> dict:
                # Return a copy of `self.__dict__`.
                return dict(self.__dict__)
        setattr(cls, _TO_DICT, _to_dict)
    return cls

def _is_input_type(obj) -> bool:
    return hasattr(obj, _PULUMI_INPUT_TYPE) and hasattr(obj, _TO_DICT)

@input_type
class FooArgs:
    def __init__(__self__, first_arg, second_arg):
        """The docstring for FooArgs."""
        __self__.first_arg = first_arg
        __self__.second_arg = second_arg


# @dataclasses.dataclass
# @pulumi.input_type
# class BucketWebsiteArgs:
#     first_arg: Optional[pulumi.Input[str]] = pulumi.property("firstArg")
#     second_arg: Optional[pulumi.Input[float]] = pulumi.property("secondArg")

# @pulumi.output_type
# class BucketWebsite:
#     first_arg: str = pulumi.property("firstArg")
#     second_arg: float = pulumi.property("secondArg")



@input_type
class BarArgs:
    def __init__(__self__, first_arg, second_arg):
        """The docstring for FooArgs."""
        __self__.first_arg = first_arg
        __self__.second_arg = second_arg

    def _translate_property(self, prop):
        table = {
            "first_arg": "firstArg",
            "second_arg": "secondArg",
        }
        return table.get(prop) or prop

@input_type
class BazArgs:
    def __init__(__self__, first_arg, second_arg):
        """The docstring for FooArgs."""
        __self__.first_arg = first_arg
        __self__.second_arg = second_arg

    def _to_dict(self):
        return {
            "firstArg": self.first_arg,
            "secondArg": self.second_arg,
        }

class NoSubclass:
    pass
class DictSubclass(dict):
    pass

class BaseTestCase(unittest.TestCase):
    def assertHasAttr(self, obj, attrname: str, message=None):
        if not hasattr(obj, attrname):
            if message is not None:
                self.fail(message)
            else:
                self.fail("{} should have an attribute {}".format(obj, attrname))

class TestInputType(BaseTestCase):
    def test_foo(self):
        f = FooArgs(first_arg="hello", second_arg=42)
        self.assertHasAttr(f, "_pulumi_input_type")
        self.assertHasAttr(f, "_to_dict")
        d = f._to_dict()
        self.assertEqual(d, {
            "first_arg": "hello",
            "second_arg": 42,
        })

    def test_bar(self):
        f = BarArgs(first_arg="hello", second_arg=42)
        self.assertHasAttr(f, "_pulumi_input_type")
        self.assertHasAttr(f, "_to_dict")
        d = f._to_dict()
        self.assertEqual(d, {
            "firstArg": "hello",
            "secondArg": 42,
        })

    def test_baz(self):
        f = BazArgs(first_arg="hello", second_arg=42)
        self.assertHasAttr(f, "_pulumi_input_type")
        self.assertHasAttr(f, "_to_dict")
        d = f._to_dict()
        self.assertEqual(d, {
            "firstArg": "hello",
            "secondArg": 42,
        })


    def test_subclasses(self):
        self.assertFalse(issubclass(NoSubclass, dict))
        self.assertTrue(issubclass(DictSubclass, dict))

