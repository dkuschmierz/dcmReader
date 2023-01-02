# dcmReader
Parser for the DCM (Data Conservation format) format used by e.g. Vector, ETAS,...

## Basic usage
The read function of DcmParser parses the given DCM-file and stores internally the parsed values.

Sample program:
    from dcmReader.dcm_reader import DcmReader

    dcm = DcmReader()
    dcm.read("tests/Sample.dcm")

    readFunctions = dcm.get_functions()
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

You can also save a DCM object to a file with the write function. The output is sorted first by FUNKTION then by LANGNAME.
This can also be used to sort a DCM file:

    from dcmReader.dcm_reader import DcmReader

    dcm = DcmReader()
    dcm.read("tests/Sample.dcm")
    dcm.write("tests/Sample_sorted.dcm")

## UnitTests
The UnitTests can be run in the tests directory by running
    python Tests.py