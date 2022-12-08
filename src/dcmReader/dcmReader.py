import logging
import os
import re
import sys

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DcmFunction:
    """Definition of a function

    Attributes:
        name (str):         Name of the function
        version (str):      Version number of the function
        description (str):  Description of the function
    """
    name = None
    description = None
    version = None

    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    def __str__(self):
        return (
            f"{self.name}\n  Version: {self.version}\n  Description: {self.description}"
        )


class DcmParameter:
    """Definition of a parameter
    
    Attributes:
        name (str):         Name of the parameter
        description (str):  Description of the parameter, started by LANGNAME in DCM
        displayName (str):  Parameter name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the parameter, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit (str):         Unit of the parameter, started by EINHEIT_W in DCM
        value (float/int):  Value of the parameter, started by WERT in DCM
        text (str):         Alternative text-value, started by TEXT in DCM
    """

    def __init__(self, name):
        self.name = name
        self.value = None
        self.description = None
        self.displayName = None
        self.variants = dict()
        self.function = None
        self.unit = None
        self.text = None

    def __str__(self):
        variants = ""
        for variantName, variantValue in self.variants.items():
            variants = variants + f"  {variantName}  =  {variantValue}\n  "
        return f"""Parameter {self.name}
  Description: {self.description}
  DisplayName: {self.displayName}
  Function:    {self.function}
  Value:       {self.value}
  Unit:        {self.unit}
  Text:        {self.text}
  Variants:
  {variants}"""


class DcmParameterBlock:
    """Definition of a block parameter
    
    Attributes:
        name (str):         Name of the block parameter
        description (str):  Description of the block parameter, started by LANGNAME in DCM
        displayName (str):  Block parameter name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the block parameter, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unit (str):         Unit of the block parameters, started by EINHEIT_W in DCM
        values (list):      List of values of the block parameter, started by WERT in DCM
        xDimension (int):   Dimension in x direction of the block parameter
        yDimension (int):   Dimension in y direction of the block parameter
    """

    def __init__(self, name):
        self.name = name
        self.values = []
        self.description = None
        self.displayName = None
        self.variants = dict()
        self.function = None
        self.unit = None
        self.xDimension = 0
        self.yDimension = 0

    def __str__(self):
        variants = ""
        for variantName, variantValue in self.variants.items():
            variants = variants + f"  {variantName}  =  {variantValue}\n  "
        return f"""Parameter {self.name}
  Description: {self.description}
  DisplayName: {self.displayName}
  Function:    {self.function}
  Value:       {self.values}
  Unit:        {self.unit}
  Variants:
  {variants}"""


class DcmCharacteristicLine:
    """Definition of a characteristic line
    
    Attributes:
        name (str):         Name of the characteristic line
        description (str):  Description of the characteristic line, started by LANGNAME in DCM
        displayName (str):  Characteristic line name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the characteristic line, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unitX (str):        Unit of the x axis values, started by EINHEIT_X in DCM
        unitValues (str):   Unit of the values, started by EINHEIT_W in DCM
        values (dict):      Dict of values of the parameter, KEYs are retrieved from ST/X, 
                            values are retrieved from WERT
        xDimension (int):   Dimension in x direction of the parameter block
    """
    def __init__(self, name) -> None:
        self.name = name
        self.values = dict()
        self.description = None
        self.displayName = None
        self.variants = dict()
        self.function = None
        self.unitX = None
        self.unitValues = None
        self.xDimension = 0

    def __str__(self):
        variants = ""
        for variantName, variantValue in self.variants.items():
            variants = variants + f"  {variantName}  =  {variantValue}\n  "
        return f"""Parameter {self.name}
  Description: {self.description}
  DisplayName: {self.displayName}
  Function:    {self.function}
  Value:       {self.values}
  Unit X:      {self.unitX}
  Unit Values: {self.unitValues}
  Variants:
  {variants}"""


class DcmFixedCharacteristicLine(DcmCharacteristicLine):
    """Definition of a fixed characteristic line, derived from characteristic line"""
    def __init__(self, name) -> None:
        super().__init__(name)


class DcmGroupCharacteristicLine(DcmCharacteristicLine):
    """Definition of a group characteristic line, derived from characteristic line"""
    def __init__(self, name) -> None:
        super().__init__(name)


