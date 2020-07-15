import unittest
import typing
from typing import get_type_hints, Dict, Any
import sys

import pulumi
from pulumi.runtime.known_types import output


_PULUMI_INPUT_TYPE = "_pulumi_input_type"
_PULUMI_OUTPUT_TYPE = "_pulumi_output_type"
_PULUMI_PROPERTIES = "_pulumi_properties"
_TO_DICT = "_to_dict"
_TRANSLATE_PROPERTY = "_translate_property"


class _MISSING_TYPE:
    pass
MISSING = _MISSING_TYPE()
"""
MISSING is a singleton sentinel objec to detec if a parameter is supplied or not.
"""

class Property:
    """TODO"""
    def __init__(self, name: str, default: Any = MISSING) -> None:
        self.name = name
        self.default = default
        self.type: Any = None


def input_property(name: str, default: Any = MISSING):
    """TODO"""
    return Property(name, default)


def output_property(name: str):
    """TODO"""
    return Property(name)

# TODO
def _get_properties(cls: type) -> Dict[str, Property]:
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
    cls_hints = get_type_hints(cls)

    # Properties.
    return {
        name: _get_property(cls, name, cls_hints[name])
        for name in cls_annotations
    }


def _get_property(cls: type, a_name: str, a_type: type) -> Property:
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, Property):
        f = default
    else:
        f = Property(name=a_name, default=default)

    f.type = a_type

    return f


def _output_types(cls: type) -> typing.Dict[str, typing.Any]:
    # Use the built-in `get_origin` and `get_args` functions on Python 3.8+,
    # otherwise fallback to downlevel implementations.
    if sys.version_info[:2] >= (3, 8):
        get_origin = typing.get_origin
        get_args = typing.get_args
    else:
        def get_origin(tp):
            if sys.version_info[:2] >= (3, 7):
                if isinstance(tp, typing._GenericAlias):
                    return tp.__origin__
            else:
                if hasattr(tp, "__origin__"):
                    return tp.__origin__
            return None

        def get_args(tp):
            if sys.version_info[:2] >= (3, 7):
                if isinstance(tp, typing._GenericAlias):
                    return tp.__args__
            else:
                if hasattr(tp, "__args__"):
                    return tp.__args__
            return ()

    def is_union_type(tp):
        if sys.version_info[:2] >= (3, 7):
            return (tp is typing.Union or
                    isinstance(tp, typing._GenericAlias) and tp.__origin__ is typing.Union)
        return type(tp) is typing._Union

    def is_optional_type(tp):
        if tp is type(None):
            return True
        elif is_union_type(tp):
            return any(is_optional_type(tt) for tt in get_args(tp))
        else:
            return False

    def get_result_value(val: type) -> type:
        origin = get_origin(val)
        if origin is pulumi.Output:
            args = get_args(val)
            assert len(args) == 1
            val = args[0]

        if is_optional_type(val):
            args = get_args(val)
            assert len(args) == 2
            assert args[1] is type(None)
            val = args[0]

        return val

        # origin = get_origin(val)
        # if origin is list or origin is typing.List:
        #     args = get_args(val)
        #     assert len(args) == 1
        #     return (args[0], True)
        # elif origin is dict or origin is typing.Dict:
        #     args = get_args(val)
        #     assert len(args) == 2
        #     assert args[0] is str
        #     return (args[1], True)
        # else:
        #     return (val, False)

    props = _get_properties(cls)
    return {
        name: get_result_value(prop.type) for name, prop in props.items()
    }


    # r = {}
    # for k, v in typing.get_type_hints(cls).items():
    #     # Skip id, urn, and keys that start with an underscore.
    #     if k in ["id", "urn"] or k.startswith("_"):
    #         continue

    #     # TODO skip non-outputs

    #     if get_origin(v) is pulumi.Output:
    #         args = get_args(v)
    #         assert len(args) == 1
    #         result_value = get_result_value(args[0])
    #         if result_value is not None:
    #             r[k] = result_value
    # return r




class BucketAccelerationStatusArgs(dict):
    pass

class BucketWebsite(dict):
    pass

class Bucket(pulumi.CustomResource):
    a0: 'pulumi.Output[BucketAccelerationStatusArgs]'
    a1: pulumi.Output[BucketAccelerationStatusArgs]
    a2: pulumi.Output['BucketAccelerationStatusArgs']
    a3: pulumi.Output[typing.List[BucketAccelerationStatusArgs]]
    a4: pulumi.Output[typing.List['BucketAccelerationStatusArgs']]
    a5: pulumi.Output['typing.List[BucketAccelerationStatusArgs]']
    a6: pulumi.Output[typing.Optional[BucketAccelerationStatusArgs]]
    a7: pulumi.Output[typing.Optional['BucketAccelerationStatusArgs']]
    a8: pulumi.Output['typing.Optional[BucketAccelerationStatusArgs]']
    a9: 'pulumi.Output[typing.Optional[BucketAccelerationStatusArgs]]'
    a10: pulumi.Output[typing.Optional[typing.List[BucketAccelerationStatusArgs]]]
    a11: pulumi.Output[typing.Optional[typing.List['BucketAccelerationStatusArgs']]]
    a12: pulumi.Output[typing.Optional['typing.List[BucketAccelerationStatusArgs]']]
    a13: pulumi.Output['typing.Optional[typing.List[BucketAccelerationStatusArgs]]']
    a14: 'pulumi.Output[typing.Optional[typing.List[BucketAccelerationStatusArgs]]]'

    w1: pulumi.Output['BucketWebsite']
    w2: 'pulumi.Output[typing.Dict[str, BucketWebsite]]'

    def __init__(__self__, resource_name):
        super().__init__(
            'aws:s3/bucket:Bucket',
            resource_name,
            dict(),
            None)

class TestOutputType(unittest.TestCase):
    def test_output_types(self):
        self.assertEqual(_output_types(Bucket), {
            "a0": BucketAccelerationStatusArgs,
            "a1": BucketAccelerationStatusArgs,
            "a2": BucketAccelerationStatusArgs,
            "a3": typing.List[BucketAccelerationStatusArgs],
            "a4": typing.List[BucketAccelerationStatusArgs],
            "a5": typing.List[BucketAccelerationStatusArgs],
            "a6": BucketAccelerationStatusArgs,
            "a7": BucketAccelerationStatusArgs,
            "a8": BucketAccelerationStatusArgs,
            "a9": BucketAccelerationStatusArgs,
            "a10": typing.List[BucketAccelerationStatusArgs],
            "a11": typing.List[BucketAccelerationStatusArgs],
            "a12": typing.List[BucketAccelerationStatusArgs],
            "a13": typing.List[BucketAccelerationStatusArgs],
            "a14": typing.List[BucketAccelerationStatusArgs],
            "w1": BucketWebsite,
            "w2": typing.Dict[str, BucketWebsite],
        })



