"""
Main program which prints information about DCM file
"""

import os
import sys

from dcmReader.dcm_reader import DcmReader

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify dcm-file to parse")
        sys.exit(1)

    filename = sys.argv[1]

    if os.path.isfile(filename) is False or filename.endswith(".dcm") is False:
        print("Input file not valid")
    else:
        dcm = DcmReader()
        dcm.read(filename)

        readFunctions = dcm.get_functions()
        readParameters = dcm.get_parameters()
        readBlockParameters = dcm.get_block_parameters()
        readCharacteristicLines = dcm.get_characteristic_lines()
        readFixedCharacteristicLines = dcm.get_fixed_characteristic_lines()
        readGroupCharacteristicLines = dcm.get_group_characteristic_lines()
        readCharacteristicMaps = dcm.get_characteristic_maps()
        readFixedCharacteristicMaps = dcm.get_fixed_characteristic_maps()
        readGroupCharacteristicMaps = dcm.get_group_characteristic_maps()
        readDistributions = dcm.get_distributions()

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

    sys.exit()
