"""
Definition of DCM characteristic line
"""
from dataclasses import dataclass


@dataclass
class DcmCharacteristicLine:
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

    def __init__(self, name) -> None:
        self.name = name
        self.values = {}
        self.description = None
        self.display_name = None
        self.variants = {}
        self.function = None
        self.unit_x = None
        self.unit_values = None
        self.x_dimension = 0
        self.x_mapping = None
        self.comment = None
        self._type_name = "KENNLINIE"

    def __str__(self):
        value = f"{self._type_name} {self.name} {self.x_dimension}\n"

        if self.comment:
            for line in self.comment.splitlines(True):
                value += f"* {line}"
        if self.description:
            value += f'  LANGNAME      "{self.description}"\n'
        if self.function:
            value += f'  FUNKTION      "{self.function}"\n'
        if self.display_name:
            value += f"  DISPLAYNAME   {self.display_name}\n"
        if self.unit_x:
            value += f'  EINHEIT_X     "{self.unit_x}"\n'
        if self.unit_values:
            value += f'  EINHEIT_W     "{self.unit_values}"\n'
        if self.x_mapping:
            value += f'*SSTX   {self.x_mapping}\n'
        if self.values:
            x_entries = ""
            value_entries = ""
            for x_entry, value_entry in self.values.items():
                x_entries += f"{str(x_entry)} "
                value_entries += f"{str(value_entry)} "
            value += f'  ST/X          {x_entries.strip()}\n'
            value += f'  WERT          {value_entries.strip()}\n'
        for var_name, var_value in self.variants.items():
            value += f"  VAR           {var_name}={var_value}\n"

        value += "END"

        return value

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
