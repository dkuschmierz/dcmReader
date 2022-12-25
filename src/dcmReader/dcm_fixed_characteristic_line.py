"""
Definition of DCM fixed characteristic line
"""

from dcmReader.dcm_characteristic_line import DcmCharacteristicLine

class DcmFixedCharacteristicLine(DcmCharacteristicLine):
    """Definition of a fixed characteristic line, derived from characteristic line"""

    def __init__(self, name) -> None:
        super().__init__(name)

    def __str__(self):
        value = f"FESTKENNLINIE {self.name} {self.x_dimension}\n"

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
        if self.values:
            x_entries = ""
            value_entries = ""
            for x_entry,value_entry in self.values.items():
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
