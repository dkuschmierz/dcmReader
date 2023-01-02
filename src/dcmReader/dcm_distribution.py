"""
Definition of DCM distribution
"""
from dataclasses import dataclass


@dataclass
class DcmDistribution:
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

    def __init__(self, name) -> None:
        self.name = name
        self.values = []
        self.description = None
        self.display_name = None
        self.variants = {}
        self.function = None
        self.unit_x = None
        self.x_dimension = 0
        self.comment = None

    def __str__(self):
        value = f"STUETZSTELLENVERTEILUNG {self.name} {str(self.x_dimension)}\n"

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
        if self.values:
            x_entries = ""
            for x_entry in self.values:
                x_entries += f"{str(x_entry)} "
            value += f'  ST/X          {x_entries.strip()}\n'
        for var_name, var_value in self.variants.items():
            value += f"  VAR           {var_name}={var_value}\n"

        value += "END"

        return value

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