class DcmCharacteristicMap:
    """Definition of a characteristic map

    Attributes:
        name (str):         Name of the characteristic map
        description (str):  Description of the characteristic map, started by LANGNAME in DCM
        displayName (str):  Characteristic map name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the characteristic map, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unitX (str):        Unit of the x axis values, started by EINHEIT_X in DCM
        unitY (str):        Unit of the y axis values, started by EINHEIT_Y in DCM
        unitValues (str):   Unit of the values, started by EINHEIT_W in DCM
        values (dict):      2D Dict of values of the parameter
                            The inner dict contains the values from ST/X as keys and the 
                            values retrieved from WERT as values. The keys of the outer dict 
                            contains the values from ST/Y.
        xDimension (int):   Dimension in x direction of the characteristic maps
        yDimension (int):   Dimension in y direction of the characteristic maps
    """

    def __init__(self, name) -> None:
        self.name = name
        self.values = dict()
        self.description = None
        self.displayName = None
        self.variants = dict()
        self.function = None
        self.unitX = None
        self.unitY = None
        self.unitValues = None
        self.xDimension = 0
        self.yDimension = 0

    def __str__(self):
        variants = ""
        for variantName, variantValue in self.variants.items():
            variants = variants + f"  {variantName}  =  {variantValue}\n  "
        return f"""Parameter {self.name}
  Description: {self.description}
  DisplayName: {self.displayName}
  Function:    {self.function}
  Value:       {self.values}
  Unit X:      {self.unitX}
  Unit X:      {self.unitY}
  Unit Values: {self.unitValues}
  Variants:
  {variants}"""


class DcmFixedCharacteristicMap(DcmCharacteristicMap):
    """Definition of a fixed characteristic map, derived from characteristic map"""
    def __init__(self, name) -> None:
        super().__init__(name)


class DcmGroupCharacteristicMap(DcmCharacteristicMap):
    """Definition of a group characteristic map, derived from characteristic map"""
    def __init__(self, name) -> None:
        super().__init__(name)


