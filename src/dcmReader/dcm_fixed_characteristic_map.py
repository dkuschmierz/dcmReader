"""
Definition of DCM fixed characteristic map
"""

from dcmReader.dcm_characteristic_map import DcmCharacteristicMap


class DcmFixedCharacteristicMap(DcmCharacteristicMap):
    """Definition of a fixed characteristic map, derived from characteristic map"""

    def __init__(self, name) -> None:
        super().__init__(name)
        self._type_name = "FESTKENNFELD"

    def __lt__(self, other):
        return self.function < other.function and self.description < other.description
