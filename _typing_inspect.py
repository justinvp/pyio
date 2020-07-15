# A pared down copy of get_origin and get_args from https://github.com/ilevkivskyi/typing_inspect
# that will work on Python 3.6+.

import sys

NEW_TYPING = sys.version_info[:3] >= (3, 7, 0) # PEP 560

if NEW_TYPING:
    import collections.abc
    from typing import (
        Generic, Union, ClassVar, Tuple, _GenericAlias
    )
else:
    from typing import (
        CallableMeta, Union, Tuple, TupleMeta, GenericMeta, _Union
    )


def _gorg(cls):
    """This function exists for compatibility with old typing versions."""
    assert isinstance(cls, GenericMeta)
    if hasattr(cls, '_gorg'):
        return cls._gorg
    while cls.__origin__ is not None:
        cls = cls.__origin__
    return cls


def is_generic_type(tp):
    """Test if the given type is a generic type. This includes Generic itself, but
    excludes special typing constructs such as Union, Tuple, Callable, ClassVar.
    Examples::

        is_generic_type(int) == False
        is_generic_type(Union[int, str]) == False
        is_generic_type(Union[int, T]) == False
        is_generic_type(ClassVar[List[int]]) == False
        is_generic_type(Callable[..., T]) == False

        is_generic_type(Generic) == True
        is_generic_type(Generic[T]) == True
        is_generic_type(Iterable[int]) == True
        is_generic_type(Mapping) == True
        is_generic_type(MutableMapping[T, List[int]]) == True
        is_generic_type(Sequence[Union[str, bytes]]) == True
    """
    if NEW_TYPING:
        return (isinstance(tp, type) and issubclass(tp, Generic) or
                isinstance(tp, _GenericAlias) and
                tp.__origin__ not in (Union, tuple, ClassVar, collections.abc.Callable))
    return (isinstance(tp, GenericMeta) and not
            isinstance(tp, (CallableMeta, TupleMeta)))


def is_tuple_type(tp):
    """Test if the type is a generic tuple type, including subclasses excluding
    non-generic classes.
    Examples::

        is_tuple_type(int) == False
        is_tuple_type(tuple) == False
        is_tuple_type(Tuple) == True
        is_tuple_type(Tuple[str, int]) == True
        class MyClass(Tuple[str, int]):
            ...
        is_tuple_type(MyClass) == True

    For more general tests use issubclass(..., tuple), for more precise test
    (excluding subclasses) use::

        get_origin(tp) is tuple  # Tuple prior to Python 3.7
    """
    if NEW_TYPING:
        return (tp is Tuple or isinstance(tp, _GenericAlias) and
                tp.__origin__ is tuple or
                isinstance(tp, type) and issubclass(tp, Generic) and
                issubclass(tp, tuple))
    return type(tp) is TupleMeta


def is_optional_type(tp):
    """Test if the type is type(None), or is a direct union with it, such as Optional[T].

    NOTE: this method inspects nested `Union` arguments but not `TypeVar` definition
    bounds and constraints. So it will return `False` if
     - `tp` is a `TypeVar` bound, or constrained to, an optional type
     - `tp` is a `Union` to a `TypeVar` bound or constrained to an optional type,
     - `tp` refers to a *nested* `Union` containing an optional type or one of the above.

    Users wishing to check for optionality in types relying on type variables might wish
    to use this method in combination with `get_constraints` and `get_bound`
    """

    if tp is type(None):  # noqa
        return True
    elif is_union_type(tp):
        return any(is_optional_type(tt) for tt in get_args(tp, evaluate=True))
    else:
        return False


def is_union_type(tp):
    """Test if the type is a union type. Examples::

        is_union_type(int) == False
        is_union_type(Union) == True
        is_union_type(Union[int, int]) == False
        is_union_type(Union[T, int]) == True
    """
    if NEW_TYPING:
        return (tp is Union or
                isinstance(tp, _GenericAlias) and tp.__origin__ is Union)
    return type(tp) is _Union


def get_origin(tp):
    """Get the unsubscripted version of a type. Supports generic types, Union,
    Callable, and Tuple. Returns None for unsupported types. Examples::

        get_origin(int) == None
        get_origin(ClassVar[int]) == None
        get_origin(Generic) == Generic
        get_origin(Generic[T]) == Generic
        get_origin(Union[T, int]) == Union
        get_origin(List[Tuple[T, T]][int]) == list  # List prior to Python 3.7
    """
    if NEW_TYPING:
        if isinstance(tp, _GenericAlias):
            return tp.__origin__
        return None
    if isinstance(tp, GenericMeta):
        return _gorg(tp)
    if is_union_type(tp):
        return Union
    if is_tuple_type(tp):
        return Tuple

    return None




def _eval_args(args):
    """Internal helper for get_args."""
    res = []
    for arg in args:
        if not isinstance(arg, tuple):
            res.append(arg)
        else:
            res.append(type(arg[0]).__getitem__(arg[0], _eval_args(arg[1:])))
    return tuple(res)


def get_args(tp, evaluate=None):
    """Get type arguments with all substitutions performed. For unions,
    basic simplifications used by Union constructor are performed.
    On versions prior to 3.7 if `evaluate` is False (default),
    report result as nested tuple, this matches
    the internal representation of types. If `evaluate` is True
    (or if Python version is 3.7 or greater), then all
    type parameters are applied (this could be time and memory expensive).
    Examples::

        get_args(int) == ()
        get_args(Union[int, Union[T, int], str][int]) == (int, str)
        get_args(Union[int, Tuple[T, int]][str]) == (int, (Tuple, str, int))

        get_args(Union[int, Tuple[T, int]][str], evaluate=True) == \
                 (int, Tuple[str, int])
        get_args(Dict[int, Tuple[T, T]][Optional[int]], evaluate=True) == \
                 (int, Tuple[Optional[int], Optional[int]])
        get_args(Callable[[], T][int], evaluate=True) == ([], int,)
    """
    if NEW_TYPING:
        if evaluate is not None and not evaluate:
            raise ValueError('evaluate can only be True in Python >= 3.7')
        if isinstance(tp, _GenericAlias):
            return tp.__args__
        return ()

    if is_generic_type(tp) or is_union_type(tp) or is_tuple_type(tp):
        tree = tp._subs_tree()
        if isinstance(tree, tuple) and len(tree) > 1:
            if not evaluate:
                return tree[1:]
            return _eval_args(tree[1:])

    return ()
