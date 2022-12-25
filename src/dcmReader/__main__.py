import os
import sys

from dcmReader.dcm_reader import DcmReader

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
        print(f"Number of fixed characteristic lines:   {len(readFixedCharacteristicLines)}")
        print(f"Number of group characteristic lines:   {len(readGroupCharacteristicLines)}")
        print(f"Number of characteristic maps:          {len(readCharacteristicMaps)}")
        print(f"Number of fixed characteristic maps:    {len(readFixedCharacteristicMaps)}")
        print(f"Number of group characteristic maps:    {len(readGroupCharacteristicMaps)}")
        print(f"Number of distributions:                {len(readDistributions)}")
        print()
