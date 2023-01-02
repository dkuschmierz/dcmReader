"""Definition of DCM parameter"""
from dataclasses import dataclass


@dataclass
class DcmParameter:
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

    def __init__(self, name):
        self.name = name
        self.value = None
        self.description = None
        self.display_name = None
        self.variants = {}
        self.function = None
        self.unit = None
        self.text = None
        self.comment = None

    def __str__(self):
        value = f"FESTWERT {self.name}\n"

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
        if self.value:
            value += f"  WERT          {self.value}\n"
        if self.text:
            value += f'  TEXT          "{self.text}"\n'

        for var_name, var_value in self.variants.items():
            if self.value:
                value += f"  VAR           {var_name}={var_value}\n"
            else:
                value += f'  VAR           {var_name}="{var_value}"\n'
        value += "END"

        return value

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
