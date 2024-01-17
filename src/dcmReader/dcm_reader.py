"""
DCMReader which handles data parsing.
"""

import os
import re
import logging

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

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

    def parse_variant(self, line):
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
    def parse_string(line):
        """Parses a text field

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed text field
        """
        return line.split(" ", 1)[1].strip(' "')

    def parse_block_parameters(self, line):
        """Parses a block parameters line

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed block parameters as list
        """
        parameters = line.split(" ", 1)[1]
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

    def write(self, file, file_encoding="utf-8") -> None:
        """Writes the current DCM object to a dcm file

        Args:
            file(str): DCM file to write
        """
        if not file.endswith(".dcm"):
            file += ".dcm"

        with open(file, "w", encoding=file_encoding) as dcm_file:
            dcm_file.writelines(str(self))

    def read(self, file, file_encoding="utf-8") -> None:
        """Reads and processes the given file.

        Args:
            file(str): DCM file to parse
        """
        _dcm_format = None

        comment_qualifier = ("!", "*", ".")

        with open(file, "r", encoding=file_encoding) as dcm_file:
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
                    name = self.parse_string(line)
                    found_parameter = DcmParameter(name)
                    while True:
                        line = dcm_file.readline().strip()

                        if line.startswith("END"):
                            break

                        if line.startswith("LANGNAME"):
                            found_parameter.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_parameter.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_parameter.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            found_parameter.value = self.convert_value(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            found_parameter.unit = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_parameter.variants.update(self.parse_variant(line))
                        elif line.startswith("TEXT"):
                            found_parameter.text = self.parse_string(line)
                        elif line.startswith(comment_qualifier):
                            if found_parameter.comment is None:
                                found_parameter.comment = line[1:].strip() + os.linesep
                            else:
                                found_parameter.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._parameter_list.append(found_parameter)

                # Check if parameter block start
                elif line.startswith("FESTWERTEBLOCK"):
                    block_data = re.search(r"FESTWERTEBLOCK\s+(.*?)\s+(\d+)(?:\s+\@\s+(\d+))?", line.strip())
                    found_block_parameter = DcmParameterBlock(block_data.group(1))
                    found_block_parameter.x_dimension = self.convert_value(block_data.group(2))
                    found_block_parameter.y_dimension = (
                        self.convert_value(block_data.group(3)) if block_data.group(3) is not None else 1
                    )
                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(found_block_parameter.values) != found_block_parameter.y_dimension:
                                logger.error("Y dimension in %s do not match description!", found_block_parameter.name)
                            break

                        if line.startswith("LANGNAME"):
                            found_block_parameter.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_block_parameter.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_block_parameter.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            parameters = self.parse_block_parameters(line)
                            if len(parameters) != found_block_parameter.x_dimension:
                                logger.error("X dimension in %s do not match description!", found_block_parameter.name)
                            found_block_parameter.values.append(parameters)
                        elif line.startswith("EINHEIT_W"):
                            found_block_parameter.unit = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_block_parameter.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            if found_block_parameter.comment is None:
                                found_block_parameter.comment = line[1:].strip() + os.linesep
                            else:
                                found_block_parameter.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._block_parameter_list.append(found_block_parameter)

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
                                logger.error("X dimension in %s \
                                    do not match description!", found_characteristic_line.name)
                            if len(parameters) != found_characteristic_line.x_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        do not match description!", found_characteristic_line.name
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
                                        do not match description!", found_fixed_characteristic_line.name
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
                                        do not match description!", found_group_characteristic_line.name
                                )
                            if len(stx) != found_group_characteristic_line.x_dimension:
                                logger.error(
                                    "X dimension in %s \
                                        do not match description!", found_group_characteristic_line.name
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
                    re_match = re.search(r"KENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line.strip())
                    found_characteristic_map = DcmCharacteristicMap(re_match.group(1))
                    found_characteristic_map.x_dimension = self.convert_value(re_match.group(2))
                    found_characteristic_map.y_dimension = self.convert_value(re_match.group(3))
                    stx = []
                    sty = None

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(found_characteristic_map.values) != found_characteristic_map.y_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        does not match description!", found_characteristic_map.name
                                )
                            if len(stx) != found_characteristic_map.x_dimension:
                                logger.error("X dimension in %s \
                                    do not match description!", found_characteristic_map.name)
                            for name, entry in found_characteristic_map.values.items():
                                if len(entry) != found_characteristic_map.x_dimension:
                                    logger.error(
                                        "Values dimension in %s \
                                            does not match description!", found_characteristic_map.name
                                    )
                                else:
                                    found_characteristic_map.values[name] = dict(zip(stx, entry))
                            break

                        if line.startswith("LANGNAME"):
                            found_characteristic_map.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_characteristic_map.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_characteristic_map.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(f"Values before stx/sty in {found_characteristic_map.name}")
                            parameters = self.parse_block_parameters(line)
                            if sty not in found_characteristic_map.values:
                                found_characteristic_map.values[sty] = []
                            found_characteristic_map.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parse_block_parameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convert_value(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            found_characteristic_map.unit_values = self.parse_string(line)
                        elif line.startswith("EINHEIT_X"):
                            found_characteristic_map.unit_x = self.parse_string(line)
                        elif line.startswith("EINHEIT_Y"):
                            found_characteristic_map.unit_y = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_characteristic_map.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            re_match_x = re.search(r"SSTX\s+(.*)", line)
                            re_match_y = re.search(r"SSTY\s+(.*)", line)
                            if re_match_x:
                                found_characteristic_map.x_mapping = re_match_x.group(1)
                            elif re_match_y:
                                found_characteristic_map.y_mapping = re_match_y.group(1)
                            else:
                                if found_characteristic_map.comment is None:
                                    found_characteristic_map.comment = line[1:].strip() + os.linesep
                                else:
                                    found_characteristic_map.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._characteristic_map_list.append(found_characteristic_map)

                # Check for fixed characteristic map
                elif line.startswith("FESTKENNFELD "):
                    re_match = re.search(r"FESTKENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line.strip())
                    found_fixed_characteristic_map = DcmFixedCharacteristicMap(re_match.group(1))
                    found_fixed_characteristic_map.x_dimension = self.convert_value(re_match.group(2))
                    found_fixed_characteristic_map.y_dimension = self.convert_value(re_match.group(3))
                    stx = []
                    sty = None

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(found_fixed_characteristic_map.values) != found_fixed_characteristic_map.y_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        does not match description!", found_fixed_characteristic_map.name
                                )
                            if len(stx) != found_fixed_characteristic_map.x_dimension:
                                logger.error(
                                    "X dimension in %s do not match description!", found_fixed_characteristic_map.name
                                )
                            for name, entry in found_fixed_characteristic_map.values.items():
                                if len(entry) != found_fixed_characteristic_map.x_dimension:
                                    logger.error(
                                        "Values dimension in %s \
                                            does not match description!", found_fixed_characteristic_map.name
                                    )
                                else:
                                    found_fixed_characteristic_map.values[name] = dict(zip(stx, entry))
                            break

                        if line.startswith("LANGNAME"):
                            found_fixed_characteristic_map.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_fixed_characteristic_map.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_fixed_characteristic_map.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(f"Values before stx/sty in {found_fixed_characteristic_map.name}")
                            parameters = self.parse_block_parameters(line)
                            if sty not in found_fixed_characteristic_map.values:
                                found_fixed_characteristic_map.values[sty] = []
                            found_fixed_characteristic_map.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parse_block_parameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convert_value(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            found_fixed_characteristic_map.unit_values = self.parse_string(line)
                        elif line.startswith("EINHEIT_X"):
                            found_fixed_characteristic_map.unit_x = self.parse_string(line)
                        elif line.startswith("EINHEIT_Y"):
                            found_fixed_characteristic_map.unit_y = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_fixed_characteristic_map.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            re_match_x = re.search(r"SSTX\s+(.*)", line)
                            re_match_y = re.search(r"SSTY\s+(.*)", line)
                            if re_match_x:
                                found_fixed_characteristic_map.x_mapping = re_match_x.group(1)
                            elif re_match_y:
                                found_fixed_characteristic_map.y_mapping = re_match_y.group(1)
                            else:
                                if found_fixed_characteristic_map.comment is None:
                                    found_fixed_characteristic_map.comment = line[1:].strip() + os.linesep
                                else:
                                    found_fixed_characteristic_map.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._fixed_characteristic_map_list.append(found_fixed_characteristic_map)

                # Check for group characteristic map
                elif line.startswith("GRUPPENKENNFELD "):
                    re_match = re.search(r"GRUPPENKENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line.strip())
                    found_group_characteristic_map = DcmGroupCharacteristicMap(re_match.group(1))
                    found_group_characteristic_map.x_dimension = self.convert_value(re_match.group(2))
                    found_group_characteristic_map.y_dimension = self.convert_value(re_match.group(3))
                    stx = []
                    sty = None

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(found_group_characteristic_map.values) != found_group_characteristic_map.y_dimension:
                                logger.error(
                                    "Values dimension in %s \
                                        does not match description!", found_group_characteristic_map.name
                                )
                            if len(stx) != found_group_characteristic_map.x_dimension:
                                logger.error(
                                    "X dimension in %s do not match description!", found_group_characteristic_map.name
                                )
                            for name, entry in found_group_characteristic_map.values.items():
                                if len(entry) != found_group_characteristic_map.x_dimension:
                                    logger.error(
                                        "Values dimension in %s \
                                            does not match description!", found_group_characteristic_map.name
                                    )
                                else:
                                    found_group_characteristic_map.values[name] = dict(zip(stx, entry))
                            break

                        if line.startswith("LANGNAME"):
                            found_group_characteristic_map.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_group_characteristic_map.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_group_characteristic_map.function = self.parse_string(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(f"Values before stx/sty in {found_group_characteristic_map.name}")
                            parameters = self.parse_block_parameters(line)
                            if sty not in found_group_characteristic_map.values:
                                found_group_characteristic_map.values[sty] = []
                            found_group_characteristic_map.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parse_block_parameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convert_value(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            found_group_characteristic_map.unit_values = self.parse_string(line)
                        elif line.startswith("EINHEIT_X"):
                            found_group_characteristic_map.unit_x = self.parse_string(line)
                        elif line.startswith("EINHEIT_Y"):
                            found_group_characteristic_map.unit_y = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_group_characteristic_map.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            re_match_x = re.search(r"SSTX\s+(.*)", line)
                            re_match_y = re.search(r"SSTY\s+(.*)", line)
                            if re_match_x:
                                found_group_characteristic_map.x_mapping = re_match_x.group(1)
                            elif re_match_y:
                                found_group_characteristic_map.y_mapping = re_match_y.group(1)
                            else:
                                if found_group_characteristic_map.comment is None:
                                    found_group_characteristic_map.comment = line[1:].strip() + os.linesep
                                else:
                                    found_group_characteristic_map.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._group_characteristic_map_list.append(found_group_characteristic_map)

                # Check if distribution
                elif line.startswith("STUETZSTELLENVERTEILUNG"):
                    re_match = re.search(r"STUETZSTELLENVERTEILUNG\s+(.*?)\s+(\d+)", line.strip())
                    found_distribution = DcmDistribution(re_match.group(1))
                    found_distribution.x_dimension = self.convert_value(re_match.group(2))
                    parameters = None
                    stx = None

                    while True:
                        line = dcm_file.readline().strip()
                        if line.startswith("END"):
                            if len(found_distribution.values) != found_distribution.x_dimension:
                                logger.error("X dimension in %s do not match description!", found_distribution.name)
                            break

                        if line.startswith("LANGNAME"):
                            found_distribution.description = self.parse_string(line)
                        elif line.startswith("DISPLAYNAME"):
                            found_distribution.display_name = self.parse_string(line)
                        elif line.startswith("FUNKTION"):
                            found_distribution.function = self.parse_string(line)
                        elif line.startswith("ST/X"):
                            found_distribution.values.extend(self.parse_block_parameters(line))
                        elif line.startswith("EINHEIT_X"):
                            found_distribution.unit_x = self.parse_string(line)
                        elif line.startswith("VAR"):
                            found_distribution.variants.update(self.parse_variant(line))
                        elif line.startswith(comment_qualifier):
                            if found_distribution.comment is None:
                                found_distribution.comment = line[1:].strip() + os.linesep
                            else:
                                found_distribution.comment += line[1:].strip() + os.linesep
                        else:
                            logger.warning("Unknown parameter field: %s", line)

                    self._distribution_list.append(found_distribution)

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
