"""
Definition of DCM characteristic map
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dcmReader.utils import _DcmBase


def _attrs_init() -> dict:
    return {
        "description": "",
        "display_name": "",
        "variants": {},
        "function": "",
        "units_x": "",
        "units_y": "",
        "units": "",
    }


@dataclass
class DcmCharacteristicMap(_DcmBase):
    """Definition of a characteristic map

    Attributes:
        name (str):         Name of the characteristic map
        description (str):  Description of the characteristic map, started by LANGNAME in DCM
        display_name (str):  Characteristic map name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the characteristic map, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit_x (str):        Unit of the x axis values, started by EINHEIT_X in DCM
        unit_y (str):        Unit of the y axis values, started by EINHEIT_Y in DCM
        unit_values (str):   Unit of the values, started by EINHEIT_W in DCM
        values (dict):      2D Dict of values of the parameter
                            The inner dict contains the values from ST/X as keys and the
                            values retrieved from WERT as values. The keys of the outer dict
                            contains the values from ST/Y.
        x_dimension (int):   Dimension in x direction of the characteristic maps
        y_dimension (int):   Dimension in y direction of the characteristic maps
    """

    attrs: dict = field(default_factory=_attrs_init)
