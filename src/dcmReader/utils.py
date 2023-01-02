from __future__ import annotations

import math
from typing import Protocol

from dataclasses import dataclass, field


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


class HasValuesProtocol(Protocol):
    values: list[list[float]]


class ShapeRelatedMixin(HasValuesProtocol):
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


@dataclass
class _DcmBase(ShapeRelatedMixin):
    name: str
    values: list[list[float]] = field(default_factory=list)
    coords: tuple[list[float], ...] = field(default_factory=tuple)
    attrs: dict = field(default_factory=dict)
    block_type: str = ""

    def __lt__(self, other):
        return (
            self.attrs["function"] < other.attrs["function"]
            and self.attrs["description"] < other.attrs["description"]
        )

    def _print_str(self, name: str, is_function: False) -> str:
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

        def chunked(val, n=6):
            yield from [val[i : i + n] for i in range(0, len(val), n)]

        def to_str(list_: str | int | float | list) -> str:
            list__: list = [list_] if isinstance(list_, (str, int, float)) else list_
            return " ".join(map(str, list__))

        if is_function:
            return f'{name} {self.name} "{self.version}"  "{self.description}"'

        value = f"{name} {self.name} {to_str(self.shape)}\n"

        ks = (
            ("LANGNAME", "description", lambda x: f'"{x}"'),
            ("FUNKTION", "function", lambda x: f"{x}"),
            ("DISPLAYNAME", "display_name", lambda x: f'"{x}"'),
            ("EINHEIT_X", "units_x", lambda x: f'"{x}"'),
            ("EINHEIT_Y", "units_y", lambda x: f'"{x}"'),
            ("EINHEIT_W", "units", lambda x: f'"{x}"'),
        )
        for k, v, f in ks:
            if self.attrs.get(v, ""):
                value += f"  {k: <13} {f(self.attrs[v])}\n"

        ndim = self.ndim
        for i, (coord, coord_label) in enumerate(zip(self.coords, ("X", "Y"))):
            lbl = f"ST/{coord_label}"
            value += f"  {lbl: <13} {to_str(coord)}\n"

            if i == ndim - 1:
                for value_entries in chunked(self.values[i]):
                    value += f"  {'WERT': <13} {to_str(value_entries)}\n"

        # for i, x_entries in enumerate(chunked(self.coords[0])):
        #     value += f"  {'ST/X': <13} {to_str(x_entries)}\n"

        # for i, y_entry in enumerate(self.coords[1]):
        #     value += f"  {'ST/Y': <13} {y_entry}\n"

        #     for value_entries in chunked(self.values[i]):
        #         value += f"  {'WERT': <13} {to_str(value_entries)}\n"

        for var_name, var_value in self.attrs["variants"].items():
            value += f"  {'VAR': <13} {var_name}={var_value}\n"

        value += "END"

        return value

    def __str__(self) -> str:
        is_function = True if self.block_type == "FUNKTIONEN" else False
        return self._print_str(self.block_type, is_function)
