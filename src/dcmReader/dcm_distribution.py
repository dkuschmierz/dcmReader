"""
Definition of DCM distribution
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
        # "units": "",
        "comment": "",
    }


@dataclass
class DcmDistribution(_DcmBase):
    """Definition of a distribution

    Attributes:
        name (str):         Name of the distribution
        description (str):  Description of the distribution, started by LANGNAME in DCM
        display_name (str):  Distribution name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the distribution, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit_x (str):        Unit of the x axis values, started by EINHEIT_X in DCM
        values (list):      List of values of the distribution, values are retrieved from WERT
        x_dimension (int):   Dimension in x direction of the distribution
        comment (str):      Block comment
    """

    attrs: dict = field(default_factory=_attrs_init)
