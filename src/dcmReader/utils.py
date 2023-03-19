"""
Definition of DCM characteristic map
"""
from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING, Protocol

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

if TYPE_CHECKING:
    from typing import Union, Any, Callable, TypedDict

    from numpy.typing import ArrayLike

    T_Fmt = Callable[..., str]

    class T_Setting(TypedDict):
        key_ger: str
        key_eng: str
        print_key: str
        print_format: T_Fmt
        print_kwargs: dict[str, Any]
        parse_key: str
        parse_method: Callable

    T_Settings = dict[str, T_Setting]


_COMMENT_QUALIFIER = ("!", "*", ".")

_SETTINGS: T_Settings = {
    k: {
        "key_ger": k,
        "key_eng": "comment",
        "print_key": "*",
        "print_format": lambda x: f"{x}",
        "print_kwargs": {"pad": 0, "n": 1},
        "parse_key": "",  # comment
        "parse_method": lambda self: self._parse_comment,
    }
    for k in _COMMENT_QUALIFIER
}
_SETTINGS.update(
    {
        "LANGNAME": {
            "key_ger": "LANGNAME",
            "key_eng": "description",
            "print_key": "LANGNAME",
            "print_format": lambda x: f'"{x}"',
            "print_kwargs": {},
            "parse_key": "description",
            "parse_method": lambda self: self._parse_string,
        },
        "FUNKTION": {
            "key_ger": "FUNKTION",
            "key_eng": "function",
            "print_key": "FUNKTION",
            "print_format": lambda x: f"{x}",
            "print_kwargs": {},
            "parse_key": "function",
            "parse_method": lambda self: self._parse_string,
        },
        "DISPLAYNAME": {
            "key_ger": "DISPLAYNAME",
            "key_eng": "display_name",
            "print_key": "DISPLAYNAME",
            "print_format": lambda x: f'"{x}"',
            "print_kwargs": {},
            "parse_key": "display_name",
            "parse_method": lambda self: self._parse_string,
        },
        "EINHEIT_X": {
            "key_ger": "EINHEIT_X",
            "key_eng": "units_x",
            "print_key": "EINHEIT_X",
            "print_format": lambda x: f'"{x}"',
            "print_kwargs": {},
            "parse_key": "units_x",
            "parse_method": lambda self: self._parse_string,
        },
        "EINHEIT_Y": {
            "key_ger": "EINHEIT_Y",
            "key_eng": "units_y",
            "print_key": "EINHEIT_Y",
            "print_format": lambda x: f'"{x}"',
            "print_kwargs": {},
            "parse_key": "units_y",
            "parse_method": lambda self: self._parse_string,
        },
        "EINHEIT_W": {
            "key_ger": "EINHEIT_W",
            "key_eng": "units",
            "print_key": "EINHEIT_W",
            "print_format": lambda x: f'"{x}"',
            "print_kwargs": {},
            "parse_key": "units",
            "parse_method": lambda self: self._parse_string,
        },
        "ST/X": {
            "key_ger": "ST/X",
            "key_eng": "ST/X",
            "print_key": "ST/X",
            "print_format": lambda x: f"{x}",
            "print_kwargs": {},
            "parse_key": "",
            "parse_method": lambda self: self._parse_coord_x,
        },
        "ST/Y": {
            "key_ger": "ST/Y",
            "key_eng": "ST/Y",
            "print_key": "ST/Y",
            "print_format": lambda x: f"{x}",
            "print_kwargs": {},
            "parse_key": "",
            "parse_method": lambda self: self._parse_coord_y,
        },
        "SSTX": {
            # From comments:
            "key_ger": "SSTX",
            "key_eng": "name_x",
            "print_key": "*SSTX",
            "print_format": lambda x: f"{x}",
            "print_kwargs": {},
            "parse_key": "name_x",
            "parse_method": lambda self: self._parse_string,
        },
        "SSTY": {
            # From comments:
            "key_ger": "SSTY",
            "key_eng": "name_y",
            "print_key": "*SSTY",
            "print_format": lambda x: f"{x}",
            "print_kwargs": {},
            "parse_key": "name_y",
            "parse_method": lambda self: self._parse_string,
        },
        "WERT": {
            "key_ger": "WERT",
            "key_eng": "value",
            "print_key": "WERT",
            "print_format": lambda x: f"{x}",
            "print_kwargs": {},
            "parse_key": "",
            "parse_method": lambda self: self._parse_wert,
        },
        "TEXT": {
            "key_ger": "TEXT",
            "key_eng": "text",
            "print_key": "TEXT",
            "print_format": lambda x: f'"{x}"',
            "print_kwargs": {},
            "parse_key": "",
            "parse_method": lambda self: self._parse_text,
        },
        "VAR": {
            "key_ger": "VAR",
            "key_eng": "variants",
            "print_key": "VAR",
            "print_format": lambda x: ", ".join(
                [f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}" for k, v in x.items()]
            ),
            "print_kwargs": {},
            "parse_key": "variants",
            "parse_method": lambda self: self._parse_variant,
        },
    }
)


