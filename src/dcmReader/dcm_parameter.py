"""Definition of DCM parameter"""
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
class DcmParameter(_DcmBase):
    """Definition of a parameter

    Attributes:
        name (str):         Name of the parameter
        description (str):  Description of the parameter, started by LANGNAME in DCM
        display_name (str): Parameter name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the parameter, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit (str):         Unit of the parameter, started by EINHEIT_W in DCM
        value (float/int):  Value of the parameter, started by WERT in DCM
        text (str):         Alternative text-value, started by TEXT in DCM
        comment (str):      Block comment
    """

    attrs: dict = field(default_factory=_attrs_init)
