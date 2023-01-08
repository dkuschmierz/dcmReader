"""
Definition of DCM fixed characteristic line
"""

from dataclasses import dataclass
from dcmReader.dcm_characteristic_line import DcmCharacteristicLine


@dataclass
class DcmFixedCharacteristicLine(DcmCharacteristicLine):
    """Definition of a fixed characteristic line, derived from characteristic line"""

    def __init__(self, name) -> None:
        super().__init__(name)
        self._type_name = "FESTKENNLINIE"

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
