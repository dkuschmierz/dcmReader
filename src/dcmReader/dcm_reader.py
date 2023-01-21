"""
DCMReader which handles data parsing.
"""
from __future__ import annotations

import os
import re
import logging

from collections import defaultdict
from typing import TYPE_CHECKING

from dcmReader.dcm_parameter import DcmParameter
from dcmReader.dcm_function import DcmFunction
from dcmReader.dcm_parameter_block import DcmParameterBlock
from dcmReader.dcm_characteristic_line import DcmCharacteristicLine
from dcmReader.dcm_fixed_characteristic_line import DcmFixedCharacteristicLine
from dcmReader.dcm_group_characteristic_line import DcmGroupCharacteristicLine
from dcmReader.dcm_characteristic_map import DcmCharacteristicMap
from dcmReader.dcm_fixed_characteristic_map import DcmFixedCharacteristicMap
from dcmReader.dcm_group_characteristic_map import DcmGroupCharacteristicMap
from dcmReader.dcm_distribution import DcmDistribution
from dcmReader.utils import _get_shape

if TYPE_CHECKING:
    from dcmReader.utils import ArrayLike

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

comment_qualifier = ("!", "*", ".")


class DcmReader:
    """Parser for the DCM (Data Conservation Format) format used by e.g. Vector, ETAS,..."""

    def __init__(self):
        self._file_header = ""
        self._file_header_finished = False
        self._functions_list = []
        self._parameter_list = []
        self._block_parameter_list = []
        self._characteristic_line_list = []
        self._fixed_characteristic_line_list = []
        self._group_characteristic_line_list = []
        self._characteristic_map_list = []
        self._fixed_characteristic_map_list = []
        self._group_characteristic_map_list = []
        self._distribution_list = []

        self.parser_methods = {
            "LANGNAME": {"key": "description", "method": self.parse_string},
            "DISPLAYNAME": {"key": "display_name", "method": self.parse_string},
            "FUNKTION": {"key": "function", "method": self.parse_string},
            "WERT": {"key": "", "method": self._parse_wert},
            "ST/X": {"key": "", "method": self._parse_coord_x},
            "ST/Y": {"key": "", "method": self._parse_coord_y},
            "EINHEIT_W": {"key": "units", "method": self.parse_string},
            "EINHEIT_X": {"key": "units_x", "method": self.parse_string},
            "EINHEIT_Y": {"key": "units_y", "method": self.parse_string},
            "VAR": {"key": "variants", "method": self.parse_string},
            "TEXT": {"key": "", "method": self._parse_text},
            # Data from comments:
            "SSTX": {"key": "x_mapping", "method": self.parse_string},
            "SSTY": {"key": "y_mapping", "method": self.parse_string},
        }
        self.parser_methods.update({k: {"key": "", "method": self._parse_comment} for k in comment_qualifier})

    def _parse_wert(self, line: str, *, coord_x, coord_y, values: defaultdict, **kwargs):
        # if not (coord_x or coord_y):
        #     raise ValueError(f"Values before stx/sty in {kwargs.get('name', 'Error')}")

        sty = coord_y[-1] if len(coord_y) > 0 else None
        values[sty].extend(self.parse_block_parameters(line))

    def _parse_text(self, line: str, *, coord_x, coord_y, values: defaultdict, **kwargs):
        sty = coord_y[-1] if len(coord_y) > 0 else None

        parameters = line.split(None, 1)[1]
        # parameters = " ".join(parameters.split()).split()
        parameters = [s.strip("\"'") for s in parameters.split()]
        values[sty].extend(parameters)

    def _parse_coord_x(self, line: str, *, coord_x: list, **kwargs) -> None:
        coord_x.extend(self.parse_block_parameters(line))

    def _parse_coord_y(self, line: str, *, coord_y: list, **kwargs) -> None:
        self._parse_coord_x(line, coord_x=coord_y)

    def _parse_comment(self, line: str, *, attrs: dict, **kwargs):
        # TODO: Should the comment remember which row? So it can be reprinted there?

        cq, line_no_cq = line[0], line[1:].strip()
        k = line_no_cq.split(None, 1)[0]

        p = self.parser_methods.get(k, None)
        if p is not None:
            # The comment has known keyword, parse it accordingly:
            parsed_values = p["method"](line_no_cq, attrs=attrs, **kwargs)

            # Optionally store in attrs, otherwise assume it's
            # stored within the method:
            if p["key"]:
                attrs[p["key"]] = parsed_values
        else:
            cmnt_prev = attrs.get("comment", "")
            attrs["comment"] = f"{cmnt_prev}{line_no_cq}{os.linesep}"

    def parse_variant(self, line, **kwargs):
        """Parses a variant field

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed variant either as float/int if variant is value
            or as str if variant is text field
        """
        variant = re.search(r"VAR\s+(.*?)=(.*)", line.strip())
        value = None
        try:
            value = self.convert_value(str(variant.group(2)).strip())
        except ValueError:
            value = str(variant.group(2)).strip('" ')
        return {str(variant.group(1)).strip(): value}

    @staticmethod
    def parse_string(line, **kwargs):
        """Parses a text field

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed text field
        """
        return line.split(None, 1)[1].strip(' "')
        # return line.split(" ", 1)[1].strip(' "')

    def parse_block_parameters(self, line, **kwargs):
        """Parses a block parameters line

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed block parameters as list
        """
        parameters = line.split(None, 1)[1]
        parameters = " ".join(parameters.split()).split()
        return [self.convert_value(i) for i in parameters]

    @staticmethod
    def convert_value(value):
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

    def parse_block_kennfeld(self, DcmThing, line_intro, dcm_file):
        block_type, name, *shape_rev = line_intro.split()
        # print(block_type, name)
        dcm_thing = DcmThing(name=name, block_type=block_type)

        # Reverse the order of x and y to match numpy:
        shape_rev.reverse()
        shape: tuple[int, ...] = tuple(int(v) for v in shape_rev if v != "@")
        coord_y, coord_x = [], []

        values: defaultdict[float, list] = defaultdict(list)
        while True:
            line = dcm_file.readline().strip()

            # Get the first keyword:
            keyword = line.split(None, 1)[0]

            if keyword.startswith("END"):

                if block_type == "STUETZSTELLENVERTEILUNG":
                    values[None] = coord_x
                    dcm_thing.attrs["x_mapping"] = dcm_thing.name

                # Handle coords and dims:
                xy = ("x", "y")
                k_axis = tuple(f"{v}_mapping" for v in xy)
                crds_rev = (coord_x, coord_y)
                dims_rev = []
                coords_rev = []
                for i, v in enumerate(reversed(shape)):
                    dims_rev.append(dcm_thing.attrs.get(k_axis[i], f"{dcm_thing.name}_{xy[i]}"))
                    if crds_rev[i]:
                        coords_rev.append(crds_rev[i])
                dcm_thing.dims = tuple(reversed(dims_rev))
                dcm_thing.coords = tuple(reversed(coords_rev))

                # Handle values:
                values_list = list(values.values())
                values_fin: ArrayLike
                if len(values_list) == 1 and len(shape) == 0:
                    # constant single float
                    # squeeze out the wrapping list:
                    values_fin = values_list[0][0]
                elif len(values) > 0 and len(shape) == 1:
                    # Tables:
                    values_fin = values_list[0]
                elif len(values) > 0 and len(shape) > 1:
                    # Maps:
                    values_fin = values_list
                else:
                    # Error?
                    values_fin = None
                dcm_thing.values = values_fin

                # Check if the parsing went ok:
                value_shape = _get_shape(dcm_thing.values)
                if value_shape != shape:
                    logger.error(
                        f"The parsed shape, {value_shape}, does not match the "
                        f"expected shape, {shape}, from the '{block_type} {name}'-block"
                    )

                break

            else:
                # Get parser settings for this keyword:
                p = self.parser_methods.get(keyword, None)

                if p is None:
                    # Is it a comment?
                    p = self.parser_methods.get(keyword[0], None)

                if p is not None:
                    # Parse the line:
                    parsed_values = p["method"](
                        line,
                        # Used in functions:
                        coord_x=coord_x,
                        coord_y=coord_y,
                        values=values,
                        attrs=dcm_thing.attrs,
                        # Error handling:
                        name=dcm_thing.name,
                    )

                    # Optionally store in attrs, otherwise assume it's
                    # stored within the method:
                    if p["key"]:
                        dcm_thing.attrs[p["key"]] = parsed_values
                else:
                    logger.warning(f"JW: Unknown parameter field: {line=}{keyword=}")

        return dcm_thing

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
        _dcm_format = None

        with open(file, "r", encoding="utf-8") as dcm_file:
            for line in dcm_file:
                # Remove whitespaces
                line = line.strip()

                # Check if line is comment
                if line.startswith(comment_qualifier):
                    if not self._file_header_finished:
                        self._file_header = self._file_header + line[1:].strip() + os.linesep
                    continue

                # At this point first comment block passed
                self._file_header_finished = True

                # Check if empty line
                if line == "":
                    continue

                # Check if format version line
                if _dcm_format is None:
                    if line.startswith("KONSERVIERUNG_FORMAT"):
                        _dcm_format = float(re.search(r"(\d\.\d)", line.strip()).group(1))
                        continue

                    logging.info("Found line: %s", line)
                    raise Exception("Incorrect file structure. DCM file format has to be first entry!")

                # Check if functions start
                if line.startswith("FUNKTIONEN"):
                    while True:
                        line = dcm_file.readline()
                        if line.startswith("END"):
                            break
                        function_match = re.search(r"FKT (.*?)(?: \"(.*?)?\"(?: \"(.*?)?\")?)?$", line.strip())
                        self._functions_list.append(
                            DcmFunction(
                                function_match.group(1),
                                function_match.group(2),
                                function_match.group(3),
                            )
                        )

                # Check if parameter starts
                elif line.startswith("FESTWERT "):
                    self._parameter_list.append(self.parse_block_kennfeld(DcmParameter, line, dcm_file))

                    # name = self.parse_string(line)
                    # found_parameter = DcmParameter(name)
                    # while True:
                    #     line = dcm_file.readline().strip()

                    #     if line.startswith("END"):
                    #         break

                    #     if line.startswith("LANGNAME"):
                    #         found_parameter.description = self.parse_string(line)
                    #     elif line.startswith("DISPLAYNAME"):
                    #         found_parameter.display_name = self.parse_string(line)
                    #     elif line.startswith("FUNKTION"):
                    #         found_parameter.function = self.parse_string(line)
                    #     elif line.startswith("WERT"):
                    #         found_parameter.value = self.convert_value(line.split(" ", 1)[1].strip())
                    #     elif line.startswith("EINHEIT_W"):
                    #         found_parameter.unit = self.parse_string(line)
                    #     elif line.startswith("VAR"):
                    #         found_parameter.variants.update(self.parse_variant(line))
                    #     elif line.startswith("TEXT"):
                    #         found_parameter.text = self.parse_string(line)
                    #     elif line.startswith(comment_qualifier):
                    #         if found_parameter.comment is None:
                    #             found_parameter.comment = line[1:].strip() + os.linesep
                    #         else:
                    #             found_parameter.comment += line[1:].strip() + os.linesep
                    #     else:
                    #         logger.warning("Unknown parameter field: %s", line)

                    # self._parameter_list.append(found_parameter)

                # Check if parameter block start
                elif line.startswith("FESTWERTEBLOCK"):
                    self._block_parameter_list.append(self.parse_block_kennfeld(DcmParameter, line, dcm_file))

                    # block_data = re.search(r"FESTWERTEBLOCK\s+(.*?)\s+(\d+)(?:\s+\@\s+(\d+))?", line.strip())
                    # found_block_parameter = DcmParameterBlock(block_data.group(1))
                    # found_block_parameter.x_dimension = self.convert_value(block_data.group(2))
                    # found_block_parameter.y_dimension = (
                    #     self.convert_value(block_data.group(3)) if block_data.group(3) is not None else 1
                    # )
                    # while True:
                    #     line = dcm_file.readline().strip()
                    #     if line.startswith("END"):
                    #         if len(found_block_parameter.values) != found_block_parameter.y_dimension:
                    #             logger.error("Y dimension in %s do not match description!", found_block_parameter.name)
                    #         break

                    #     if line.startswith("LANGNAME"):
                    #         found_block_parameter.description = self.parse_string(line)
                    #     elif line.startswith("DISPLAYNAME"):
                    #         found_block_parameter.display_name = self.parse_string(line)
                    #     elif line.startswith("FUNKTION"):
                    #         found_block_parameter.function = self.parse_string(line)
                    #     elif line.startswith("WERT"):
                    #         parameters = self.parse_block_parameters(line)
                    #         if len(parameters) != found_block_parameter.x_dimension:
                    #             logger.error("X dimension in %s do not match description!", found_block_parameter.name)
                    #         found_block_parameter.values.append(parameters)
                    #     elif line.startswith("EINHEIT_W"):
                    #         found_block_parameter.unit = self.parse_string(line)
                    #     elif line.startswith("VAR"):
                    #         found_block_parameter.variants.update(self.parse_variant(line))
                    #     elif line.startswith(comment_qualifier):
                    #         if found_block_parameter.comment is None:
                    #             found_block_parameter.comment = line[1:].strip() + os.linesep
                    #         else:
                    #             found_block_parameter.comment += line[1:].strip() + os.linesep
                    #     else:
                    #         logger.warning("Unknown parameter field: %s", line)

                    # self._block_parameter_list.append(found_block_parameter)

                # Check if characteristic line
                elif line.startswith("KENNLINIE"):
                    re_match = re.search(r"KENNLINIE\s+(.*?)\s+(\d+)", line.strip())
                    found_characteristic_line = DcmCharacteristicLine(re_match.group(1))
                    found_characteristic_line.x_dimension = self.convert_value(re_match.group(2))
                    parameters = []
                    stx = []

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(stx) != found_characteristic_line.x_dimension:
                                logger.error(
                                    "X dimension in %s \
                                    do not match description!",
                                    found_characteristic_line.name,
                                )
                            if len(parameters) != found_characteristic_line.x_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        do not match description!",
                                    found_characteristic_line.name,
                                )
                            found_characteristic_line.values = dict(zip(stx, parameters))
                            break
                        if line.startswith("LANGNAME"):
                            found_characteristic_line.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_characteristic_line.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_characteristic_line.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parse_block_parameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parse_block_parameters(line))
                        elif line.startswith("EINHEIT_W"):
                            found_characteristic_line.unit_values = self.parse_string(line)
                        elif line.startswith("EINHEIT_X"):
                            found_characteristic_line.unit_x = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_characteristic_line.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            re_match = re.search(r"SSTX\s+(.*)", line)
                            if re_match:
                                found_characteristic_line.x_mapping = re_match.group(1)
                            else:
                                if found_characteristic_line.comment is None:
                                    found_characteristic_line.comment = line[1:].strip() + os.linesep
                                else:
                                    found_characteristic_line.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._characteristic_line_list.append(found_characteristic_line)

                # Check if fixed characteristic line
                elif line.startswith("FESTKENNLINIE"):
                    re_match = re.search(r"FESTKENNLINIE\s+(.*?)\s+(\d+)", line.strip())
                    found_fixed_characteristic_line = DcmFixedCharacteristicLine(re_match.group(1))
                    found_fixed_characteristic_line.x_dimension = self.convert_value(re_match.group(2))
                    parameters = []
                    stx = []

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(stx) != found_fixed_characteristic_line.x_dimension:
                                logger.error(
                                    "X dimension in %s do not match description!", found_fixed_characteristic_line.name
                                )
                            if len(parameters) != found_fixed_characteristic_line.x_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        do not match description!",
                                    found_fixed_characteristic_line.name,
                                )
                            found_fixed_characteristic_line.values = dict(zip(stx, parameters))
                            break

                        if line.startswith("LANGNAME"):
                            found_fixed_characteristic_line.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_fixed_characteristic_line.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_fixed_characteristic_line.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parse_block_parameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parse_block_parameters(line))
                        elif line.startswith("EINHEIT_W"):
                            found_fixed_characteristic_line.unit_values = self.parse_string(line)
                        elif line.startswith("EINHEIT_X"):
                            found_fixed_characteristic_line.unit_x = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_fixed_characteristic_line.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            re_match = re.search(r"SSTX\s+(.*)", line)
                            if re_match:
                                found_fixed_characteristic_line.x_mapping = re_match.group(1)
                            else:
                                if found_fixed_characteristic_line.comment is None:
                                    found_fixed_characteristic_line.comment = line[1:].strip() + os.linesep
                                else:
                                    found_fixed_characteristic_line.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._fixed_characteristic_line_list.append(found_fixed_characteristic_line)

                # Check if group characteristic line
                elif line.startswith("GRUPPENKENNLINIE"):
                    re_match = re.search(r"GRUPPENKENNLINIE\s+(.*?)\s+(\d+)", line.strip())
                    found_group_characteristic_line = DcmGroupCharacteristicLine(re_match.group(1))
                    found_group_characteristic_line.x_dimension = self.convert_value(re_match.group(2))
                    parameters = []
                    stx = []

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(parameters) != found_group_characteristic_line.x_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        do not match description!",
                                    found_group_characteristic_line.name,
                                )
                            if len(stx) != found_group_characteristic_line.x_dimension:
                                logger.error(
                                    "X dimension in %s \
                                        do not match description!",
                                    found_group_characteristic_line.name,
                                )
                            found_group_characteristic_line.values = dict(zip(stx, parameters))
                            break

                        if line.startswith("LANGNAME"):
                            found_group_characteristic_line.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_group_characteristic_line.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_group_characteristic_line.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parse_block_parameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parse_block_parameters(line))
                        elif line.startswith("EINHEIT_W"):
                            found_group_characteristic_line.unit_values = self.parse_string(line)
                        elif line.startswith("EINHEIT_X"):
                            found_group_characteristic_line.unit_x = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_group_characteristic_line.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            re_match = re.search(r"SSTX\s+(.*)", line)
                            if re_match:
                                found_group_characteristic_line.x_mapping = re_match.group(1)
                            else:
                                if found_group_characteristic_line.comment is None:
                                    found_group_characteristic_line.comment = line[1:].strip() + os.linesep
                                else:
                                    found_group_characteristic_line.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._group_characteristic_line_list.append(found_group_characteristic_line)

                # Check for characteristic map
                elif line.startswith("KENNFELD "):
                    self._characteristic_map_list.append(
                        self.parse_block_kennfeld(DcmCharacteristicMap, line, dcm_file)
                    )

                # Check for fixed characteristic map
                elif line.startswith("FESTKENNFELD "):
                    self._fixed_characteristic_map_list.append(
                        self.parse_block_kennfeld(DcmFixedCharacteristicMap, line, dcm_file)
                    )

                # Check for group characteristic map
                elif line.startswith("GRUPPENKENNFELD "):
                    self._group_characteristic_map_list.append(
                        self.parse_block_kennfeld(DcmGroupCharacteristicMap, line, dcm_file)
                    )

                # Check if distribution
                elif line.startswith("STUETZSTELLENVERTEILUNG"):
                    self._distribution_list.append(self.parse_block_kennfeld(DcmDistribution, line, dcm_file))

                    # re_match = re.search(r"STUETZSTELLENVERTEILUNG\s+(.*?)\s+(\d+)", line.strip())
                    # found_distribution = DcmDistribution(re_match.group(1))
                    # found_distribution.x_dimension = self.convert_value(re_match.group(2))
                    # parameters = None
                    # stx = None

                    # while True:
                    #     line = dcm_file.readline().strip()
                    #     if line.startswith("END"):
                    #         if len(found_distribution.values) != found_distribution.x_dimension:
                    #             logger.error("X dimension in %s do not match description!", found_distribution.name)
                    #         break

                    #     if line.startswith("LANGNAME"):
                    #         found_distribution.description = self.parse_string(line)
                    #     elif line.startswith("DISPLAYNAME"):
                    #         found_distribution.display_name = self.parse_string(line)
                    #     elif line.startswith("FUNKTION"):
                    #         found_distribution.function = self.parse_string(line)
                    #     elif line.startswith("ST/X"):
                    #         found_distribution.values.extend(self.parse_block_parameters(line))
                    #     elif line.startswith("EINHEIT_X"):
                    #         found_distribution.unit_x = self.parse_string(line)
                    #     elif line.startswith("VAR"):
                    #         found_distribution.variants.update(self.parse_variant(line))
                    #     elif line.startswith(comment_qualifier):
                    #         if found_distribution.comment is None:
                    #             found_distribution.comment = line[1:].strip() + os.linesep
                    #         else:
                    #             found_distribution.comment += line[1:].strip() + os.linesep
                    #     else:
                    #         logger.warning("Unknown parameter field: %s", line)

                    # self._distribution_list.append(found_distribution)

                # Unknown start of line
                else:
                    logger.warning("Unknown line detected\n%s", line)

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
        for line in self._file_header.splitlines(True):
            output_string += f"* {line}"

        # Print the file version
        output_string += "\nKONSERVIERUNG_FORMAT 2.0\n"

        # Print the functions list
        output_string += "\nFUNKTIONEN\n"
        for function in sorted(self._functions_list):
            output_string += f"  {function}\n"
        output_string += "END\n\n"

        # Print rest of DCM objects
        object_list = []
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
