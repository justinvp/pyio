import unittest
import typing
import sys

import pulumi

class BucketAccelerationStatusArgs(dict):
    pass

class BucketWebsite(dict):
    pass

class Bucket(pulumi.CustomResource):
    acceleration_status: pulumi.Output[BucketAccelerationStatusArgs]
    website: pulumi.Output['BucketWebsite']
    objects: pulumi.Output[typing.List[BucketAccelerationStatusArgs]]
    tags: 'pulumi.Output[typing.Dict[str, BucketWebsite]]'

    def __init__(__self__, resource_name):
        super().__init__(
            'aws:s3/bucket:Bucket',
            resource_name,
            dict(),
            None)


def _output_types(cls: type) -> typing.Dict[str, typing.Tuple[type, bool]]:
    # Python 3.8 has get_origin() and get_args().
    if sys.version_info[:2] >= (3, 8):
        get_origin = typing.get_origin
        get_args = typing.get_args
    else:
        def get_origin(tp):
            if hasattr(tp, "__origin__"):
                return tp.__origin__
            return None

        def get_args(tp):
            if hasattr(tp, "__args__"):
                return tp.__args__
            return ()

    def get_result_value(val: type) -> typing.Optional[typing.Tuple[type, bool]]:
        # TODO need to check to see if it is an output dict type
        # TODO need to handle Optional
        origin = get_origin(val)
        if origin is list or origin is typing.List:
            args = get_args(val)
            if len(args) > 0:
                return (args[0], True)
        elif origin is dict or origin is typing.Dict:
            args = get_args(val)
            if len(args) > 1:
                assert args[0] is str
                return (args[1], True)
        else:
            return (val, False)
        return None


    r = {}
    for key, value in typing.get_type_hints(Bucket).items():
        # Skip id, urn, and keys that start with underscore.
        if key in ["id", "urn"] or key.startswith("_"):
            continue

        if get_origin(value) is pulumi.Output:
            args = get_args(value)
            if len(args) > 0:
                result_value = get_result_value(args[0])
                if result_value is not None:
                    r[key] = result_value
    return r


class TestHello(unittest.TestCase):
    def test_hello(self):
        self.assertTrue(True)

    def test_output_types(self):
        self.assertEqual(_output_types(Bucket), {
            "acceleration_status": (BucketAccelerationStatusArgs, False),
            "website": (BucketWebsite, False),
            "objects": (BucketAccelerationStatusArgs, True),
            "tags": (BucketWebsite, True),
        })

