# dcmReader
Parser for the DCM (Data Conservation format) format used by e.g. Vector, ETAS,...

## Basic usage
The read function of DcmParser parses the given DCM-file and stores internally the parsed values.

Sample program:

    dcm = DcmReader()
    dcm.read("tests/Sample.dcm")

    readFunctions = dcm.getFunctions()
    for fnc in readFunctions:
        print(fnc)

Will return:

    ParameterFunction
      Version: 1.0
      Description: Function for parameters
    BlockParameterFunction
      Version: 2.0
      Description: Function for block parameters
    CharacteristicLineFunction
      Version: 3.0
      Description: Function for characteristic line functions
    FixedCharacteristicLineFunction
      Version: 3.1
      Description: Function for fixed characteristic line functions
    GroupCharacteristicLineFunction
      Version: 3.2
      Description: Function for group characteristic line functions
    CharacteristicMapFunction
      Version: 4.0
      Description: Function for characteristic map functions
    FixedCharacteristicMapFunction
      Version: 4.1
      Description: Function for fixed characteristic map functions
    GroupCharacteristicMapFunction
      Version: 4.2
      Description: Function for group characteristic map functions
    DistributionFunction
      Version: 5.0
      Description: Function for distribution functions

## UnitTests
The UnitTests can be run in the tests directory by running
    python Tests.py