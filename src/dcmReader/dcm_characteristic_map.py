"""
Definition of DCM characteristic map
"""
from dataclasses import dataclass


@dataclass
class DcmCharacteristicMap:
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
        x_mapping (str):    Mapping of the x axis to a distribution, if available as a comment in DCM
        y_mapping (str):    Mapping of the y axis to a distribution, if available as a comment in DCM
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
        self.unit_y = None
        self.unit_values = None
        self.x_dimension = 0
        self.y_dimension = 0
        self.x_mapping = None
        self.y_mapping = None
        self.comment = None
        self._type_name = "KENNFELD"

    def __str__(self):
        value = f"{self._type_name} {self.name} {self.x_dimension} {self.y_dimension}\n"

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
        if self.unit_y:
            value += f'  EINHEIT_Y     "{self.unit_y}"\n'
        if self.unit_values:
            value += f'  EINHEIT_W     "{self.unit_values}"\n'
        if self.x_mapping:
            value += f'*SSTX   {self.x_mapping}\n'
        if self.y_mapping:
            value += f'*SSTY   {self.y_mapping}\n'
        stx_written = False
        for y_entry, map_values in self.values.items():
            x_entries = ""
            value_entries = ""
            for x_entry, value_entry in map_values.items():
                x_entries += f"{str(x_entry)} "
                value_entries += f"{str(value_entry)} "
            if not stx_written:
                value += f'  ST/X          {x_entries.strip()}\n'
                stx_written = True
            value += f'  ST/Y          {str(y_entry).strip()}\n'
            value += f'  WERT          {value_entries.strip()}\n'
        for var_name, var_value in self.variants.items():
            value += f"  VAR           {var_name}={var_value}\n"

        value += "END"

        return value

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
