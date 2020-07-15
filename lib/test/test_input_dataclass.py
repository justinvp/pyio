import unittest
import typing
import sys

import pulumi

_PULUMI_INPUT_TYPE = "_pulumi_input_type"
_PULUMI_PROPERTIES = "_pulumi_properties"
_TO_DICT = "_to_dict"
_TRANSLATE_PROPERTY = "_translate_property"

T = typing.TypeVar('T')

# A sentinel object to detect if a parameter is supplied or not.
class _MISSING_TYPE:
    pass
MISSING = _MISSING_TYPE()

class Property:
    def __init__(self, name: str, default: typing.Any = MISSING) -> None:
        self.name = name
        self.default = default
        self.type: typing.Any = None

def property(name: str, default: typing.Any = MISSING):
    return Property(name)

def _get_property(cls: type, a_name: str, a_type: type) -> Property:
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, Property):
        f = default
    else:
        f = property(name=a_name, default=default)

    f.type = a_type

    return f

def input_type(cls: typing.Type[T]) -> typing.Type[T]:
    """Input type decorator. TODO"""

    # Annotations that are defined in this class (not in base
    # classes). If __annotations__ isn't present, then this class
    # adds no new annotations. We use this to compute properties that are
    # added by this class.
    #
    # Properties are found from cls_annotations, which is guaranteed to be
    # ordered as of Python 3.7 (the implementation happens to be ordered on
    # Python 3.6). Default values are from class attributes, if a property
    # has a default. If the default value is a Property(), then it
    # contains additional info beyond (and possibly including) the
    # actual default value.
    cls_annotations = cls.__dict__.get('__annotations__', {})

    # Get type hints includes __annotations__ from base classes (which we don't want),
    # but handles forward references (which we _do_ want).
    # We'll look for properties in cls_annotations, but get the actual type from cls_hints.
    cls_hints = typing.get_type_hints(cls)

    # Properties.
    props = {
        name: _get_property(cls, name, cls_hints[name])
            for name in cls_annotations
    }

    # Clean-up class attributes.
    for name, prop in props.items():
        # If the class attribute (which is the default value for this
        # prop) exists and is of type 'Property', replace it with the
        # real default. This is so that normal class introspection
        # sees a real default value, not a Property.
        if isinstance(getattr(cls, name, None), Property):
            if prop.default is not MISSING:
                # If there's no default, delete the class attribute so
                # that it is not set at all in the post-processed class.
                delattr(cls, name)
            else:
                setattr(cls, name, prop.default)

    # Mark this class as an input type and save the properties.
    setattr(cls, _PULUMI_INPUT_TYPE, True)
    setattr(cls, _PULUMI_PROPERTIES, props)

    # Add a _to_dict func, if needed.
    if not hasattr(cls, _TO_DICT):
        _translate_property = getattr(cls, _TRANSLATE_PROPERTY, None)
        if callable(_translate_property):
            def _to_dict(self) -> dict:
                # Return a copy of `self.__dict__` with translated keys.
                return {
                    _translate_property(self, props[k].name if k in props else k): v
                        for k, v in self.__dict__.items()
                }
        else:
            def _to_dict(self) -> dict:
                # Return a copy of `self.__dict__`.
                return {
                    props[k].name if k in props else k: v
                        for k, v in self.__dict__.items()
                }
        setattr(cls, _TO_DICT, _to_dict)
    return cls

import dataclasses

#@dataclasses.dataclass
@input_type
class BucketWebsiteArgs:
    """The class docstring"""

    first_arg: str = property("firstArg")
    """The first argument"""

    second_arg: float = property("secondArg")
    """The second argument"""

    def __init__(self, first_arg, second_arg):
        """The init docstring"""
        self.first_arg = first_arg
        self.second_arg = second_arg


class BaseTestCase(unittest.TestCase):
    def assertHasAttr(self, obj, attrname: str, message=None):
        if not hasattr(obj, attrname):
            if message is not None:
                self.fail(message)
            else:
                self.fail("{} should have an attribute {}".format(obj, attrname))


class TestInputType(BaseTestCase):
    def test_bucket_website_args(self):
        f = BucketWebsiteArgs(first_arg="hello", second_arg=42)
        self.assertHasAttr(f, "_pulumi_input_type")
        self.assertHasAttr(f, "_to_dict")
        d = f._to_dict()
        self.assertEqual(d, {
            "firstArg": "hello",
            "secondArg": 42,
        })
