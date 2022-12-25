"""
Definition of DCM fixed characteristic map
"""

from dcmReader.dcm_characteristic_map import DcmCharacteristicMap

class DcmGroupCharacteristicMap(DcmCharacteristicMap):
    """Definition of a group characteristic map, derived from characteristic map"""

    def __init__(self, name) -> None:
        super().__init__(name)

    def __str__(self):
        value = f"GRUPPENKENNFELD {self.name} {self.x_dimension} {self.y_dimension}\n"

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
        stx_written = False
        for y_entry, map_values in self.values.items():
            x_entries = ""
            value_entries = ""
            for x_entry,value_entry in map_values.items():
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