class DcmDistribution:
    """Definition of a distribution
    
    Attributes:
        name (str):         Name of the distribution
        description (str):  Description of the distribution, started by LANGNAME in DCM
        displayName (str):  Distribution name according asam-2mc, started by DISPLAYNAME in DCM
        variants (dict):    Variants for the distribution, started by VAR in DCM
        function (str):     Name of the assigned function, started by FUNKTION in DCM
        unitX (str):        Unit of the x axis values, started by EINHEIT_X in DCM
        values (list):      List of values of the distribution, values are retrieved from WERT
        xDimension (int):   Dimension in x direction of the distribution
    """
    def __init__(self, name) -> None:
        self.name = name
        self.values = []
        self.description = None
        self.displayName = None
        self.variants = dict()
        self.function = None
        self.unitX = None
        self.xDimension = 0

    def __str__(self):
        variants = ""
        for variantName, variantValue in self.variants.items():
            variants = variants + f"  {variantName}  =  {variantValue}\n  "
        return f"""Parameter {self.name}
  Description: {self.description}
  DisplayName: {self.displayName}
  Function:    {self.function}
  Value:       {self.values}
  Unit X:      {self.unitX}
  Variants:
  {variants}"""


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
        variant = re.search(r"VAR\s+(.*?)=(.*)", line)
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
                        self._fileHeader = (
                            self._fileHeader + line[1:].strip() + os.linesep
                        )
                    continue

                # At this point first comment block passed
                self._fileHeaderFinished = True

                # Check if empty line
                if line == "":
                    continue

                # Check if format version line
                if _dcmFormat is None:
                    if line.startswith("KONSERVIERUNG_FORMAT"):
                        _dcmFormat = float(re.search(r"(\d\.\d)", line).group(1))
                        continue
                    else:
                        logging.info(f"Found line: {line}")
                        raise Exception(
                            "Incorrect file structure. DCM file format has to be first entry!"
                        )

                # Check if functions start
                if line.startswith("FUNKTIONEN"):
                    while True:
                        line = f.readline()
                        if line.startswith("END"):
                            break
                        functionMatch = re.search(
                            r"\s+FKT (.*?)(?: \"(.*?)?\"(?: \"(.*?)?\")?)?$", line
                        )
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
                            foundParameter.displayName = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundParameter.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            foundParameter.value = self.convertValue(
                                line.split(" ", 1)[1].strip()
                            )
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
                    blockData = re.search(
                        r"FESTWERTEBLOCK\s+(.*?)\s+(\d+)(?:\s+\@\s+(\d+))?", line
                    )
                    foundBlockParameter = DcmParameterBlock(blockData.group(1))
                    foundBlockParameter.xDimension = self.convertValue(
                        blockData.group(2)
                    )
                    foundBlockParameter.yDimension = (
                        self.convertValue(blockData.group(3))
                        if blockData.group(3) is not None
                        else 1
                    )
                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if (
                                len(foundBlockParameter.values)
                                != foundBlockParameter.yDimension
                            ):
                                logger.error(
                                    f"Y dimension in {foundBlockParameter.name} do not match description!"
                                )
                            break
                        elif line.startswith("LANGNAME"):
                            foundBlockParameter.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundBlockParameter.displayName = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundBlockParameter.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            parameters = self.parseBlockParameters(line)
                            if len(parameters) != foundBlockParameter.xDimension:
                                logger.error(
                                    f"X dimension in {foundBlockParameter.name} do not match description!"
                                )
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
                    reMatch = re.search(r"KENNLINIE\s+(.*?)\s+(\d+)", line)
                    foundCharacteristicLine = DcmCharacteristicLine(reMatch.group(1))
                    foundCharacteristicLine.xDimension = self.convertValue(
                        reMatch.group(2)
                    )
                    parameters = []
                    stx = []

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(stx) != foundCharacteristicLine.xDimension:
                                logger.error(
                                    f"X dimension in {foundCharacteristicLine.name} do not match description!"
                                )
                            if len(parameters) != foundCharacteristicLine.xDimension:
                                logger.error(
                                    f"Values dimension in {foundCharacteristicLine.name} do not match description!"
                                )
                            foundCharacteristicLine.values = dict(zip(stx, parameters))
                            break
                        elif line.startswith("LANGNAME"):
                            foundCharacteristicLine.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundCharacteristicLine.displayName = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundCharacteristicLine.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            parameters.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_W"):
                            foundCharacteristicLine.unitValues = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundCharacteristicLine.unitX = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundCharacteristicLine.variants.update(
                                self.parseVariant(line)
                            )
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._characteristicLineList.append(foundCharacteristicLine)

                # Check if fixed characteristic line
                elif line.startswith("FESTKENNLINIE"):
                    reMatch = re.search(r"FESTKENNLINIE\s+(.*?)\s+(\d+)", line)
                    foundFixedCharacteristicLine = DcmFixedCharacteristicLine(
                        reMatch.group(1)
                    )
                    foundFixedCharacteristicLine.xDimension = self.convertValue(
                        reMatch.group(2)
                    )
                    parameters = []
                    stx = []

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if len(stx) != foundFixedCharacteristicLine.xDimension:
                                logger.error(
                                    f"X dimension in {foundFixedCharacteristicLine.name} do not match description!"
                                )
                            if (
                                len(parameters)
                                != foundFixedCharacteristicLine.xDimension
                            ):
                                logger.error(
                                    f"Values dimension in {foundFixedCharacteristicLine.name} do not match description!"
                                )
                            foundFixedCharacteristicLine.values = dict(
                                zip(stx, parameters)
                            )
                            break
                        elif line.startswith("LANGNAME"):
                            foundFixedCharacteristicLine.description = self.parseString(
                                line
                            )
                        elif line.startswith("DISPLAYNAME"):
                            foundFixedCharacteristicLine.displayName = self.parseString(
                                line
                            )
                        elif line.startswith("FUNKTION"):
                            foundFixedCharacteristicLine.function = self.parseString(
                                line
                            )
                        elif line.startswith("WERT"):
                            parameters.extend(self.parseBlockParameters(line))                        
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))                        
                        elif line.startswith("EINHEIT_W"):
                            foundFixedCharacteristicLine.unitValues = self.parseString(
                                line
                            )
                        elif line.startswith("EINHEIT_X"):
                            foundFixedCharacteristicLine.unitX = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundFixedCharacteristicLine.variants.update(
                                self.parseVariant(line)
                            )
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._fixedCharacteristicLineList.append(
                        foundFixedCharacteristicLine
                    )

                # Check if group characteristic line
                elif line.startswith("GRUPPENKENNLINIE"):
                    reMatch = re.search(r"GRUPPENKENNLINIE\s+(.*?)\s+(\d+)", line)
                    foundGroupCharacteristicLine = DcmGroupCharacteristicLine(
                        reMatch.group(1)
                    )
                    foundGroupCharacteristicLine.xDimension = self.convertValue(
                        reMatch.group(2)
                    )
                    parameters = []
                    stx = []

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if (
                                len(parameters)
                                != foundGroupCharacteristicLine.xDimension
                            ):
                                logger.error(
                                    f"Values dimension in {foundGroupCharacteristicLine.name} do not match description!"
                                )
                            if len(stx) != foundGroupCharacteristicLine.xDimension:
                                logger.error(
                                    f"X dimension in {foundGroupCharacteristicLine.name} do not match description!"
                                )
                            foundGroupCharacteristicLine.values = dict(
                                zip(stx, parameters)
                            )
                            break
                        elif line.startswith("LANGNAME"):
                            foundGroupCharacteristicLine.description = self.parseString(
                                line
                            )
                        elif line.startswith("DISPLAYNAME"):
                            foundGroupCharacteristicLine.displayName = self.parseString(
                                line
                            )
                        elif line.startswith("FUNKTION"):
                            foundGroupCharacteristicLine.function = self.parseString(
                                line
                            )
                        elif line.startswith("WERT"):
                            parameters.extend(self.parseBlockParameters(line))                            
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_W"):
                            foundGroupCharacteristicLine.unitValues = self.parseString(
                                line
                            )
                        elif line.startswith("EINHEIT_X"):
                            foundGroupCharacteristicLine.unitX = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundGroupCharacteristicLine.variants.update(
                                self.parseVariant(line)
                            )
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._groupCharacteristicLineList.append(
                        foundGroupCharacteristicLine
                    )

                # Check for characteristic map
                elif line.startswith("KENNFELD "):
                    reMatch = re.search(r"KENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line)
                    foundCharacteristicMap = DcmCharacteristicMap(reMatch.group(1))
                    foundCharacteristicMap.xDimension = self.convertValue(
                        reMatch.group(2)
                    )
                    foundCharacteristicMap.yDimension = self.convertValue(
                        reMatch.group(3)
                    )
                    stx = []
                    sty = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if (
                                len(foundCharacteristicMap.values)
                                != foundCharacteristicMap.yDimension
                            ):
                                logger.error(
                                    f"Values dimension in {foundCharacteristicMap.name} does not match description!"
                                )
                            if len(stx) != foundCharacteristicMap.xDimension:
                                logger.error(
                                    f"X dimension in {foundCharacteristicMap.name} do not match description!"
                                )
                            for name, entry in foundCharacteristicMap.values.items():
                                if len(entry) != foundCharacteristicMap.xDimension:
                                    logger.error(
                                        f"Values dimension in {foundCharacteristicMap.name} does not match description!"
                                    )
                                else:
                                    foundCharacteristicMap.values[name] = dict(zip(stx, entry))
                            break
                        elif line.startswith("LANGNAME"):
                            foundCharacteristicMap.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundCharacteristicMap.displayName = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundCharacteristicMap.function = self.parseString(line)
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(
                                    f"Values before stx/sty in {foundCharacteristicMap.name}"
                                )
                            parameters = self.parseBlockParameters(line)
                            if sty not in foundCharacteristicMap.values.keys():
                                foundCharacteristicMap.values[sty] = []
                            foundCharacteristicMap.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundCharacteristicMap.unitValues = self.parseString(line)
                        elif line.startswith("EINHEIT_X"):
                            foundCharacteristicMap.unitX = self.parseString(line)
                        elif line.startswith("EINHEIT_Y"):
                            foundCharacteristicMap.unitY = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundCharacteristicMap.variants.update(
                                self.parseVariant(line)
                            )
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._characteristicMapList.append(foundCharacteristicMap)

                # Check for fixed characteristic map
                elif line.startswith("FESTKENNFELD "):
                    reMatch = re.search(r"FESTKENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line)
                    foundFixedCharacteristicMap = DcmFixedCharacteristicMap(
                        reMatch.group(1)
                    )
                    foundFixedCharacteristicMap.xDimension = self.convertValue(
                        reMatch.group(2)
                    )
                    foundFixedCharacteristicMap.yDimension = self.convertValue(
                        reMatch.group(3)
                    )
                    stx = []
                    sty = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if (
                                len(foundFixedCharacteristicMap.values)
                                != foundFixedCharacteristicMap.yDimension
                            ):
                                logger.error(
                                    f"Values dimension in {foundFixedCharacteristicMap.name} does not match description!"
                                )
                            if len(stx) != foundFixedCharacteristicMap.xDimension:
                                logger.error(
                                    f"X dimension in {foundFixedCharacteristicMap.name} do not match description!"
                                )
                            for name, entry in foundFixedCharacteristicMap.values.items():
                                if (
                                    len(entry)
                                    != foundFixedCharacteristicMap.xDimension
                                ):
                                    logger.error(
                                        f"Values dimension in {foundFixedCharacteristicMap.name} does not match description!"
                                    )
                                else:
                                    foundFixedCharacteristicMap.values[name] = dict(zip(stx, entry))
                            break
                        elif line.startswith("LANGNAME"):
                            foundFixedCharacteristicMap.description = self.parseString(
                                line
                            )
                        elif line.startswith("DISPLAYNAME"):
                            foundFixedCharacteristicMap.displayName = self.parseString(
                                line
                            )
                        elif line.startswith("FUNKTION"):
                            foundFixedCharacteristicMap.function = self.parseString(
                                line
                            )
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(
                                    f"Values before stx/sty in {foundFixedCharacteristicMap.name}"
                                )
                            parameters = self.parseBlockParameters(line)
                            if sty not in foundFixedCharacteristicMap.values.keys():
                                foundFixedCharacteristicMap.values[sty] = []
                            foundFixedCharacteristicMap.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundFixedCharacteristicMap.unitValues = self.parseString(
                                line
                            )
                        elif line.startswith("EINHEIT_X"):
                            foundFixedCharacteristicMap.unitX = self.parseString(line)
                        elif line.startswith("EINHEIT_Y"):
                            foundFixedCharacteristicMap.unitY = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundFixedCharacteristicMap.variants.update(
                                self.parseVariant(line)
                            )
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._fixedCharacteristicMapList.append(foundFixedCharacteristicMap)

                # Check for group characteristic map
                elif line.startswith("GRUPPENKENNFELD "):
                    reMatch = re.search(
                        r"GRUPPENKENNFELD\s+(.*?)\s+(\d+)\s+(\d+)", line
                    )
                    foundGroupCharacteristicMap = DcmGroupCharacteristicMap(
                        reMatch.group(1)
                    )
                    foundGroupCharacteristicMap.xDimension = self.convertValue(
                        reMatch.group(2)
                    )
                    foundGroupCharacteristicMap.yDimension = self.convertValue(
                        reMatch.group(3)
                    )
                    stx = []
                    sty = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if (
                                len(foundGroupCharacteristicMap.values)
                                != foundGroupCharacteristicMap.yDimension
                            ):
                                logger.error(
                                    f"Values dimension in {foundGroupCharacteristicMap.name} does not match description!"
                                )
                            if len(stx) != foundGroupCharacteristicMap.xDimension:
                                logger.error(
                                    f"X dimension in {foundGroupCharacteristicMap.name} do not match description!"
                                )
                            for name, entry in foundGroupCharacteristicMap.values.items():
                                if (
                                    len(entry)
                                    != foundGroupCharacteristicMap.xDimension
                                ):
                                    logger.error(
                                        f"Values dimension in {foundGroupCharacteristicMap.name} does not match description!"
                                    )
                                else:
                                    foundGroupCharacteristicMap.values[name] = dict(zip(stx, entry))
                            break
                        elif line.startswith("LANGNAME"):
                            foundGroupCharacteristicMap.description = self.parseString(
                                line
                            )
                        elif line.startswith("DISPLAYNAME"):
                            foundGroupCharacteristicMap.displayName = self.parseString(
                                line
                            )
                        elif line.startswith("FUNKTION"):
                            foundGroupCharacteristicMap.function = self.parseString(
                                line
                            )
                        elif line.startswith("WERT"):
                            if stx is None or sty is None:
                                raise ValueError(
                                    f"Values before stx/sty in {foundGroupCharacteristicMap.name}"
                                )
                            parameters = self.parseBlockParameters(line)
                            if sty not in foundGroupCharacteristicMap.values.keys():
                                foundGroupCharacteristicMap.values[sty] = []
                            foundGroupCharacteristicMap.values[sty].extend(parameters)
                        elif line.startswith("ST/X"):
                            stx.extend(self.parseBlockParameters(line))
                        elif line.startswith("ST/Y"):
                            sty = self.convertValue(line.split(" ", 1)[1].strip())
                        elif line.startswith("EINHEIT_W"):
                            foundGroupCharacteristicMap.unitValues = self.parseString(
                                line
                            )
                        elif line.startswith("EINHEIT_X"):
                            foundGroupCharacteristicMap.unitX = self.parseString(line)
                        elif line.startswith("EINHEIT_Y"):
                            foundGroupCharacteristicMap.unitY = self.parseString(line)
                        elif line.startswith("VAR"):
                            foundGroupCharacteristicMap.variants.update(
                                self.parseVariant(line)
                            )
                        else:
                            if not line.startswith("*"):
                                logger.warning(f"Unknown parameter field: {line}")

                    self._groupCharacteristicMapList.append(foundGroupCharacteristicMap)

                # Check if distribution
                elif line.startswith("STUETZSTELLENVERTEILUNG"):
                    reMatch = re.search(
                        r"STUETZSTELLENVERTEILUNG\s+(.*?)\s+(\d+)", line
                    )
                    foundDistribution = DcmDistribution(reMatch.group(1))
                    foundDistribution.xDimension = self.convertValue(reMatch.group(2))
                    parameters = None
                    stx = None

                    while True:
                        line = f.readline().strip()
                        if line.startswith("END"):
                            if (
                                len(foundDistribution.values)
                                != foundDistribution.xDimension
                            ):
                                logger.error(
                                    f"X dimension in {foundDistribution.name} do not match description!"
                                )
                            break
                        elif line.startswith("LANGNAME"):
                            foundDistribution.description = self.parseString(line)
                        elif line.startswith("DISPLAYNAME"):
                            foundDistribution.displayName = self.parseString(line)
                        elif line.startswith("FUNKTION"):
                            foundDistribution.function = self.parseString(line)
                        elif line.startswith("ST/X"):
                            foundDistribution.values.extend(self.parseBlockParameters(line))
                        elif line.startswith("EINHEIT_X"):
                            foundDistribution.unitX = self.parseString(line)
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


if __name__ == "__main__":
    """Parses a DCM file and prints some information"""
    if len(sys.argv) < 2:
        print("Please specify dcm-file to parse")
        exit()

    filename = sys.argv[1]

    if os.path.isfile(filename) is False or filename.endswith(".dcm") is False:
        print("Input file not valid")
    else:
        dcm = DcmReader()
        dcm.read(filename)

        readFunctions = dcm.getFunctions()
        readParameters = dcm.getParameters()
        readBlockParameters = dcm.getBlockParameters()
        readCharacteristicLines = dcm.getCharacteristicLines()
        readFixedCharacteristicLines = dcm.getFixedCharacteristicLines()
        readGroupCharacteristicLines = dcm.getGroupCharacteristicLines()
        readCharacteristicMaps = dcm.getCharacteristicMaps()
        readFixedCharacteristicMaps = dcm.getFixedCharacteristicMaps()
        readGroupCharacteristicMaps = dcm.getGroupCharacteristicMaps()
        readDistributions = dcm.getDistributions()

        print()
        print(f"Successfully parsed {filename}")
        print("-" * (20 + len(filename)))
        print(f"Number of functions:                    {len(readFunctions)}")
        print(f"Number of parameters:                   {len(readParameters)}")
        print(f"Number of block parameters:             {len(readBlockParameters)}")
        print(f"Number of characteristic lines:         {len(readCharacteristicLines)}")
        print(
            f"Number of fixed characteristic lines:   {len(readFixedCharacteristicLines)}"
        )
        print(
            f"Number of group characteristic lines:   {len(readGroupCharacteristicLines)}"
        )
        print(f"Number of characteristic maps:          {len(readCharacteristicMaps)}")
        print(
            f"Number of fixed characteristic maps:    {len(readFixedCharacteristicMaps)}"
        )
        print(
            f"Number of group characteristic maps:    {len(readGroupCharacteristicMaps)}"
        )
        print(f"Number of distributions:                {len(readDistributions)}")
        print()