class _HasValuesProtocol(Protocol):
    values: np.ndarray


class ShapeRelatedMixin(_HasValuesProtocol):
    @property
    def shape(self) -> tuple[int, ...]:
        """
        Get shape of array.

        See Also
        --------
        numpy.ndarray.shape
        """
        return self.values.shape

    @property
    def ndim(self) -> int:
        """
        Get number of array dimensions.

        See Also
        --------
        numpy.ndarray.ndim
        """
        return self.values.ndim

    @property
    def size(self) -> int:
        """
        Get number of elements in the array.

        See Also
        --------
        numpy.ndarray.size
        """
        return self.values.size

    def __len__(self) -> int:
        return len(self.values)


def _fmt_base(x) -> str:
    return f"{x}"


def _to_str(val: ArrayLike, fmt: T_Fmt = _fmt_base, delimiter: str = " ") -> str:
    val_list = np.atleast_1d(val)

    out = delimiter.join(map(fmt, val_list))
    return out


def _print_values(key: str, value: ArrayLike, fmt: T_Fmt = _fmt_base, n: int = 6, pad: int = 14) -> str:
    """Print pairwise values prettily."""
    # Normalize so that value is always a list:
    value_list = np.atleast_1d(value)

    # Split strings that contains a newline:
    if value_list.dtype.kind in {"U", "S"}:
        value_list = np.array("\n".join(value_list).split("\n"))

    # Split too long lists into chunks.
    value_list_chunked = [value_list[i : i + n] for i in range(0, len(value_list), n)]

    # Return the key and value in a table-format:
    pad_ = f"<{pad}"
    out = ""
    for v in value_list_chunked:
        value_str = _to_str(v, fmt)
        out += f"  {key:{pad_}}{value_str}\n"
    return out


@dataclass
class _DcmBase(ShapeRelatedMixin):
    name: str
    values: np.ndarray = field(default_factory=lambda: np.array([]))
    coords: tuple[np.ndarray, ...] = field(default_factory=tuple)
    dims: tuple[str, ...] = field(default_factory=tuple)
    attrs: dict = field(default_factory=dict)
    element_syntax: str = ""

    def __lt__(self, other) -> bool:
        self_function = self.attrs.get("function", "")
        self_description = self.attrs.get("description", "")
        other_function = other.attrs.get("function", "")
        other_description = other.attrs.get("description", "")
        return self_function < other_function and self_description < other_description

    def _print_attrs(self, k: str, value: str) -> str:
        setting = _SETTINGS[k]
        key_eng = setting["key_eng"]

        attrs_value = self.attrs.get(key_eng, "")
        if attrs_value:
            print_key = setting["print_key"]
            print_val = attrs_value
            print_format = setting["print_format"]
            print_kwargs = setting["print_kwargs"]

            value += _print_values(print_key, print_val, print_format, **print_kwargs)

        return value

    def _print_dcm_format(self) -> str:
        """
        Print the data according to the dcm-format.
        """

        ndim = self.ndim
        shape_rev: list[int | str] = list(reversed(self.shape))
        if self.element_syntax == "FESTWERTEBLOCK" and ndim == 2:
            shape_rev.insert(1, "@")
        coords_rev = list(reversed(self.coords))
        ncoords = len(coords_rev)

        # Header:
        shape_str = _to_str(shape_rev)
        value = f"{self.element_syntax} {self.name} {shape_str}\n"

        # Attributes printed before the values:
        for k in _SETTINGS.keys():
            if k in ("WERT", "ST/X", "ST/Y", "VAR") + _COMMENT_QUALIFIER[:-1]:
                continue

            value = self._print_attrs(k, value)

        # x-values:
        if ncoords > 0:
            value += _print_values("ST/X", coords_rev[0], _SETTINGS["ST/X"]["print_format"])

        # y-value and values:
        print_key_val = "TEXT" if self.values.dtype.kind in ("S", "U") else "WERT"
        for i, val in enumerate(np.atleast_2d(self.values)):
            if ncoords > 1:
                value += _print_values("ST/Y", coords_rev[1][i], _SETTINGS["ST/Y"]["print_format"])

            value += _print_values(print_key_val, val, _SETTINGS[print_key_val]["print_format"])

        # # Attributes printed after the values:
        for k in ("VAR",):
            value = self._print_attrs(k, value)

        # Close:
        value += "END"

        return value

    def __str__(self) -> str:
        return self._print_dcm_format()
