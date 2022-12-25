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
        self._fileHeader = ""
        self._fileHeaderFinished = False
        self._functionsList = []
        self._parameterList = []
        self._blockParameterList = []
        self._characteristicLineList = []
        self._fixedCharacteristicLineList = []
        self._groupCharacteristicLineList = []
        self._characteristicMapList = []
        self._fixedCharacteristicMapList = []
        self._groupCharacteristicMapList = []
        self._distributionList = []

    def parseVariant(self, line):
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
            value = self.convertValue(str(variant.group(2)).strip())
        except ValueError:
            value = str(variant.group(2)).strip('" ')
        return {str(variant.group(1)).strip(): value}

    def parseString(self, line):
        """Parses a text field

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed text field
        """
        return line.split(" ", 1)[1].strip(' "')

    def parseBlockParameters(self, line):
        """Parses a block parameters line

        Args:
            line (str): One line of the DCM file

        Returns:
            Parsed block parameters as list
        """
        parameters = line.split(" ", 1)[1]
        parameters = " ".join(parameters.split()).split()
        return [self.convertValue(i) for i in parameters]

    def convertValue(self, value):
        """Converts a text value to the correct number

        Args:
            value (str): String to convert

        Returns:
            Value as int or float
        """
        try:
            floatValue = float(value)
            # Check if . is in value, so even if float could
            # be integer return as float
            if floatValue.is_integer() and "." not in value:
                return int(floatValue)
            else:
                return floatValue
        except ValueError:
            raise ValueError(f"Cannot convert {value} from string to number.")

    def write(self, file) -> None:
        """Writes the current DCM object to a dcm file

        Args:
            file(str): DCM file to write
        """
        if not file.endswith(".dcm"):
            file += ".dcm"

        with open(file, "w") as f:
            f.writelines(str(self))

    def read(self, file) -> None:
        """Reads and processes the given file.

        Args:
            file(str): DCM file to parse
        """
        _dcmFormat = None

        with open(file, "r") as f:
            for line in f:
                # Remove whitespaces
                line = line.strip()

                # Check if line is comment
                if line.startswith(("!", "*", ".")):
                    if not self._fileHeaderFinished:
                        self._fileHeader = self._fileHeader + line[1:].strip() + os.linesep
                    continue

                # At this point first comment block passed
                self._fileHeaderFinished = True

                # Check if empty line
                if line == "":
                    continue

                # Check if format version line
                if _dcmFormat is None:
                    if line.startswith("KONSERVIERUNG_FORMAT"):
                        _dcmFormat = float(re.search(r"(\d\.\d)", line.strip()).group(1))
                        continue
                    else:
                        logging.info(f"Found line: {line}")
                        raise Exception("Incorrect file structure. DCM file format has to be first entry!")

                # Check if functions start
                if line.startswith("FUNKTIONEN"):
                    while True:
                        line = f.readline()
                        if line.startswith("END"):
                            break
                        functionMatch = re.search(r"FKT (.*?)(?: \"(.*?)?\"(?: \"(.*?)?\")?)?$", line.strip())
                        self._functionsList.append(
                            DcmFunction(
                                functionMatch.group(1),
                                functionMatch.group(2),
                                functionMatch.group(3),
                            )
                        )

                # Check if parameter starts
                elif line.startswith("FESTWERT "):
                    name = self.parseString(line)
                    foundParameter = DcmParameter(name)
                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            break
                        elif line.startswith("LANGNAME"):
                            foundParameter.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundParameter.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundParameter.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            foundParameter.value = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundParameter.unit = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundParameter.variants.update(self.parseVariant(line))
                        elif line.startswith("TEXT"):
                            foundParameter.text = self.parseString(line)
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._parameterList.append(foundParameter)

                # Check if parameter block start
                elif line.startswith("FESTWERTEBLOCK"):
                    blockData = re.search(r"FESTWERTEBLOCK\s+(.*?)\s+(\d+)(?:\s+\@\s+(\d+))?", line.strip())
                    foundBlockParameter = DcmParameterBlock(blockData.group(1))
                    foundBlockParameter.x_dimension = self.convertValue(blockData.group(2))
                    foundBlockParameter.y_dimension = (
                        self.convertValue(blockData.group(3)) if blockData.group(3) is not None else 1
                    )
                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(foundBlockParameter.values) != foundBlockParameter.y_dimension:
                                logger.error(f"Y dimension in {foundBlockParameter.name} do not match description!")
                            break
                        elif line.startswith("LANGNAME"):
                            foundBlockParameter.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundBlockParameter.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundBlockParameter.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            parameters = self.parseBlockParameters(line)
                            if len(parameters) != foundBlockParameter.x_dimension:
                                logger.error(f"X dimension in {foundBlockParameter.name} do not match description!")
                            foundBlockParameter.values.append(parameters)
                        elif line.startswith("EINHEIT_W"):
                            foundBlockParameter.unit = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundBlockParameter.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._blockParameterList.append(foundBlockParameter)

                # Check if characteristic line
                elif line.startswith("KENNLINIE"):
                    reMatch = re.search(r"KENNLINIE\s+(.*?)\s+(\d+)", line.strip())
                    foundCharacteristicLine = DcmCharacteristicLine(reMatch.group(1))
                    foundCharacteristicLine.x_dimension = self.convertValue(reMatch.group(2))
                    parameters = []
                    stx = []

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(stx) != foundCharacteristicLine.x_dimension:
                                logger.error(f"X dimension in {foundCharacteristicLine.name} do not match description!")
                            if len(parameters) != foundCharacteristicLine.x_dimension:
                                logger.error(
                                    f"Values dimension in {foundCharacteristicLine.name} do not match description!"
                                )
                            foundCharacteristicLine.values = dict(zip(stx, parameters))
                            break
                        elif line.startswith("LANGNAME"):
                            foundCharacteristicLine.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundCharacteristicLine.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundCharacteristicLine.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_W"):
                            foundCharacteristicLine.unit_values = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundCharacteristicLine.unit_x = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundCharacteristicLine.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._characteristicLineList.append(foundCharacteristicLine)

                # Check if fixed characteristic line
                elif line.startswith("FESTKENNLINIE"):
                    reMatch = re.search(r"FESTKENNLINIE\s+(.*?)\s+(\d+)", line.strip())
                    foundFixedCharacteristicLine = DcmFixedCharacteristicLine(reMatch.group(1))
                    foundFixedCharacteristicLine.x_dimension = self.convertValue(reMatch.group(2))
                    parameters = []
                    stx = []

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(stx) != foundFixedCharacteristicLine.x_dimension:
                                logger.error(
                                    f"X dimension in {foundFixedCharacteristicLine.name} do not match description!"
                                )
                            if len(parameters) != foundFixedCharacteristicLine.x_dimension:
                                logger.error(
                                    f"Values dimension in {foundFixedCharacteristicLine.name} do not match description!"
                                )
                            foundFixedCharacteristicLine.values = dict(zip(stx, parameters))
                            break
                        elif line.startswith("LANGNAME"):
                            foundFixedCharacteristicLine.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundFixedCharacteristicLine.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundFixedCharacteristicLine.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_W"):
                            foundFixedCharacteristicLine.unit_values = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundFixedCharacteristicLine.unit_x = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundFixedCharacteristicLine.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._fixedCharacteristicLineList.append(foundFixedCharacteristicLine)

                # Check if group characteristic line
                elif line.startswith("GRUPPENKENNLINIE"):
                    reMatch = re.search(r"GRUPPENKENNLINIE\s+(.*?)\s+(\d+)", line.strip())
                    foundGroupCharacteristicLine = DcmGroupCharacteristicLine(reMatch.group(1))
                    foundGroupCharacteristicLine.x_dimension = self.convertValue(reMatch.group(2))
                    parameters = []
                    stx = []

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(parameters) != foundGroupCharacteristicLine.x_dimension:
                                logger.error(
                                    f"Values dimension in {foundGroupCharacteristicLine.name} do not match description!"
                                )
                            if len(stx) != foundGroupCharacteristicLine.x_dimension:
                                logger.error(
                                    f"X dimension in {foundGroupCharacteristicLine.name} do not match description!"
                                )
                            foundGroupCharacteristicLine.values = dict(zip(stx, parameters))
                            break
                        elif line.startswith("LANGNAME"):
                            foundGroupCharacteristicLine.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundGroupCharacteristicLine.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundGroupCharacteristicLine.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_W"):
                            foundGroupCharacteristicLine.unit_values = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundGroupCharacteristicLine.unit_x = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundGroupCharacteristicLine.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._groupCharacteristicLineList.append(foundGroupCharacteristicLine)

                # Check for characteristic map
                elif line.startswith("KENNFELD "):
                    reMatch = re.search(r"KENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line.strip())
                    foundCharacteristicMap = DcmCharacteristicMap(reMatch.group(1))
                    foundCharacteristicMap.x_dimension = self.convertValue(reMatch.group(2))
                    foundCharacteristicMap.y_dimension = self.convertValue(reMatch.group(3))
                    stx = []
                    sty = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(foundCharacteristicMap.values) != foundCharacteristicMap.y_dimension:
                                logger.error(
                                    f"Values dimension in {foundCharacteristicMap.name} does not match description!"
                                )
                            if len(stx) != foundCharacteristicMap.x_dimension:
                                logger.error(f"X dimension in {foundCharacteristicMap.name} do not match description!")
                            for name, entry in foundCharacteristicMap.values.items():
                                if len(entry) != foundCharacteristicMap.x_dimension:
                                    logger.error(
                                        f"Values dimension in {foundCharacteristicMap.name} does not match description!"
                                    )
                                else:
                                    foundCharacteristicMap.values[name] = dict(zip(stx, entry))
                            break
                        elif line.startswith("LANGNAME"):
                            foundCharacteristicMap.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundCharacteristicMap.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundCharacteristicMap.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(f"Values before stx/sty in {foundCharacteristicMap.name}")
                            parameters = self.parseBlockParameters(line)
                            if sty not in foundCharacteristicMap.values.keys():
                                foundCharacteristicMap.values[sty] = []
                            foundCharacteristicMap.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundCharacteristicMap.unit_values = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundCharacteristicMap.unit_x = self.parseString(line)
                        elif line.startswith("EINHEIT_Y"):
                            foundCharacteristicMap.unit_y = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundCharacteristicMap.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._characteristicMapList.append(foundCharacteristicMap)

                # Check for fixed characteristic map
                elif line.startswith("FESTKENNFELD "):
                    reMatch = re.search(r"FESTKENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line.strip())
                    foundFixedCharacteristicMap = DcmFixedCharacteristicMap(reMatch.group(1))
                    foundFixedCharacteristicMap.x_dimension = self.convertValue(reMatch.group(2))
                    foundFixedCharacteristicMap.y_dimension = self.convertValue(reMatch.group(3))
                    stx = []
                    sty = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(foundFixedCharacteristicMap.values) != foundFixedCharacteristicMap.y_dimension:
                                logger.error(
                                    f"Values dimension in {foundFixedCharacteristicMap.name} does not match description!"
                                )
                            if len(stx) != foundFixedCharacteristicMap.x_dimension:
                                logger.error(
                                    f"X dimension in {foundFixedCharacteristicMap.name} do not match description!"
                                )
                            for name, entry in foundFixedCharacteristicMap.values.items():
                                if len(entry) != foundFixedCharacteristicMap.x_dimension:
                                    logger.error(
                                        f"Values dimension in {foundFixedCharacteristicMap.name} does not match description!"
                                    )
                                else:
                                    foundFixedCharacteristicMap.values[name] = dict(zip(stx, entry))
                            break
                        elif line.startswith("LANGNAME"):
                            foundFixedCharacteristicMap.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundFixedCharacteristicMap.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundFixedCharacteristicMap.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(f"Values before stx/sty in {foundFixedCharacteristicMap.name}")
                            parameters = self.parseBlockParameters(line)
                            if sty not in foundFixedCharacteristicMap.values.keys():
                                foundFixedCharacteristicMap.values[sty] = []
                            foundFixedCharacteristicMap.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundFixedCharacteristicMap.unit_values = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundFixedCharacteristicMap.unit_x = self.parseString(line)
                        elif line.startswith("EINHEIT_Y"):
                            foundFixedCharacteristicMap.unit_y = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundFixedCharacteristicMap.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._fixedCharacteristicMapList.append(foundFixedCharacteristicMap)

                # Check for group characteristic map
                elif line.startswith("GRUPPENKENNFELD "):
                    reMatch = re.search(r"GRUPPENKENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line.strip())
                    foundGroupCharacteristicMap = DcmGroupCharacteristicMap(reMatch.group(1))
                    foundGroupCharacteristicMap.x_dimension = self.convertValue(reMatch.group(2))
                    foundGroupCharacteristicMap.y_dimension = self.convertValue(reMatch.group(3))
                    stx = []
                    sty = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(foundGroupCharacteristicMap.values) != foundGroupCharacteristicMap.y_dimension:
                                logger.error(
                                    f"Values dimension in {foundGroupCharacteristicMap.name} does not match description!"
                                )
                            if len(stx) != foundGroupCharacteristicMap.x_dimension:
                                logger.error(
                                    f"X dimension in {foundGroupCharacteristicMap.name} do not match description!"
                                )
                            for name, entry in foundGroupCharacteristicMap.values.items():
                                if len(entry) != foundGroupCharacteristicMap.x_dimension:
                                    logger.error(
                                        f"Values dimension in {foundGroupCharacteristicMap.name} does not match description!"
                                    )
                                else:
                                    foundGroupCharacteristicMap.values[name] = dict(zip(stx, entry))
                            break
                        elif line.startswith("LANGNAME"):
                            foundGroupCharacteristicMap.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundGroupCharacteristicMap.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundGroupCharacteristicMap.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(f"Values before stx/sty in {foundGroupCharacteristicMap.name}")
                            parameters = self.parseBlockParameters(line)
                            if sty not in foundGroupCharacteristicMap.values.keys():
                                foundGroupCharacteristicMap.values[sty] = []
                            foundGroupCharacteristicMap.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundGroupCharacteristicMap.unit_values = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundGroupCharacteristicMap.unit_x = self.parseString(line)
                        elif line.startswith("EINHEIT_Y"):
                            foundGroupCharacteristicMap.unit_y = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundGroupCharacteristicMap.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._groupCharacteristicMapList.append(foundGroupCharacteristicMap)

                # Check if distribution
                elif line.startswith("STUETZSTELLENVERTEILUNG"):
                    reMatch = re.search(r"STUETZSTELLENVERTEILUNG\s+(.*?)\s+(\d+)", line.strip())
                    foundDistribution = DcmDistribution(reMatch.group(1))
                    foundDistribution.x_dimension = self.convertValue(reMatch.group(2))
                    parameters = None
                    stx = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(foundDistribution.values) != foundDistribution.x_dimension:
                                logger.error(f"X dimension in {foundDistribution.name} do not match description!")
                            break
                        elif line.startswith("LANGNAME"):
                            foundDistribution.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundDistribution.display_name = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundDistribution.function = self.parseString(line)
                        elif line.startswith("ST/X"):
                            foundDistribution.values.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_X"):
                            foundDistribution.unit_x = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundDistribution.variants.update(self.parseVariant(line))
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._distributionList.append(foundDistribution)

                # Unknown start of line
                else:
                    logger.warning(f"Unknown line detected\n{line}")

    def getFunctions(self) -> list:
        """Returns all found functions as a list"""
        return self._functionsList

    def getParameters(self) -> list:
        """Returns all found parameters as a list"""
        return self._parameterList

    def getBlockParameters(self) -> list:
        """Returns all found block parameters as a list"""
        return self._blockParameterList

    def getCharacteristicLines(self) -> list:
        """Returns all found characteristic lines as a list"""
        return self._characteristicLineList

    def getFixedCharacteristicLines(self) -> list:
        """Returns all found fixed characteristic lines as a list"""
        return self._fixedCharacteristicLineList

    def getGroupCharacteristicLines(self) -> list:
        """Returns all found group characteristic lines as a list"""
        return self._groupCharacteristicLineList

    def getCharacteristicMaps(self) -> list:
        """Returns all found characteristic maps as a list"""
        return self._characteristicMapList

    def getFixedCharacteristicMaps(self) -> list:
        """Returns all found fixed characteristic maps as a list"""
        return self._fixedCharacteristicMapList

    def getGroupCharacteristicMaps(self) -> list:
        """Returns all found group characteristic maps as a list"""
        return self._groupCharacteristicMapList

    def getDistributions(self) -> list:
        """Returns all found distributions as a list"""
        return self._distributionList

    def __str__(self) -> str:
        output_string = ""
        # Print the file header
        for line in self._fileHeader.splitlines(True):
            output_string += f"* {line}"

        # Print the file version
        output_string += "\nKONSERVIERUNG_FORMAT 2.0\n"

        # Print the functions list
        output_string += "\nFUNKTIONEN\n"
        for function in sorted(self._functionsList):
            output_string += f"  {function}\n"
        output_string += "END\n\n"

        # Print rest of DCM objects
        objectList = list()
        objectList.extend(self._parameterList)
        objectList.extend(self._blockParameterList)
        objectList.extend(self._characteristicLineList)
        objectList.extend(self._fixedCharacteristicLineList)
        objectList.extend(self._groupCharacteristicLineList)
        objectList.extend(self._characteristicMapList)
        objectList.extend(self._fixedCharacteristicMapList)
        objectList.extend(self._groupCharacteristicMapList)
        objectList.extend(self._distributionList)

        for object in sorted(objectList):
            output_string += f"\n{object}\n"

        return output_string
