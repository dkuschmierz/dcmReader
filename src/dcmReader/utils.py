"""
Definition of DCM characteristic map
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Protocol

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

if TYPE_CHECKING:
    try:
        from numpy.typing import ArrayLike
    except ImportError:
        from typing import Union

        ArrayLike = Union[float, list[float], list[list[float]]]


def _get_shape(ndarray: list | float) -> tuple[int, ...]:
    """
    Get the shape of array-like.

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
    """
    # https://stackoverflow.com/questions/51960857/how-can-i-get-a-list-shape-without-using-numpy
    if isinstance(ndarray, list):
        # More dimensions, so make a recursive call
        outermost_size = len(ndarray)
        if outermost_size == 0:
            return (outermost_size,)
        else:
            return (outermost_size, *_get_shape(ndarray[0]))
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
        return (
            self.attrs["function"] < other.attrs["function"] and self.attrs["description"] < other.attrs["description"]
        )

    def _print_dcm_format(self, name: str, is_function: False) -> str:
        """
        Print the data according to the dcm-format.

        Arrays longer than 6 are split to new line.

        Parameters
        ----------
        name : str
            Name of the block.
        is_function : False
            Is the block a 'FUNKTIONEN'.
        """

        def to_str(val: str | int | float | list, delimiter: str = " ") -> str:
            val_list: list = [val] if isinstance(val, (str, int, float)) else val
            return delimiter.join(map(str, val_list))

        def print_values(key: str, value: str | int | float | list, n: int = 6) -> str:
            """Print pairwise values prettily."""
            # Normalize so that val is always a list:
            value_list: list = [value] if isinstance(value, (str, int, float)) else value

            # Split too long lists into chunks.
            value_list_chunked = [value_list[i : i + n] for i in range(0, len(value_list), n)]

            out = ""
            for v in value_list_chunked:
                out += f"  {key: <13} {to_str(v)}\n"
            return out

        if is_function:
            return f'{name} {self.name} "{self.version}" "{self.description}"'

        shape_rev = list(reversed(self.shape))
        coords_rev = list(reversed(self.coords))
        ndim = self.ndim

        value = f"{name} {self.name} {to_str(shape_rev)}\n"

        ks = (
            ("LANGNAME", "description", lambda x: f'"{x}"'),
            ("FUNKTION", "function", lambda x: f"{x}"),
            ("DISPLAYNAME", "display_name", lambda x: f'"{x}"'),
            ("EINHEIT_X", "units_x", lambda x: f'"{x}"'),
            ("EINHEIT_Y", "units_y", lambda x: f'"{x}"'),
            ("EINHEIT_W", "units", lambda x: f'"{x}"'),
            ("*SSTX", "x_mapping", lambda x: f"{x}"),
            ("*SSTY", "y_mapping", lambda x: f"{x}"),
            # Printed after WERT:
            ("TEXT", "text", lambda x: f"{x}"),
            ("VAR", "variants", lambda x: f"{x}"),
        )
        idx_as_suffx = 2
        for k, v, f in ks[:-idx_as_suffx]:
            if self.attrs.get(v, ""):
                value += print_values(k, f"{f(self.attrs[v])}")

        if ndim > 0:
            value += print_values("ST/X", coords_rev[0])

        for i, val in enumerate(self.values if ndim > 1 else [self.values]):
            if ndim > 1:
                value += print_values("ST/Y", coords_rev[1][i])

            value += print_values("WERT", val)

        for k, v, f in ks[-idx_as_suffx:]:
            if self.attrs.get(v, ""):
                value += print_values(k, f"{f(self.attrs[v])}")

        value += "END"

        return value

    def __str__(self) -> str:
        is_function = self.block_type == "FUNKTIONEN"
        return self._print_dcm_format(self.block_type, is_function)
