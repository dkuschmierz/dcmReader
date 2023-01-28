"""
Definition of DCM characteristic line
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dcmReader.utils import _DcmBase


def _attrs_init() -> dict:
    return {}
    # return {
    #     "description": "",
    #     "display_name": "",
    #     "variants": {},
    #     "function": "",
    #     "units_x": "",
    #     "units_y": "",
    #     "units": "",
    # }


@dataclass
class DcmFunction(_DcmBase):
    """Definition of a function

    Attributes:
        name (str):         Name of the function
        version (str):      Version number of the function
        description (str):  Description of the function
    """

    attrs: dict = field(default_factory=_attrs_init)

    def _print_dcm_format(self) -> str:
        version = self.attrs.get("version", "")
        description = self.attrs.get("description", "")
        return f'{self.element_syntax} {self.name} "{version}" "{description}"'


@dataclass
class DcmVariantCoding(_DcmBase):
    """Definition of a function

    Attributes:
        name (str):         Name of the function
        version (str):      Version number of the function
        description (str):  Description of the function
    """

    attrs: dict = field(default_factory=_attrs_init)

    def _print_dcm_format(self) -> str:
        raise NotImplementedError


@dataclass
class DcmModuleHeader(_DcmBase):
    """Definition of a function

    Attributes:
        name (str):         Name of the function
        version (str):      Version number of the function
        description (str):  Description of the function
    """

    attrs: dict = field(default_factory=_attrs_init)

    def _print_dcm_format(self) -> str:
        raise NotImplementedError


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


@dataclass
class DcmParameterBlock(_DcmBase):
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


@dataclass
class DcmCharacteristicLine(_DcmBase):
    """Definition of a characteristic line

    Attributes:
        name (str):         Name of the characteristic line
        description (str):  Description of the characteristic line, started by LANGNAME in DCM
        display_name (str): Characteristic line name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the characteristic line, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit_x (str):       Unit of the x axis values, started by EINHEIT_X in DCM
        unit_values (str):  Unit of the values, started by EINHEIT_W in DCM
        values (dict):      Dict of values of the parameter, KEYs are retrieved from ST/X,
                            values are retrieved from WERT
        x_dimension (int):  Dimension in x direction of the parameter block
        x_mapping (str):    Mapping of the x axis to a distribution, if available as a comment in DCM
        comment (str):      Block comment
    """

    attrs: dict = field(default_factory=_attrs_init)


class DcmFixedCharacteristicLine(DcmCharacteristicLine):
    """Definition of a fixed characteristic line, derived from characteristic line"""


class DcmGroupCharacteristicLine(DcmCharacteristicLine):
    """Definition of a group characteristic line, derived from characteristic line"""


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


class DcmFixedCharacteristicMap(DcmCharacteristicMap):
    """Definition of a fixed characteristic map, derived from characteristic map"""


class DcmGroupCharacteristicMap(DcmCharacteristicMap):
    """Definition of a group characteristic map, derived from characteristic map"""


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
