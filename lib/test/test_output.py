import unittest
import typing
import sys

import pulumi




def _output_types(cls: type) -> typing.Dict[str, typing.Tuple[type, bool]]:
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

    def get_result_value(val: type) -> typing.Optional[typing.Tuple[type, bool]]:
        if is_optional_type(val):
            args = get_args(val)
            assert len(args) == 2
            assert args[1] is type(None)
            val = args[0]

        origin = get_origin(val)
        if origin is list or origin is typing.List:
            args = get_args(val)
            assert len(args) == 1
            return (args[0], True)
        elif origin is dict or origin is typing.Dict:
            args = get_args(val)
            assert len(args) == 2
            assert args[0] is str
            return (args[1], True)
        else:
            return (val, False)

    r = {}
    for k, v in typing.get_type_hints(cls).items():
        # Skip id, urn, and keys that start with an underscore.
        if k in ["id", "urn"] or k.startswith("_"):
            continue

        # TODO skip non-outputs

        if get_origin(v) is pulumi.Output:
            args = get_args(v)
            assert len(args) == 1
            result_value = get_result_value(args[0])
            if result_value is not None:
                r[k] = result_value
    return r


class Property:
    def __init__(self, name: str) -> None:
        self.name = name
        pass

def property(name: str):
    return Property(name)


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
            "a0": (BucketAccelerationStatusArgs, False),
            "a1": (BucketAccelerationStatusArgs, False),
            "a2": (BucketAccelerationStatusArgs, False),
            "a3": (BucketAccelerationStatusArgs, True),
            "a4": (BucketAccelerationStatusArgs, True),
            "a5": (BucketAccelerationStatusArgs, True),
            "a6": (BucketAccelerationStatusArgs, False),
            "a7": (BucketAccelerationStatusArgs, False),
            "a8": (BucketAccelerationStatusArgs, False),
            "a9": (BucketAccelerationStatusArgs, False),
            "a10": (BucketAccelerationStatusArgs, True),
            "a11": (BucketAccelerationStatusArgs, True),
            "a12": (BucketAccelerationStatusArgs, True),
            "a13": (BucketAccelerationStatusArgs, True),
            "a14": (BucketAccelerationStatusArgs, True),
            "w1": (BucketWebsite, False),
            "w2": (BucketWebsite, True),
        })



