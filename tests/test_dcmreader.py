import os
import sys
import unittest

testdir = os.path.dirname(__file__)
srcdir = "../src"
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

from dcmReader.dcm_reader import DcmReader


class TestWriteFile(unittest.TestCase):
    def test_fileWriting(self):
        dcm = DcmReader()
        dcm.read("./Sample.dcm")
        self.assertEqual(9, len(dcm.get_functions()))
        dcm.write("./Sample_written")


class TestFunctions(unittest.TestCase):
    def test_functionParsing(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        self.assertEqual(9, len(dcm.get_functions()))
        self.assertEqual(9, len(dcmWritten.get_functions()))


class TestParameters(unittest.TestCase):
    def test_foundParameter(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        self.assertEqual(2, len(dcm.get_parameters()))
        self.assertEqual(2, len(dcmWritten.get_parameters()))

    def test_valueParameter(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        valueParameter = dcm.get_parameters()[0]

        self.assertEqual("valueParameter", valueParameter.name)
        self.assertEqual("Sample value parameter", valueParameter.attrs["description"])
        self.assertEqual("ParameterFunction", valueParameter.attrs["function"])
        self.assertEqual("°C", valueParameter.attrs["units"])
        self.assertEqual(25.0, valueParameter.values)
        self.assertEqual(27.5, valueParameter.attrs["variants"]["VariantA"])
        self.assertEqual(None, valueParameter.text)
        self.assertEqual("Sample comment\nSecond comment line", valueParameter.attrs["comment"])

    def test_textParameter(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        valueParameter = dcm.get_parameters()[1]

        self.assertEqual("textParameter", valueParameter.name)
        self.assertEqual("Sample text parameter", valueParameter.attrs["description"])
        self.assertEqual("ParameterFunction", valueParameter.attrs["function"])
        self.assertEqual("-", valueParameter.attrs["units"])
        self.assertEqual(None, valueParameter.values)
        self.assertEqual("ParameterB", valueParameter.attrs["variants"]["VariantA"])
        self.assertEqual("ParameterA", valueParameter.text)


class TestParameterBlock(unittest.TestCase):
    def test_blockParameter1D(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        blockParameter = dcm.get_block_parameters()[0]
        blockParameterWritten = dcmWritten.get_block_parameters()[0]

        self.assertEqual("blockParameter1D", blockParameter.name)
        self.assertEqual("Sample block parameters", blockParameter.attrs["description"])
        self.assertEqual("BlockParameterFunction", blockParameter.attrs["function"])
        self.assertEqual("BlockParameterDisplayname", blockParameter.attrs["display_name"])
        self.assertEqual("°C", blockParameter.attrs["units"])
        self.assertEqual(0.75, blockParameter.values[0][0])
        self.assertEqual(-0.25, blockParameter.values[0][1])
        self.assertEqual(0.5, blockParameter.values[0][2])
        self.assertEqual(1.5, blockParameter.values[0][3])
        self.assertEqual("Sample comment", blockParameter.attrs["comment"])

        self.assertEqual("blockParameter1D", blockParameterWritten.name)
        self.assertEqual("Sample block parameters", blockParameterWritten.attrs["description"])
        self.assertEqual("BlockParameterFunction", blockParameterWritten.attrs["function"])
        self.assertEqual("BlockParameterDisplayname", blockParameterWritten.attrs["display_name"])
        self.assertEqual("°C", blockParameterWritten.attrs["units"])
        self.assertEqual(0.75, blockParameterWritten.values[0][0])
        self.assertEqual(-0.25, blockParameterWritten.values[0][1])
        self.assertEqual(0.5, blockParameterWritten.values[0][2])
        self.assertEqual(1.5, blockParameterWritten.values[0][3])
        self.assertEqual("Sample comment", blockParameterWritten.attrs["comment"])

    def test_blockParameter2D(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        blockParameter = dcm.get_block_parameters()[1]
        blockParameterWritten = dcmWritten.get_block_parameters()[1]

        self.assertEqual("blockParameter2D", blockParameter.name)
        self.assertEqual("Sample block parameters", blockParameter.attrs["description"])
        self.assertEqual("BlockParameterFunction", blockParameter.attrs["function"])
        self.assertEqual("BlockParameterDisplayname", blockParameter.attrs["display_name"])
        self.assertEqual("°C", blockParameter.attrs["units"])
        self.assertEqual(0.75, blockParameter.values[0][0])
        self.assertEqual(-0.25, blockParameter.values[0][1])
        self.assertEqual(0.5, blockParameter.values[0][2])
        self.assertEqual(1.5, blockParameter.values[0][3])
        self.assertEqual(10.75, blockParameter.values[1][0])
        self.assertEqual(-10.25, blockParameter.values[1][1])
        self.assertEqual(10.5, blockParameter.values[1][2])
        self.assertEqual(11.5, blockParameter.values[1][3])

        self.assertEqual("blockParameter2D", blockParameterWritten.name)
        self.assertEqual("Sample block parameters", blockParameterWritten.attrs["description"])
        self.assertEqual("BlockParameterFunction", blockParameterWritten.attrs["function"])
        self.assertEqual("BlockParameterDisplayname", blockParameterWritten.attrs["display_name"])
        self.assertEqual("°C", blockParameterWritten.attrs["units"])
        self.assertEqual(0.75, blockParameterWritten.values[0][0])
        self.assertEqual(-0.25, blockParameterWritten.values[0][1])
        self.assertEqual(0.5, blockParameterWritten.values[0][2])
        self.assertEqual(1.5, blockParameterWritten.values[0][3])
        self.assertEqual(10.75, blockParameterWritten.values[1][0])
        self.assertEqual(-10.25, blockParameterWritten.values[1][1])
        self.assertEqual(10.5, blockParameterWritten.values[1][2])
        self.assertEqual(11.5, blockParameterWritten.values[1][3])


class TestCharacteristicLines(unittest.TestCase):
    def test_characteristicLine(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_characteristic_lines()[0]
        characteristicWritten = dcmWritten.get_characteristic_lines()[0]

        self.assertEqual(1, len(dcm.get_characteristic_lines()))

        self.assertEqual("characteristicLine", characteristic.name)
        self.assertEqual("Sample characteristic line", characteristic.attrs["description"])
        self.assertEqual("CharacteristicLineFunction", characteristic.attrs["function"])
        self.assertEqual("CharacteristicLineDisplayname", characteristic.attrs["display_name"])
        self.assertEqual("°", characteristic.unit_values)
        self.assertEqual("s", characteristic.attrs["units_x"])
        self.assertEqual(0.0, characteristic.values[0.0])
        self.assertEqual(80.0, characteristic.values[1.0])
        self.assertEqual(120.0, characteristic.values[2.0])
        self.assertEqual(180.0, characteristic.values[3.0])
        self.assertEqual(220.0, characteristic.values[4.0])
        self.assertEqual(260.0, characteristic.values[5.0])
        self.assertEqual(300.0, characteristic.values[6.0])
        self.assertEqual(340.0, characteristic.values[7.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("Sample comment", characteristic.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_characteristic_lines()))

        self.assertEqual("characteristicLine", characteristicWritten.name)
        self.assertEqual("Sample characteristic line", characteristicWritten.attrs["description"])
        self.assertEqual("CharacteristicLineFunction", characteristicWritten.attrs["function"])
        self.assertEqual("CharacteristicLineDisplayname", characteristicWritten.attrs["display_name"])
        self.assertEqual("°", characteristicWritten.unit_values)
        self.assertEqual("s", characteristicWritten.attrs["units_x"])
        self.assertEqual(0.0, characteristicWritten.values[0.0])
        self.assertEqual(80.0, characteristicWritten.values[1.0])
        self.assertEqual(120.0, characteristicWritten.values[2.0])
        self.assertEqual(180.0, characteristicWritten.values[3.0])
        self.assertEqual(220.0, characteristicWritten.values[4.0])
        self.assertEqual(260.0, characteristicWritten.values[5.0])
        self.assertEqual(300.0, characteristicWritten.values[6.0])
        self.assertEqual(340.0, characteristicWritten.values[7.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("Sample comment", characteristicWritten.attrs["comment"])

    def test_fixedCharacteristicLine(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_fixed_characteristic_lines()[0]
        characteristicWritten = dcmWritten.get_fixed_characteristic_lines()[0]

        self.assertEqual(1, len(dcm.get_fixed_characteristic_lines()))

        self.assertEqual("fixedCharacteristicLine", characteristic.name)
        self.assertEqual("Sample fixed characteristic line", characteristic.attrs["description"])
        self.assertEqual("FixedCharacteristicLineFunction", characteristic.attrs["function"])
        self.assertEqual("FixedCharacteristicLineDisplayname", characteristic.attrs["display_name"])
        self.assertEqual("°", characteristic.unit_values)
        self.assertEqual("s", characteristic.attrs["units_x"])
        self.assertEqual(45.0, characteristic.values[0.0])
        self.assertEqual(90.0, characteristic.values[1.0])
        self.assertEqual(135.0, characteristic.values[2.0])
        self.assertEqual(180.0, characteristic.values[3.0])
        self.assertEqual(225.0, characteristic.values[4.0])
        self.assertEqual(270.0, characteristic.values[5.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("Sample comment", characteristic.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_fixed_characteristic_lines()))

        self.assertEqual("fixedCharacteristicLine", characteristicWritten.name)
        self.assertEqual("Sample fixed characteristic line", characteristicWritten.attrs["description"])
        self.assertEqual("FixedCharacteristicLineFunction", characteristicWritten.attrs["function"])
        self.assertEqual("FixedCharacteristicLineDisplayname", characteristicWritten.attrs["display_name"])
        self.assertEqual("°", characteristicWritten.unit_values)
        self.assertEqual("s", characteristicWritten.attrs["units_x"])
        self.assertEqual(45.0, characteristicWritten.values[0.0])
        self.assertEqual(90.0, characteristicWritten.values[1.0])
        self.assertEqual(135.0, characteristicWritten.values[2.0])
        self.assertEqual(180.0, characteristicWritten.values[3.0])
        self.assertEqual(225.0, characteristicWritten.values[4.0])
        self.assertEqual(270.0, characteristicWritten.values[5.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("Sample comment", characteristicWritten.attrs["comment"])

    def test_groupCharacteristicLine(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_group_characteristic_lines()[0]
        characteristicWritten = dcmWritten.get_group_characteristic_lines()[0]

        self.assertEqual(1, len(dcm.get_group_characteristic_lines()))

        self.assertEqual("groupCharacteristicLine", characteristic.name)
        self.assertEqual("Sample group characteristic line", characteristic.attrs["description"])
        self.assertEqual("GroupCharacteristicLineFunction", characteristic.attrs["function"])
        self.assertEqual("GroupCharacteristicLineDisplayname", characteristic.attrs["display_name"])
        self.assertEqual("°", characteristic.unit_values)
        self.assertEqual("s", characteristic.attrs["units_x"])
        self.assertEqual(-45.0, characteristic.values[1.0])
        self.assertEqual(-90.0, characteristic.values[2.0])
        self.assertEqual(-135.0, characteristic.values[3.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("Sample comment", characteristic.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_group_characteristic_lines()))

        self.assertEqual("groupCharacteristicLine", characteristicWritten.name)
        self.assertEqual("Sample group characteristic line", characteristicWritten.attrs["description"])
        self.assertEqual("GroupCharacteristicLineFunction", characteristicWritten.attrs["function"])
        self.assertEqual("GroupCharacteristicLineDisplayname", characteristicWritten.attrs["display_name"])
        self.assertEqual("°", characteristicWritten.unit_values)
        self.assertEqual("s", characteristicWritten.attrs["units_x"])
        self.assertEqual(-45.0, characteristicWritten.values[1.0])
        self.assertEqual(-90.0, characteristicWritten.values[2.0])
        self.assertEqual(-135.0, characteristicWritten.values[3.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("Sample comment", characteristicWritten.attrs["comment"])


class TestCharacteristicMaps(unittest.TestCase):
    def test_characteristicMap(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_characteristic_maps()[0]
        characteristicWritten = dcmWritten.get_characteristic_maps()[0]

        self.assertEqual(1, len(dcm.get_characteristic_maps()))

        self.assertEqual("characteristicMap", characteristic.name)
        self.assertEqual("Sample characteristic map", characteristic.attrs["description"])
        self.assertEqual("CharacteristicMapFunction", characteristic.attrs["function"])
        self.assertEqual("CharacteristicMapDisplayname", characteristic.attrs["display_name"])
        self.assertEqual("bar", characteristic.unit_values)
        self.assertEqual("°C", characteristic.attrs["units_x"])
        self.assertEqual("m/s", characteristic.attrs["units_y"])
        self.assertEqual(0.0, characteristic.values[1.0][1.0])
        self.assertEqual(0.4, characteristic.values[1.0][2.0])
        self.assertEqual(0.8, characteristic.values[1.0][3.0])
        self.assertEqual(1.0, characteristic.values[1.0][4.0])
        self.assertEqual(1.4, characteristic.values[1.0][5.0])
        self.assertEqual(1.8, characteristic.values[1.0][6.0])
        self.assertEqual(1.0, characteristic.values[2.0][1.0])
        self.assertEqual(2.0, characteristic.values[2.0][2.0])
        self.assertEqual(3.0, characteristic.values[2.0][3.0])
        self.assertEqual(2.0, characteristic.values[2.0][4.0])
        self.assertEqual(3.0, characteristic.values[2.0][5.0])
        self.assertEqual(4.0, characteristic.values[2.0][6.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("DISTRIBUTION Y", characteristic.y_mapping)
        self.assertEqual("Sample comment", characteristic.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_characteristic_maps()))

        self.assertEqual("characteristicMap", characteristicWritten.name)
        self.assertEqual("Sample characteristic map", characteristicWritten.attrs["description"])
        self.assertEqual("CharacteristicMapFunction", characteristicWritten.attrs["function"])
        self.assertEqual("CharacteristicMapDisplayname", characteristicWritten.attrs["display_name"])
        self.assertEqual("bar", characteristicWritten.unit_values)
        self.assertEqual("°C", characteristicWritten.attrs["units_x"])
        self.assertEqual("m/s", characteristicWritten.attrs["units_y"])
        self.assertEqual(0.0, characteristicWritten.values[1.0][1.0])
        self.assertEqual(0.4, characteristicWritten.values[1.0][2.0])
        self.assertEqual(0.8, characteristicWritten.values[1.0][3.0])
        self.assertEqual(1.0, characteristicWritten.values[1.0][4.0])
        self.assertEqual(1.4, characteristicWritten.values[1.0][5.0])
        self.assertEqual(1.8, characteristicWritten.values[1.0][6.0])
        self.assertEqual(1.0, characteristicWritten.values[2.0][1.0])
        self.assertEqual(2.0, characteristicWritten.values[2.0][2.0])
        self.assertEqual(3.0, characteristicWritten.values[2.0][3.0])
        self.assertEqual(2.0, characteristicWritten.values[2.0][4.0])
        self.assertEqual(3.0, characteristicWritten.values[2.0][5.0])
        self.assertEqual(4.0, characteristicWritten.values[2.0][6.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("DISTRIBUTION Y", characteristicWritten.y_mapping)
        self.assertEqual("Sample comment", characteristicWritten.attrs["comment"])

    def test_fixedCharacteristicMap(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_fixed_characteristic_maps()[0]
        characteristicWritten = dcmWritten.get_fixed_characteristic_maps()[0]

        self.assertEqual(1, len(dcm.get_fixed_characteristic_maps()))

        self.assertEqual("fixedCharacteristicMap", characteristic.name)
        self.assertEqual("Sample fixed characteristic map", characteristic.attrs["description"])
        self.assertEqual("FixedCharacteristicMapFunction", characteristic.attrs["function"])
        self.assertEqual("FixedCharacteristicMapDisplayname", characteristic.attrs["display_name"])
        self.assertEqual("bar", characteristic.unit_values)
        self.assertEqual("°C", characteristic.attrs["units_x"])
        self.assertEqual("m/s", characteristic.attrs["units_y"])
        self.assertEqual(0.0, characteristic.values[0.0][1.0])
        self.assertEqual(0.4, characteristic.values[0.0][2.0])
        self.assertEqual(0.8, characteristic.values[0.0][3.0])
        self.assertEqual(1.0, characteristic.values[0.0][4.0])
        self.assertEqual(1.4, characteristic.values[0.0][5.0])
        self.assertEqual(1.8, characteristic.values[0.0][6.0])
        self.assertEqual(1.0, characteristic.values[1.0][1.0])
        self.assertEqual(2.0, characteristic.values[1.0][2.0])
        self.assertEqual(3.0, characteristic.values[1.0][3.0])
        self.assertEqual(2.0, characteristic.values[1.0][4.0])
        self.assertEqual(3.0, characteristic.values[1.0][5.0])
        self.assertEqual(4.0, characteristic.values[1.0][6.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("DISTRIBUTION Y", characteristic.y_mapping)
        self.assertEqual("Sample comment", characteristic.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_fixed_characteristic_maps()))

        self.assertEqual("fixedCharacteristicMap", characteristicWritten.name)
        self.assertEqual("Sample fixed characteristic map", characteristicWritten.attrs["description"])
        self.assertEqual("FixedCharacteristicMapFunction", characteristicWritten.attrs["function"])
        self.assertEqual("FixedCharacteristicMapDisplayname", characteristicWritten.attrs["display_name"])
        self.assertEqual("bar", characteristicWritten.unit_values)
        self.assertEqual("°C", characteristicWritten.attrs["units_x"])
        self.assertEqual("m/s", characteristicWritten.attrs["units_y"])
        self.assertEqual(0.0, characteristicWritten.values[0.0][1.0])
        self.assertEqual(0.4, characteristicWritten.values[0.0][2.0])
        self.assertEqual(0.8, characteristicWritten.values[0.0][3.0])
        self.assertEqual(1.0, characteristicWritten.values[0.0][4.0])
        self.assertEqual(1.4, characteristicWritten.values[0.0][5.0])
        self.assertEqual(1.8, characteristicWritten.values[0.0][6.0])
        self.assertEqual(1.0, characteristicWritten.values[1.0][1.0])
        self.assertEqual(2.0, characteristicWritten.values[1.0][2.0])
        self.assertEqual(3.0, characteristicWritten.values[1.0][3.0])
        self.assertEqual(2.0, characteristicWritten.values[1.0][4.0])
        self.assertEqual(3.0, characteristicWritten.values[1.0][5.0])
        self.assertEqual(4.0, characteristicWritten.values[1.0][6.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("DISTRIBUTION Y", characteristicWritten.y_mapping)
        self.assertEqual("Sample comment", characteristicWritten.attrs["comment"])

    def test_groupCharacteristicMap(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_group_characteristic_maps()[0]
        characteristicWritten = dcmWritten.get_group_characteristic_maps()[0]

        self.assertEqual(1, len(dcm.get_group_characteristic_maps()))

        self.assertEqual("groupCharacteristicMap", characteristic.name)
        self.assertEqual("Sample group characteristic map", characteristic.attrs["description"])
        self.assertEqual("GroupCharacteristicMapFunction", characteristic.attrs["function"])
        self.assertEqual("GroupCharacteristicMapDisplayname", characteristic.attrs["display_name"])
        self.assertEqual("bar", characteristic.unit_values)
        self.assertEqual("°C", characteristic.attrs["units_x"])
        self.assertEqual("m/s", characteristic.attrs["units_y"])
        self.assertEqual(1.0, characteristic.values[1.0][1.0])
        self.assertEqual(2.0, characteristic.values[1.0][2.0])
        self.assertEqual(3.0, characteristic.values[1.0][3.0])
        self.assertEqual(2.0, characteristic.values[1.0][4.0])
        self.assertEqual(3.0, characteristic.values[1.0][5.0])
        self.assertEqual(4.0, characteristic.values[1.0][6.0])
        self.assertEqual(2.0, characteristic.values[2.0][1.0])
        self.assertEqual(4.0, characteristic.values[2.0][2.0])
        self.assertEqual(6.0, characteristic.values[2.0][3.0])
        self.assertEqual(3.0, characteristic.values[2.0][4.0])
        self.assertEqual(4.0, characteristic.values[2.0][5.0])
        self.assertEqual(5.0, characteristic.values[2.0][6.0])
        self.assertEqual(3.0, characteristic.values[3.0][1.0])
        self.assertEqual(6.0, characteristic.values[3.0][2.0])
        self.assertEqual(9.0, characteristic.values[3.0][3.0])
        self.assertEqual(7.0, characteristic.values[3.0][4.0])
        self.assertEqual(8.0, characteristic.values[3.0][5.0])
        self.assertEqual(9.0, characteristic.values[3.0][6.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("DISTRIBUTION Y", characteristic.y_mapping)
        self.assertEqual("Sample comment", characteristic.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_group_characteristic_maps()))

        self.assertEqual("groupCharacteristicMap", characteristicWritten.name)
        self.assertEqual("Sample group characteristic map", characteristicWritten.attrs["description"])
        self.assertEqual("GroupCharacteristicMapFunction", characteristicWritten.attrs["function"])
        self.assertEqual("GroupCharacteristicMapDisplayname", characteristicWritten.attrs["display_name"])
        self.assertEqual("bar", characteristicWritten.unit_values)
        self.assertEqual("°C", characteristicWritten.attrs["units_x"])
        self.assertEqual("m/s", characteristicWritten.attrs["units_y"])
        self.assertEqual(1.0, characteristicWritten.values[1.0][1.0])
        self.assertEqual(2.0, characteristicWritten.values[1.0][2.0])
        self.assertEqual(3.0, characteristicWritten.values[1.0][3.0])
        self.assertEqual(2.0, characteristicWritten.values[1.0][4.0])
        self.assertEqual(3.0, characteristicWritten.values[1.0][5.0])
        self.assertEqual(4.0, characteristicWritten.values[1.0][6.0])
        self.assertEqual(2.0, characteristicWritten.values[2.0][1.0])
        self.assertEqual(4.0, characteristicWritten.values[2.0][2.0])
        self.assertEqual(6.0, characteristicWritten.values[2.0][3.0])
        self.assertEqual(3.0, characteristicWritten.values[2.0][4.0])
        self.assertEqual(4.0, characteristicWritten.values[2.0][5.0])
        self.assertEqual(5.0, characteristicWritten.values[2.0][6.0])
        self.assertEqual(3.0, characteristicWritten.values[3.0][1.0])
        self.assertEqual(6.0, characteristicWritten.values[3.0][2.0])
        self.assertEqual(9.0, characteristicWritten.values[3.0][3.0])
        self.assertEqual(7.0, characteristicWritten.values[3.0][4.0])
        self.assertEqual(8.0, characteristicWritten.values[3.0][5.0])
        self.assertEqual(9.0, characteristicWritten.values[3.0][6.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("DISTRIBUTION Y", characteristicWritten.y_mapping)
        self.assertEqual("Sample comment", characteristicWritten.attrs["comment"])


class TestDistribution(unittest.TestCase):
    def test_distribution(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        distribution = dcm.get_distributions()[0]
        distributionWritten = dcmWritten.get_distributions()[0]

        self.assertEqual(1, len(dcm.get_distributions()))

        self.assertEqual("distrib", distribution.name)
        self.assertEqual("Sample distribution", distribution.attrs["description"])
        self.assertEqual("DistributionFunction", distribution.attrs["function"])
        self.assertEqual("DistributionDisplayname", distribution.attrs["display_name"])
        self.assertEqual("mm", distribution.attrs["units_x"])
        self.assertEqual(1.0, distribution.values[0])
        self.assertEqual(2.0, distribution.values[1])
        self.assertEqual(3.0, distribution.values[2])
        self.assertEqual("SST", distribution.attrs["comment"])

        self.assertEqual(1, len(dcmWritten.get_distributions()))

        self.assertEqual("distrib", distributionWritten.name)
        self.assertEqual("Sample distribution", distributionWritten.attrs["description"])
        self.assertEqual("DistributionFunction", distributionWritten.attrs["function"])
        self.assertEqual("DistributionDisplayname", distributionWritten.attrs["display_name"])
        self.assertEqual("mm", distributionWritten.attrs["units_x"])
        self.assertEqual(1.0, distributionWritten.values[0])
        self.assertEqual(2.0, distributionWritten.values[1])
        self.assertEqual(3.0, distributionWritten.values[2])
        self.assertEqual("SST", distributionWritten.attrs["comment"])


if __name__ == "__main__":
    unittest.main()
