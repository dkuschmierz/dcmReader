"""
Definition of DCM characteristic map
"""
from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING, Protocol

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from typing import Union

    ArrayLike = float | str | list[float | str] | list[list[float | str]]


def _get_shape(array_like: ArrayLike, *, check_if_ragged: bool = False) -> tuple[int, ...]:
    """
    Get the shape of array_like.

    Examples
    --------
    >>> _get_shape(1)
    ()
    >>> _get_shape([])
    (0,)
    >>> _get_shape([1])
    (1,)
    >>> _get_shape([[1]])
    (1, 1)
    >>> _get_shape([[1], [2]])
    (2, 1)

    Calculating the shape from a ragged sequence does not work. It's possible to check
    for these inconsistencies although at a cost of performance:

    >>> try:
    >>>     _get_shape([[0, 1, 2], [4, 5]], check_if_ragged=True)
    >>> except ValueError as e:
    >>>     msg = str(e)
    >>>     print(f"{msg[:48]} (...) {msg[-17:]}")
    >>> _get_shape([[0, 1, 2], [4, 5]], check_if_ragged=True)
    Calculating a shape from ragged nested sequences (...) is not supported.
    """
    # https://stackoverflow.com/questions/51960857/how-can-i-get-a-list-shape-without-using-numpy
    if isinstance(array_like, list):
        # More dimensions, so make a recursive call
        outermost_size = len(array_like)
        if outermost_size == 0:
            return (outermost_size,)
        else:
            if check_if_ragged:
                # This costs some
                it = iter(array_like)
                the_len = len(next(it))
                if not all(len(l) == the_len for l in it):
                    raise ValueError(
                        "Calculating a shape from ragged nested sequences "
                        "(which is a list-or-tuple of lists-or-tuples "
                        "with different lengths or shapes) is not supported."
                    )
            return (outermost_size, *_get_shape(array_like[0]))
    else:
        # No more dimensions, so we're done
        return ()


class _HasValuesProtocol(Protocol):
    values: ArrayLike


class ShapeRelatedMixin(_HasValuesProtocol):
    @property
    def shape(self) -> tuple[int, ...]:
        """
        Get shape of array.

        See Also
        --------
        numpy.ndarray.shape
        """
        return _get_shape(self.values)

    @property
    def ndim(self) -> int:
        """
        Get number of array dimensions.

        See Also
        --------
        numpy.ndarray.ndim
        """
        return len(self.shape)

    @property
    def size(self) -> int:
        """
        Get number of elements in the array.

        See Also
        --------
        numpy.ndarray.size
        """
        return math.prod(self.shape)

    def __len__(self) -> int:
        try:
            return self.shape[0]
        except IndexError:
            raise TypeError("len() of unsized object")


def _to_str(val: str | int | float | list, delimiter: str = " ") -> str:
    val_list: list = [val] if isinstance(val, (str, int, float)) else val
    return delimiter.join(map(str, val_list))


def _print_values(key: str, value: str | int | float | list, n: int = 6, pad: int = 14) -> str:
    """Print pairwise values prettily."""
    # Normalize so that value is always a list:
    value_list: list = [value] if isinstance(value, (str, int, float)) else value

    # Split too long lists into chunks.
    value_list_chunked = [value_list[i : i + n] for i in range(0, len(value_list), n)]

    # Return the key and value in a table-format:
    pad_ = f"<{pad}"
    out = ""
    for v in value_list_chunked:
        out += f"  {key:{pad_}}{_to_str(v)}\n"
    return out


def _attrs_init() -> dict:
    return {
        "description": "",
        "display_name": "",
        "variants": {},
        "text": "",
        "function": "",
        "units_x": "",
        "units_y": "",
        "units": "",
    }


@dataclass
class _DcmBase(ShapeRelatedMixin):
    name: str
    values: ArrayLike = field(default_factory=list)
    coords: tuple[ArrayLike, ...] = field(default_factory=tuple)
    dims: tuple[str, ...] = field(default_factory=tuple)
    attrs: dict = field(default_factory=_attrs_init)
    block_type: str = ""

    def __lt__(self, other):
        self_function = self.attrs.get("function", None)
        self_description = self.attrs.get("descrition", None)
        other_function = other.attrs.get("function", None)
        other_description = other.attrs.get("descrition", None)
        return self_function < other_function and self_description < other_description

    def _print_dcm_format(self) -> str:
        """
        Print the data according to the dcm-format.
        """

        if self.block_type == "FUNKTIONEN":
            return f'{self.block_type} {self.name} "{self.version}" "{self.description}"'

        ndim = self.ndim
        shape_rev: list[int | str] = list(reversed(self.shape))
        if self.block_type == "FESTWERTEBLOCK" and ndim == 2:
            shape_rev.insert(1, "@")
        coords_rev = list(reversed(self.coords))

        # Header:
        value = f"{self.block_type} {self.name} {_to_str(shape_rev)}\n"

        # Attributes printed before the values:
        ks = (
            # TODO: Should comments be reprinted? They have currently lost the position
            # so the comment might be out of context.
            # ("*", "comment", lambda x: f"{', '.join(x.split(os.linesep))}", {"pad": 0, "n": 1}),
            ("LANGNAME", "description", lambda x: f'"{x}"', {}),
            ("FUNKTION", "function", lambda x: f"{x}", {}),
            ("DISPLAYNAME", "display_name", lambda x: f'"{x}"', {}),
            ("EINHEIT_X", "units_x", lambda x: f'"{x}"', {}),
            ("EINHEIT_Y", "units_y", lambda x: f'"{x}"', {}),
            ("EINHEIT_W", "units", lambda x: f'"{x}"', {}),
            ("*SSTX", "x_mapping", lambda x: f"{x}", {}),
            ("*SSTY", "y_mapping", lambda x: f"{x}", {}),
            # Printed after WERT:
            ("TEXT", "text", lambda x: f"{x}", {}),  # Is this equivalent to WERT?
            ("VAR", "variants", lambda x: f"{x}", {}),
        )
        idx_as_suffx = 2
        for k, v, f, kws in ks[:-idx_as_suffx]:
            if self.attrs.get(v, ""):
                value += _print_values(k, f"{f(self.attrs[v])}", **kws)

        # x-values:
        if ndim > 0:
            value += _print_values("ST/X", coords_rev[0])

        # y-value and values:
        for i, val in enumerate(self.values if ndim > 1 else [self.values]):
            if ndim > 1:
                value += _print_values("ST/Y", coords_rev[1][i])

            value += _print_values("WERT", val)

        # Attributes printed after the values:
        for k, v, f, kws in ks[-idx_as_suffx:]:
            if self.attrs.get(v, ""):
                value += _print_values(k, f"{f(self.attrs[v])}", **kws)

        # Close:
        value += "END"

        return value

    def __str__(self) -> str:
        return self._print_dcm_format()
