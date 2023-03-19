"""
DCMReader which handles data parsing.
"""
from __future__ import annotations

import os
import re
import logging

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar, Any, Generic, Protocol

import numpy as np

from dcmReader.elements import (
    DcmFunction,
    # DcmVariantCoding,
    # DcmModuleHeader,
    DcmParameter,
    DcmParameterBlock,
    DcmCharacteristicLine,
    DcmFixedCharacteristicLine,
    DcmGroupCharacteristicLine,
    DcmCharacteristicMap,
    DcmFixedCharacteristicMap,
    DcmGroupCharacteristicMap,
    DcmDistribution,
)
from dcmReader.utils import _COMMENT_QUALIFIER, _SETTINGS

if TYPE_CHECKING:
    from io import TextIOWrapper

    from dcmReader.utils import _DcmBase

    T_Element = TypeVar("T_Element", bound=_DcmBase)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class DcmReader:
    """Parser for the DCM (Data Conservation Format) format used by e.g. Vector, ETAS,..."""

    _functions_list: list[DcmFunction] = field(repr=False, default_factory=list)
    _parameter_list: list[DcmParameter] = field(repr=False, default_factory=list)
    _block_parameter_list: list[DcmParameterBlock] = field(repr=False, default_factory=list)
    _characteristic_line_list: list[DcmCharacteristicLine] = field(repr=False, default_factory=list)
    _fixed_characteristic_line_list: list[DcmFixedCharacteristicLine] = field(repr=False, default_factory=list)
    _group_characteristic_line_list: list[DcmGroupCharacteristicLine] = field(repr=False, default_factory=list)
    _characteristic_map_list: list[DcmCharacteristicMap] = field(repr=False, default_factory=list)
    _fixed_characteristic_map_list: list[DcmFixedCharacteristicMap] = field(repr=False, default_factory=list)
    _group_characteristic_map_list: list[DcmGroupCharacteristicMap] = field(repr=False, default_factory=list)
    _distribution_list: list[DcmDistribution] = field(repr=False, default_factory=list)
    _data: dict[str, _DcmBase] = field(repr=False, default_factory=dict)
    attrs: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.parser_methods = _SETTINGS

    def _parse_wert(self, line: str, *, element: T_Element, **kwargs) -> None:
        element.values = np.concatenate([element.values, self._parse_block_parameters(line)])

    def _parse_text(self, line: str, *, element: T_Element, **kwargs) -> None:
        parameters = line.split(None, 1)[1]
        parameters_list = [s.strip("\"'") for s in parameters.split()]
        element.values = np.concatenate([element.values, parameters_list])

    def _parse_coord_x(self, line: str, *, coord_x: list[float], **kwargs) -> None:
        coord_x.extend(self._parse_block_parameters(line))

    def _parse_coord_y(self, line: str, *, coord_y: list[float], **kwargs) -> None:
        self._parse_coord_x(line, coord_x=coord_y)

    def _parse_comment(self, line: str, *, element: T_Element, **kwargs) -> None:
        # TODO: Should the comment remember which row? So it can be reprinted there?

        line_no_cq = line[1:].strip()
        k = line_no_cq.split(None, 1)[0]

        p = self.parser_methods.get(k, None)
        if p is not None:
            # The comment has a known keyword, parse it accordingly:
            parsed_values = p["parse_method"](self)(line_no_cq, attrs=element.attrs, **kwargs)

            # Optionally store in attrs, otherwise assume it's
            # stored within the method:
            if p["parse_key"]:
                element.attrs[p["parse_key"]] = parsed_values
        else:
            cmnt_prev = element.attrs.get("comment", "")
            cmnts = [cmnt_prev, line_no_cq] if cmnt_prev else [line_no_cq]
            element.attrs["comment"] = "\n".join(cmnts)

    def _parse_string(self, line: str, **kwargs) -> str:
        """Parses a text field

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed text field
        """
        return line.split(None, 1)[1].strip(' "')

    def _parse_variant(self, line: str, **kwargs) -> dict:
        """Parses a variant field
        Args:
            line (str): One line of the DCM file
        Returns:
            Parsed variant either as float/int if variant is value
            or as str if variant is text field
        """
        variant = re.search(r"VAR\s+(.*?)=(.*)", line.strip())
        if variant is None:
            return {}

        key = str(variant.group(1)).strip()
        value_str = str(variant.group(2)).strip()
        value: str | float | None = None
        try:
            # Check if it's number
            value = self._convert_value(value_str)
        except ValueError:
            value = value_str.strip('" ')

        return {key: value}

    def _parse_block_parameters(self, line: str, **kwargs) -> list:
        """Parses a block parameters line

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed block parameters as list
        """
        parameters = line.split(None, 1)[1]
        parameters_list = " ".join(parameters.split()).split()
        return [self._convert_value(i) for i in parameters_list]

    def _convert_value(self, value: str) -> float:
        """Converts a text value to the correct number

        Args:
            value (str): String to convert

        Returns:
            Value as int or float
        """
        try:
            float_value = float(value)
            # Check if . is in value, so even if float could
            # be integer return as float
            if float_value.is_integer() and "." not in value:
                return int(float_value)

            return float_value

        except ValueError as err:
            raise ValueError(f"Cannot convert {value} from string to number.") from err

    def _parse_elements(self, DcmElement: type[T_Element], line_intro: str, dcm_file: TextIOWrapper) -> T_Element:
        element_syntax, name, *shape_rev = line_intro.split()
        element = DcmElement(name=name, element_syntax=element_syntax)

        # Reverse the order of x and y to match numpy:
        shape_rev.reverse()
        shape: tuple[int, ...] = tuple(int(v) for v in shape_rev if v != "@")
        coord_y: list[float] = []
        coord_x: list[float] = []

        while True:
            line = dcm_file.readline().strip()

            # Get the first keyword:
            keyword = line.split(None, 1)[0]

            if keyword.startswith("END"):
                if element_syntax == "STUETZSTELLENVERTEILUNG":
                    element.values = np.asarray(coord_x)
                    element.attrs[_SETTINGS["SSTX"]["key_eng"]] = element.name

                # Handle coords and dims:
                xy = ("x", "y")
                k_axis = tuple(_SETTINGS[f"SST{v.upper()}"]["key_eng"] for v in xy)
                crds_rev = (coord_x, coord_y)
                dims_rev = []
                coords_rev = []
                for i, v in enumerate(reversed(shape)):
                    dims_rev.append(element.attrs.get(k_axis[i], f"{element.name}_{xy[i]}"))
                    if crds_rev[i]:
                        coords_rev.append(crds_rev[i])
                element.dims = tuple(reversed(dims_rev))
                element.coords = tuple(np.array(v) for v in reversed(coords_rev))

                element.values = element.values.reshape(shape)

                break

            else:
                # Get parser settings for this keyword:
                p = self.parser_methods.get(keyword, None)

                if p is None:
                    # Is it a comment?
                    p = self.parser_methods.get(keyword[0], None)

                if p is not None:
                    # Parse the line:
                    parsed_values = p["parse_method"](self)(line, coord_x=coord_x, coord_y=coord_y, element=element)

                    # Optionally store in attrs, otherwise assume it's
                    # stored within the method:
                    if p["parse_key"]:
                        element.attrs[p["parse_key"]] = parsed_values
                else:
                    logger.warning(f"Unknown parameter field: {line=}{keyword=}")

        return element

    def _parse_elements_funktionen(
        self, DcmElement: type[T_Element], line_intro: str, dcm_file: TextIOWrapper
    ) -> list[T_Element]:
        # element_syntax = line_intro.strip()

        elements = []
        while True:
            line = dcm_file.readline().strip()

            # Get the first keyword:
            keyword = line.split(None, 1)[0]

            if keyword.startswith("END"):
                break
            else:
                function_match = re.search(r"FKT (.*?)(?: \"(.*?)?\"(?: \"(.*?)?\")?)?$", line.strip())
                element_syntax_short = "FKT"

                fm: dict[str, str] = {"name": "", "version": "", "description": ""}
                for i, (k, v) in enumerate(fm.items()):
                    if function_match is not None:
                        fm[k] = function_match.group(i + 1)

                element = DcmElement(name=fm["name"], element_syntax=element_syntax_short)
                element.attrs["version"] = fm["version"]
                element.attrs["description"] = fm["description"]
                element.attrs["_function"] = "FUNKTIONEN"

                # Add an empty array because you cannot init with
                # np.array([]).shape=(0,) and not the correct (), np.concatenate doesn't
                # work with shape=() though so can't use that as init either:
                element.values = np.empty((), dtype=object)

                elements.append(element)

        return elements

    def write(self, file) -> None:
        """Writes the current DCM object to a dcm file

        Args:
            file(str): DCM file to write
        """
        if not file.endswith(".dcm"):
            file += ".dcm"

        with open(file, "w", encoding="utf-8") as dcm_file:
            dcm_file.writelines(str(self))

    def read(self, file) -> None:
        """Reads and processes the given file.

        Args:
            file(str): DCM file to parse
        """
        file_header_finished = False
        self.attrs["filename"] = file
        with open(file, "r", encoding="utf-8") as dcm_file:
            for line in dcm_file:
                # Remove whitespaces
                line = line.strip()

                # Check if line is comment
                if line.startswith(_COMMENT_QUALIFIER):
                    if not file_header_finished:
                        self.attrs["file_header"] = f"{self.attrs.get('file_header', '')}{line[1:].strip()}\n"
                    continue

                # At this point first comment block passed
                file_header_finished = True

                # Check if empty line
                if line == "":
                    continue

                # Check if format version line
                if self.attrs.get("dcm_format", None) is None:
                    kf, kf_value = line.split()
                    if kf == "KONSERVIERUNG_FORMAT":
                        self.attrs["dcm_format"] = float(kf_value)
                        continue

                    logging.info("Found line: %s", line)
                    raise Exception("Incorrect file structure. DCM file format has to be first entry!")

                # Check if functions start
                if line.startswith("FUNKTIONEN"):
                    self._functions_list.extend(self._parse_elements_funktionen(DcmFunction, line, dcm_file))

                # Check if parameter starts
                elif line.startswith("FESTWERT "):
                    self._parameter_list.append(self._parse_elements(DcmParameter, line, dcm_file))

                # Check if parameter block start
                elif line.startswith("FESTWERTEBLOCK"):
                    self._block_parameter_list.append(self._parse_elements(DcmParameterBlock, line, dcm_file))

                # Check if characteristic line
                elif line.startswith("KENNLINIE"):
                    self._characteristic_line_list.append(self._parse_elements(DcmCharacteristicLine, line, dcm_file))

                # Check if fixed characteristic line
                elif line.startswith("FESTKENNLINIE"):
                    self._fixed_characteristic_line_list.append(
                        self._parse_elements(DcmFixedCharacteristicLine, line, dcm_file)
                    )

                # Check if group characteristic line
                elif line.startswith("GRUPPENKENNLINIE"):
                    self._group_characteristic_line_list.append(
                        self._parse_elements(DcmGroupCharacteristicLine, line, dcm_file)
                    )

                # Check for characteristic map
                elif line.startswith("KENNFELD "):
                    self._characteristic_map_list.append(self._parse_elements(DcmCharacteristicMap, line, dcm_file))

                # Check for fixed characteristic map
                elif line.startswith("FESTKENNFELD "):
                    self._fixed_characteristic_map_list.append(
                        self._parse_elements(DcmFixedCharacteristicMap, line, dcm_file)
                    )

                # Check for group characteristic map
                elif line.startswith("GRUPPENKENNFELD "):
                    self._group_characteristic_map_list.append(
                        self._parse_elements(DcmGroupCharacteristicMap, line, dcm_file)
                    )

                # Check if distribution
                elif line.startswith("STUETZSTELLENVERTEILUNG"):
                    self._distribution_list.append(self._parse_elements(DcmDistribution, line, dcm_file))

                # Unknown start of line
                else:
                    logger.warning("Unknown line detected\n%s", line)

        _all = (
            self._parameter_list
            + self._block_parameter_list
            + self._characteristic_line_list
            + self._fixed_characteristic_line_list
            + self._group_characteristic_line_list
            + self._characteristic_map_list
            + self._fixed_characteristic_map_list
            + self._group_characteristic_map_list
            + self._distribution_list
        )
        for v in _all:
            if self._data.get(v.name) is not None:
                raise NotImplementedError("Duplicated names not supported?")
            self._data[v.name] = v

    def get_functions(self) -> list:
        """Returns all found functions as a list"""
        return self._functions_list

    def get_parameters(self) -> list:
        """Returns all found parameters as a list"""
        return self._parameter_list

    def get_block_parameters(self) -> list:
        """Returns all found block parameters as a list"""
        return self._block_parameter_list

    def get_characteristic_lines(self) -> list:
        """Returns all found characteristic lines as a list"""
        return self._characteristic_line_list

    def get_fixed_characteristic_lines(self) -> list:
        """Returns all found fixed characteristic lines as a list"""
        return self._fixed_characteristic_line_list

    def get_group_characteristic_lines(self) -> list:
        """Returns all found group characteristic lines as a list"""
        return self._group_characteristic_line_list

    def get_characteristic_maps(self) -> list:
        """Returns all found characteristic maps as a list"""
        return self._characteristic_map_list

    def get_fixed_characteristic_maps(self) -> list:
        """Returns all found fixed characteristic maps as a list"""
        return self._fixed_characteristic_map_list

    def get_group_characteristic_maps(self) -> list:
        """Returns all found group characteristic maps as a list"""
        return self._group_characteristic_map_list

    def get_distributions(self) -> list:
        """Returns all found distributions as a list"""
        return self._distribution_list

    def __str__(self) -> str:
        output_string = ""
        # Print the file header
        for line in self.attrs.get("file_header", "").splitlines(True):
            output_string += f"* {line}"

        # Print the file version
        output_string += "\nKONSERVIERUNG_FORMAT 2.0\n"

        # Print the functions list
        output_string += "\nFUNKTIONEN\n"
        for function in sorted(self._functions_list):
            output_string += f"  {function}\n"
        output_string += "END\n\n"

        # Print rest of DCM objects
        object_list: list[_DcmBase] = []
        object_list.extend(self._parameter_list)
        object_list.extend(self._block_parameter_list)
        object_list.extend(self._characteristic_line_list)
        object_list.extend(self._fixed_characteristic_line_list)
        object_list.extend(self._group_characteristic_line_list)
        object_list.extend(self._characteristic_map_list)
        object_list.extend(self._fixed_characteristic_map_list)
        object_list.extend(self._group_characteristic_map_list)
        object_list.extend(self._distribution_list)

        for item in sorted(object_list):
            output_string += f"\n{item}\n"

        return output_string

    def __getitem__(self, key):
        return self._data[key]
