import os
import sys
import unittest

testdir = os.path.dirname(__file__)
srcdir = "../src"
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

from dcmReader.dcm_reader import (
    DcmCharacteristicLine,
    DcmCharacteristicMap,
    DcmReader,
    DcmParameter,
    DcmParameterBlock,
)


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
        self.assertEqual("Sample value parameter", valueParameter.description)
        self.assertEqual("ParameterFunction", valueParameter.function)
        self.assertEqual("°C", valueParameter.unit)
        self.assertEqual(25.0, valueParameter.value)
        self.assertEqual(27.5, valueParameter.variants["VariantA"])
        self.assertEqual(None, valueParameter.text)
        self.assertEqual("Sample comment\nSecond comment line\n", valueParameter.comment)

    def test_textParameter(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        valueParameter = dcm.get_parameters()[1]

        self.assertEqual("textParameter", valueParameter.name)
        self.assertEqual("Sample text parameter", valueParameter.description)
        self.assertEqual("ParameterFunction", valueParameter.function)
        self.assertEqual("-", valueParameter.unit)
        self.assertEqual(None, valueParameter.value)
        self.assertEqual("ParameterB", valueParameter.variants["VariantA"])
        self.assertEqual("ParameterA", valueParameter.text)

    def test_ordering_parameter_with_only_name(self):
        p1 = DcmParameter("p1")
        p2 = DcmParameter("p2")
        assert p1 < p2, 'Expecting lexicographic ordering based on names'

class TestParameterBlock(unittest.TestCase):
    def test_blockParameter1D(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        blockParameter = dcm.get_block_parameters()[0]
        blockParameterWritten = dcmWritten.get_block_parameters()[0]

        self.assertEqual("blockParameter1D", blockParameter.name)
        self.assertEqual("Sample block parameters", blockParameter.description)
        self.assertEqual("BlockParameterFunction", blockParameter.function)
        self.assertEqual("BlockParameterDisplayname", blockParameter.display_name)
        self.assertEqual("°C", blockParameter.unit)
        self.assertEqual(0.75, blockParameter.values[0][0])
        self.assertEqual(-0.25, blockParameter.values[0][1])
        self.assertEqual(0.5, blockParameter.values[0][2])
        self.assertEqual(1.5, blockParameter.values[0][3])
        self.assertEqual("Sample comment\n", blockParameter.comment)

        self.assertEqual("blockParameter1D", blockParameterWritten.name)
        self.assertEqual("Sample block parameters", blockParameterWritten.description)
        self.assertEqual("BlockParameterFunction", blockParameterWritten.function)
        self.assertEqual("BlockParameterDisplayname", blockParameterWritten.display_name)
        self.assertEqual("°C", blockParameterWritten.unit)
        self.assertEqual(0.75, blockParameterWritten.values[0][0])
        self.assertEqual(-0.25, blockParameterWritten.values[0][1])
        self.assertEqual(0.5, blockParameterWritten.values[0][2])
        self.assertEqual(1.5, blockParameterWritten.values[0][3])
        self.assertEqual("Sample comment\n", blockParameterWritten.comment)

    def test_blockParameter2D(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        blockParameter = dcm.get_block_parameters()[1]
        blockParameterWritten = dcmWritten.get_block_parameters()[1]

        self.assertEqual("blockParameter2D", blockParameter.name)
        self.assertEqual("Sample block parameters", blockParameter.description)
        self.assertEqual("BlockParameterFunction", blockParameter.function)
        self.assertEqual("BlockParameterDisplayname", blockParameter.display_name)
        self.assertEqual("°C", blockParameter.unit)
        self.assertEqual(0.75, blockParameter.values[0][0])
        self.assertEqual(-0.25, blockParameter.values[0][1])
        self.assertEqual(0.5, blockParameter.values[0][2])
        self.assertEqual(1.5, blockParameter.values[0][3])
        self.assertEqual(10.75, blockParameter.values[1][0])
        self.assertEqual(-10.25, blockParameter.values[1][1])
        self.assertEqual(10.5, blockParameter.values[1][2])
        self.assertEqual(11.5, blockParameter.values[1][3])

        self.assertEqual("blockParameter2D", blockParameterWritten.name)
        self.assertEqual("Sample block parameters", blockParameterWritten.description)
        self.assertEqual("BlockParameterFunction", blockParameterWritten.function)
        self.assertEqual("BlockParameterDisplayname", blockParameterWritten.display_name)
        self.assertEqual("°C", blockParameterWritten.unit)
        self.assertEqual(0.75, blockParameterWritten.values[0][0])
        self.assertEqual(-0.25, blockParameterWritten.values[0][1])
        self.assertEqual(0.5, blockParameterWritten.values[0][2])
        self.assertEqual(1.5, blockParameterWritten.values[0][3])
        self.assertEqual(10.75, blockParameterWritten.values[1][0])
        self.assertEqual(-10.25, blockParameterWritten.values[1][1])
        self.assertEqual(10.5, blockParameterWritten.values[1][2])
        self.assertEqual(11.5, blockParameterWritten.values[1][3])

    def test_ordering_parameter_block_with_only_name(self):
        p1 = DcmParameterBlock("p1")
        p2 = DcmParameterBlock("p2")
        assert p1 < p2, 'Expecting lexicographic ordering based on names'

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
        self.assertEqual("Sample characteristic line", characteristic.description)
        self.assertEqual("CharacteristicLineFunction", characteristic.function)
        self.assertEqual("CharacteristicLineDisplayname", characteristic.display_name)
        self.assertEqual("°", characteristic.unit_values)
        self.assertEqual("s", characteristic.unit_x)
        self.assertEqual(0.0, characteristic.values[0.0])
        self.assertEqual(80.0, characteristic.values[1.0])
        self.assertEqual(120.0, characteristic.values[2.0])
        self.assertEqual(180.0, characteristic.values[3.0])
        self.assertEqual(220.0, characteristic.values[4.0])
        self.assertEqual(260.0, characteristic.values[5.0])
        self.assertEqual(300.0, characteristic.values[6.0])
        self.assertEqual(340.0, characteristic.values[7.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("Sample comment\n", characteristic.comment)

        self.assertEqual(1, len(dcmWritten.get_characteristic_lines()))

        self.assertEqual("characteristicLine", characteristicWritten.name)
        self.assertEqual("Sample characteristic line", characteristicWritten.description)
        self.assertEqual("CharacteristicLineFunction", characteristicWritten.function)
        self.assertEqual("CharacteristicLineDisplayname", characteristicWritten.display_name)
        self.assertEqual("°", characteristicWritten.unit_values)
        self.assertEqual("s", characteristicWritten.unit_x)
        self.assertEqual(0.0, characteristicWritten.values[0.0])
        self.assertEqual(80.0, characteristicWritten.values[1.0])
        self.assertEqual(120.0, characteristicWritten.values[2.0])
        self.assertEqual(180.0, characteristicWritten.values[3.0])
        self.assertEqual(220.0, characteristicWritten.values[4.0])
        self.assertEqual(260.0, characteristicWritten.values[5.0])
        self.assertEqual(300.0, characteristicWritten.values[6.0])
        self.assertEqual(340.0, characteristicWritten.values[7.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("Sample comment\n", characteristicWritten.comment)

    def test_fixedCharacteristicLine(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_fixed_characteristic_lines()[0]
        characteristicWritten = dcmWritten.get_fixed_characteristic_lines()[0]

        self.assertEqual(1, len(dcm.get_fixed_characteristic_lines()))

        self.assertEqual("fixedCharacteristicLine", characteristic.name)
        self.assertEqual("Sample fixed characteristic line", characteristic.description)
        self.assertEqual("FixedCharacteristicLineFunction", characteristic.function)
        self.assertEqual(
            "FixedCharacteristicLineDisplayname", characteristic.display_name
        )
        self.assertEqual("°", characteristic.unit_values)
        self.assertEqual("s", characteristic.unit_x)
        self.assertEqual(45.0, characteristic.values[0.0])
        self.assertEqual(90.0, characteristic.values[1.0])
        self.assertEqual(135.0, characteristic.values[2.0])
        self.assertEqual(180.0, characteristic.values[3.0])
        self.assertEqual(225.0, characteristic.values[4.0])
        self.assertEqual(270.0, characteristic.values[5.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("Sample comment\n", characteristic.comment)

        self.assertEqual(1, len(dcmWritten.get_fixed_characteristic_lines()))

        self.assertEqual("fixedCharacteristicLine", characteristicWritten.name)
        self.assertEqual("Sample fixed characteristic line", characteristicWritten.description)
        self.assertEqual("FixedCharacteristicLineFunction", characteristicWritten.function)
        self.assertEqual(
            "FixedCharacteristicLineDisplayname", characteristicWritten.display_name
        )
        self.assertEqual("°", characteristicWritten.unit_values)
        self.assertEqual("s", characteristicWritten.unit_x)
        self.assertEqual(45.0, characteristicWritten.values[0.0])
        self.assertEqual(90.0, characteristicWritten.values[1.0])
        self.assertEqual(135.0, characteristicWritten.values[2.0])
        self.assertEqual(180.0, characteristicWritten.values[3.0])
        self.assertEqual(225.0, characteristicWritten.values[4.0])
        self.assertEqual(270.0, characteristicWritten.values[5.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("Sample comment\n", characteristicWritten.comment)

    def test_groupCharacteristicLine(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_group_characteristic_lines()[0]
        characteristicWritten = dcmWritten.get_group_characteristic_lines()[0]

        self.assertEqual(1, len(dcm.get_group_characteristic_lines()))

        self.assertEqual("groupCharacteristicLine", characteristic.name)
        self.assertEqual("Sample group characteristic line", characteristic.description)
        self.assertEqual("GroupCharacteristicLineFunction", characteristic.function)
        self.assertEqual(
            "GroupCharacteristicLineDisplayname", characteristic.display_name
        )
        self.assertEqual("°", characteristic.unit_values)
        self.assertEqual("s", characteristic.unit_x)
        self.assertEqual(-45.0, characteristic.values[1.0])
        self.assertEqual(-90.0, characteristic.values[2.0])
        self.assertEqual(-135.0, characteristic.values[3.0])
        self.assertEqual("DISTRIBUTION X", characteristic.x_mapping)
        self.assertEqual("Sample comment\n", characteristic.comment)

        self.assertEqual(1, len(dcmWritten.get_group_characteristic_lines()))

        self.assertEqual("groupCharacteristicLine", characteristicWritten.name)
        self.assertEqual("Sample group characteristic line", characteristicWritten.description)
        self.assertEqual("GroupCharacteristicLineFunction", characteristicWritten.function)
        self.assertEqual(
            "GroupCharacteristicLineDisplayname", characteristicWritten.display_name
        )
        self.assertEqual("°", characteristicWritten.unit_values)
        self.assertEqual("s", characteristicWritten.unit_x)
        self.assertEqual(-45.0, characteristicWritten.values[1.0])
        self.assertEqual(-90.0, characteristicWritten.values[2.0])
        self.assertEqual(-135.0, characteristicWritten.values[3.0])
        self.assertEqual("DISTRIBUTION X", characteristicWritten.x_mapping)
        self.assertEqual("Sample comment\n", characteristicWritten.comment)

    def test_ordering_characteristic_line_with_only_name(self):
        cl1 = DcmCharacteristicLine("cl1")
        cl2 = DcmCharacteristicLine("cl2")
        assert cl1 < cl2, 'Expecting lexicographic ordering based on names'

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
        self.assertEqual("Sample characteristic map", characteristic.description)
        self.assertEqual("CharacteristicMapFunction", characteristic.function)
        self.assertEqual("CharacteristicMapDisplayname", characteristic.display_name)
        self.assertEqual("bar", characteristic.unit_values)
        self.assertEqual("°C", characteristic.unit_x)
        self.assertEqual("m/s", characteristic.unit_y)
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
        self.assertEqual("Sample comment\n", characteristic.comment)

        self.assertEqual(1, len(dcmWritten.get_characteristic_maps()))

        self.assertEqual("characteristicMap", characteristicWritten.name)
        self.assertEqual("Sample characteristic map", characteristicWritten.description)
        self.assertEqual("CharacteristicMapFunction", characteristicWritten.function)
        self.assertEqual("CharacteristicMapDisplayname", characteristicWritten.display_name)
        self.assertEqual("bar", characteristicWritten.unit_values)
        self.assertEqual("°C", characteristicWritten.unit_x)
        self.assertEqual("m/s", characteristicWritten.unit_y)
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
        self.assertEqual("Sample comment\n", characteristicWritten.comment)

    def test_fixedCharacteristicMap(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_fixed_characteristic_maps()[0]
        characteristicWritten = dcmWritten.get_fixed_characteristic_maps()[0]

        self.assertEqual(1, len(dcm.get_fixed_characteristic_maps()))

        self.assertEqual("fixedCharacteristicMap", characteristic.name)
        self.assertEqual("Sample fixed characteristic map", characteristic.description)
        self.assertEqual("FixedCharacteristicMapFunction", characteristic.function)
        self.assertEqual(
            "FixedCharacteristicMapDisplayname", characteristic.display_name
        )
        self.assertEqual("bar", characteristic.unit_values)
        self.assertEqual("°C", characteristic.unit_x)
        self.assertEqual("m/s", characteristic.unit_y)
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
        self.assertEqual("Sample comment\n", characteristic.comment)

        self.assertEqual(1, len(dcmWritten.get_fixed_characteristic_maps()))

        self.assertEqual("fixedCharacteristicMap", characteristicWritten.name)
        self.assertEqual("Sample fixed characteristic map", characteristicWritten.description)
        self.assertEqual("FixedCharacteristicMapFunction", characteristicWritten.function)
        self.assertEqual(
            "FixedCharacteristicMapDisplayname", characteristicWritten.display_name
        )
        self.assertEqual("bar", characteristicWritten.unit_values)
        self.assertEqual("°C", characteristicWritten.unit_x)
        self.assertEqual("m/s", characteristicWritten.unit_y)
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
        self.assertEqual("Sample comment\n", characteristicWritten.comment)

    def test_groupCharacteristicMap(self):
        dcm = DcmReader()
        dcmWritten = DcmReader()
        dcm.read("./Sample.dcm")
        dcmWritten.read("./Sample_written.dcm")
        characteristic = dcm.get_group_characteristic_maps()[0]
        characteristicWritten = dcmWritten.get_group_characteristic_maps()[0]

        self.assertEqual(1, len(dcm.get_group_characteristic_maps()))

        self.assertEqual("groupCharacteristicMap", characteristic.name)
        self.assertEqual("Sample group characteristic map", characteristic.description)
        self.assertEqual("GroupCharacteristicMapFunction", characteristic.function)
        self.assertEqual(
            "GroupCharacteristicMapDisplayname", characteristic.display_name
        )
        self.assertEqual("bar", characteristic.unit_values)
        self.assertEqual("°C", characteristic.unit_x)
        self.assertEqual("m/s", characteristic.unit_y)
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
        self.assertEqual("Sample comment\n", characteristic.comment)

        self.assertEqual(1, len(dcmWritten.get_group_characteristic_maps()))

        self.assertEqual("groupCharacteristicMap", characteristicWritten.name)
        self.assertEqual("Sample group characteristic map", characteristicWritten.description)
        self.assertEqual("GroupCharacteristicMapFunction", characteristicWritten.function)
        self.assertEqual(
            "GroupCharacteristicMapDisplayname", characteristicWritten.display_name
        )
        self.assertEqual("bar", characteristicWritten.unit_values)
        self.assertEqual("°C", characteristicWritten.unit_x)
        self.assertEqual("m/s", characteristicWritten.unit_y)
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
        self.assertEqual("Sample comment\n", characteristicWritten.comment)

    def test_ordering_characteristic_line_with_only_name(self):
        cm1 = DcmCharacteristicMap("cm1")
        cm2 = DcmCharacteristicMap("cm2")
        assert cm1 < cm2, 'Expecting lexicographic ordering based on names'

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
        self.assertEqual("Sample distribution", distribution.description)
        self.assertEqual("DistributionFunction", distribution.function)
        self.assertEqual("DistributionDisplayname", distribution.display_name)
        self.assertEqual("mm", distribution.unit_x)
        self.assertEqual(1.0, distribution.values[0])
        self.assertEqual(2.0, distribution.values[1])
        self.assertEqual(3.0, distribution.values[2])
        self.assertEqual("SST\n", distribution.comment)

        self.assertEqual(1, len(dcmWritten.get_distributions()))

        self.assertEqual("distrib", distributionWritten.name)
        self.assertEqual("Sample distribution", distributionWritten.description)
        self.assertEqual("DistributionFunction", distributionWritten.function)
        self.assertEqual("DistributionDisplayname", distributionWritten.display_name)
        self.assertEqual("mm", distributionWritten.unit_x)
        self.assertEqual(1.0, distributionWritten.values[0])
        self.assertEqual(2.0, distributionWritten.values[1])
        self.assertEqual(3.0, distributionWritten.values[2])
        self.assertEqual("SST\n", distributionWritten.comment)


if __name__ == "__main__":
    unittest.main()
