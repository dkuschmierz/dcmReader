"""
Definition of DCM fixed characteristic map
"""
from __future__ import annotations

from dataclasses import dataclass
from dcmReader.dcm_characteristic_map import DcmCharacteristicMap


@dataclass
class DcmGroupCharacteristicMap(DcmCharacteristicMap):
    """Definition of a group characteristic map, derived from characteristic map"""

    def __init__(
        self,
        name: str,
        values: list[list[float]] | None = None,
        coords: tuple[list[float], ...] = None,
        attrs: dict | None = None,
        *,
        block_type: str = "GRUPPENKENNFELD",
    ) -> None:
        if attrs is None:
            attrs = {
                "description": "",
                "display_name": "",
                "variants": {},
                "function": "",
                "units_x": "",
                "units_y": "",
                "units": "",
            }

        super().__init__(
            name=name,
            values=values,
            coords=coords,
            attrs=attrs,
            block_type=block_type,
        )
