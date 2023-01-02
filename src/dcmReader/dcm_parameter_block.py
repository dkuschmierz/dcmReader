"""
Definition of DCM parameter block
"""
from dataclasses import dataclass


@dataclass
class DcmParameterBlock:
    """Definition of a block parameter

    Attributes:
        name (str):         Name of the block parameter
        description (str):  Description of the block parameter, started by LANGNAME in DCM
        display_name (str): Block parameter name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the block parameter, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit (str):         Unit of the block parameters, started by EINHEIT_W in DCM
        values (list):      List of values of the block parameter, started by WERT in DCM
        x_dimension (int):  Dimension in x direction of the block parameter
        y_dimension (int):  Dimension in y direction of the block parameter
        comment (str):      Block comment
    """

    def __init__(self, name):
        self.name = name
        self.values = []
        self.description = None
        self.display_name = None
        self.variants = {}
        self.function = None
        self.unit = None
        self.x_dimension = 0
        self.y_dimension = 0
        self.comment = None

    def __str__(self):
        value = f"FESTWERTEBLOCK {self.name} {self.x_dimension}"
        if self.y_dimension > 1:
            value += f" @ {self.y_dimension}\n"
        else:
            value += "\n"

        if self.comment:
            for line in self.comment.splitlines(True):
                value += f"* {line}"
        if self.description:
            value += f'  LANGNAME      "{self.description}"\n'
        if self.function:
            value += f'  FUNKTION      "{self.function}"\n'
        if self.display_name:
            value += f"  DISPLAYNAME   {self.display_name}\n"
        if self.unit:
            value += f'  EINHEIT_W     "{self.unit}"\n'
        if self.values:
            for entry in self.values:
                value += f'  WERT          {" ".join([str(x) for x in entry])}\n'

        for var_name, var_value in self.variants.items():
            value += f"  VAR           {var_name}={var_value}\n"

        value += "END"

        return value

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
