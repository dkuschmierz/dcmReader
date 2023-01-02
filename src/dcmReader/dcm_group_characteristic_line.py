"""
Definition of DCM group characteristic line
"""
from dataclasses import dataclass
from dcmReader.dcm_characteristic_line import DcmCharacteristicLine


@dataclass
class DcmGroupCharacteristicLine(DcmCharacteristicLine):
    """Definition of a group characteristic line, derived from characteristic line"""

    def __init__(self, name) -> None:
        super().__init__(name)
        self._type_name = "GRUPPENKENNLINIE"

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
