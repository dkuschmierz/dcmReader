import os
import sys
import unittest

testdir = os.path.dirname(__file__)
srcdir = "../src"
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import dcmReader


class TestFunctions(unittest.TestCase):
    def test_functionParsing(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        self.assertEqual(9, len(dcm.getFunctions()))


class TestParameters(unittest.TestCase):
    def test_foundParameter(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        self.assertEqual(2, len(dcm.getParameters()))

    def test_valueParameter(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        valueParameter = dcm.getParameters()[0]

        self.assertEqual("valueParameter", valueParameter.name)
        self.assertEqual("Sample value parameter", valueParameter.description)
        self.assertEqual("ParameterFunction", valueParameter.function)
        self.assertEqual("°C", valueParameter.unit)
        self.assertEqual(25.0, valueParameter.value)
        self.assertEqual(27.5, valueParameter.variants["VariantA"])
        self.assertEqual(None, valueParameter.text)

    def test_textParameter(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        valueParameter = dcm.getParameters()[1]

        self.assertEqual("textParameter", valueParameter.name)
        self.assertEqual("Sample text parameter", valueParameter.description)
        self.assertEqual("ParameterFunction", valueParameter.function)
        self.assertEqual("-", valueParameter.unit)
        self.assertEqual(None, valueParameter.value)
        self.assertEqual("ParameterB", valueParameter.variants["VariantA"])
        self.assertEqual("ParameterA", valueParameter.text)


class TestParameterBlock(unittest.TestCase):
    def test_blockParameter1D(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        blockParameter = dcm.getBlockParameters()[0]

        self.assertEqual("blockParameter1D", blockParameter.name)
        self.assertEqual("Sample block parameters", blockParameter.description)
        self.assertEqual("BlockParameterFunction", blockParameter.function)
        self.assertEqual("BlockParameterDisplayname", blockParameter.displayName)
        self.assertEqual("°C", blockParameter.unit)
        self.assertEqual(0.75, blockParameter.values[0][0])
        self.assertEqual(-0.25, blockParameter.values[0][1])
        self.assertEqual(0.5, blockParameter.values[0][2])
        self.assertEqual(1.5, blockParameter.values[0][3])

    def test_blockParameter2D(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        blockParameter = dcm.getBlockParameters()[1]

        self.assertEqual("blockParameter2D", blockParameter.name)
        self.assertEqual("Sample block parameters", blockParameter.description)
        self.assertEqual("BlockParameterFunction", blockParameter.function)
        self.assertEqual("BlockParameterDisplayname", blockParameter.displayName)
        self.assertEqual("°C", blockParameter.unit)
        self.assertEqual(0.75, blockParameter.values[0][0])
        self.assertEqual(-0.25, blockParameter.values[0][1])
        self.assertEqual(0.5, blockParameter.values[0][2])
        self.assertEqual(1.5, blockParameter.values[0][3])
        self.assertEqual(10.75, blockParameter.values[1][0])
        self.assertEqual(-10.25, blockParameter.values[1][1])
        self.assertEqual(10.5, blockParameter.values[1][2])
        self.assertEqual(11.5, blockParameter.values[1][3])


class TestCharacteristicLines(unittest.TestCase):
    def test_characteristicLine(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        characteristic = dcm.getCharacteristicLines()[0]

        self.assertEqual(1, len(dcm.getCharacteristicLines()))

        self.assertEqual("characteristicLine", characteristic.name)
        self.assertEqual("Sample characteristic line", characteristic.description)
        self.assertEqual("CharacteristicLineFunction", characteristic.function)
        self.assertEqual("CharacteristicLineDisplayname", characteristic.displayName)
        self.assertEqual("°", characteristic.unitValues)
        self.assertEqual("s", characteristic.unitX)
        self.assertEqual(0.0, characteristic.values[0.0])
        self.assertEqual(80.0, characteristic.values[1.0])
        self.assertEqual(120.0, characteristic.values[2.0])
        self.assertEqual(180.0, characteristic.values[3.0])
        self.assertEqual(220.0, characteristic.values[4.0])
        self.assertEqual(260.0, characteristic.values[5.0])
        self.assertEqual(300.0, characteristic.values[6.0])
        self.assertEqual(340.0, characteristic.values[7.0])

    def test_fixedCharacteristicLine(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        characteristic = dcm.getFixedCharacteristicLines()[0]

        self.assertEqual(1, len(dcm.getFixedCharacteristicLines()))

        self.assertEqual("fixedCharacteristicLine", characteristic.name)
        self.assertEqual("Sample fixed characteristic line", characteristic.description)
        self.assertEqual("FixedCharacteristicLineFunction", characteristic.function)
        self.assertEqual(
            "FixedCharacteristicLineDisplayname", characteristic.displayName
        )
        self.assertEqual("°", characteristic.unitValues)
        self.assertEqual("s", characteristic.unitX)
        self.assertEqual(45.0, characteristic.values[0.0])
        self.assertEqual(90.0, characteristic.values[1.0])
        self.assertEqual(135.0, characteristic.values[2.0])
        self.assertEqual(180.0, characteristic.values[3.0])
        self.assertEqual(225.0, characteristic.values[4.0])
        self.assertEqual(270.0, characteristic.values[5.0])

    def test_groupCharacteristicLine(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        characteristic = dcm.getGroupCharacteristicLines()[0]

        self.assertEqual(1, len(dcm.getGroupCharacteristicLines()))

        self.assertEqual("groupCharacteristicLine", characteristic.name)
        self.assertEqual("Sample group characteristic line", characteristic.description)
        self.assertEqual("GroupCharacteristicLineFunction", characteristic.function)
        self.assertEqual(
            "GroupCharacteristicLineDisplayname", characteristic.displayName
        )
        self.assertEqual("°", characteristic.unitValues)
        self.assertEqual("s", characteristic.unitX)
        self.assertEqual(-45.0, characteristic.values[1.0])
        self.assertEqual(-90.0, characteristic.values[2.0])
        self.assertEqual(-135.0, characteristic.values[3.0])


class TestCharacteristicMaps(unittest.TestCase):
    def test_characteristicMap(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        characteristic = dcm.getCharacteristicMaps()[0]
        print(characteristic)
        self.assertEqual(1, len(dcm.getCharacteristicMaps()))

        self.assertEqual("characteristicMap", characteristic.name)
        self.assertEqual("Sample characteristic map", characteristic.description)
        self.assertEqual("CharacteristicMapFunction", characteristic.function)
        self.assertEqual("CharacteristicMapDisplayname", characteristic.displayName)
        self.assertEqual("bar", characteristic.unitValues)
        self.assertEqual("°C", characteristic.unitX)
        self.assertEqual("m/s", characteristic.unitY)
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

    def test_fixedCharacteristicMap(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        characteristic = dcm.getFixedCharacteristicMaps()[0]

        self.assertEqual(1, len(dcm.getFixedCharacteristicMaps()))

        self.assertEqual("fixedCharacteristicMap", characteristic.name)
        self.assertEqual("Sample fixed characteristic map", characteristic.description)
        self.assertEqual("FixedCharacteristicMapFunction", characteristic.function)
        self.assertEqual(
            "FixedCharacteristicMapDisplayname", characteristic.displayName
        )
        self.assertEqual("bar", characteristic.unitValues)
        self.assertEqual("°C", characteristic.unitX)
        self.assertEqual("m/s", characteristic.unitY)
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

    def test_groupCharacteristicMap(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        characteristic = dcm.getGroupCharacteristicMaps()[0]

        self.assertEqual(1, len(dcm.getGroupCharacteristicMaps()))

        self.assertEqual("groupCharacteristicMap", characteristic.name)
        self.assertEqual("Sample group characteristic map", characteristic.description)
        self.assertEqual("GroupCharacteristicMapFunction", characteristic.function)
        self.assertEqual(
            "GroupCharacteristicMapDisplayname", characteristic.displayName
        )
        self.assertEqual("bar", characteristic.unitValues)
        self.assertEqual("°C", characteristic.unitX)
        self.assertEqual("m/s", characteristic.unitY)
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


class TestDistribution(unittest.TestCase):
    def test_distribution(self):
        dcm = dcmReader.DcmReader()
        dcm.read("./Sample.dcm")
        distribution = dcm.getDistributions()[0]

        self.assertEqual(1, len(dcm.getDistributions()))

        self.assertEqual("distrib", distribution.name)
        self.assertEqual("Sample distribution", distribution.description)
        self.assertEqual("DistributionFunction", distribution.function)
        self.assertEqual("DistributionDisplayname", distribution.displayName)
        self.assertEqual("mm", distribution.unitX)
        self.assertEqual(1.0, distribution.values[0])
        self.assertEqual(2.0, distribution.values[1])
        self.assertEqual(3.0, distribution.values[2])


if __name__ == "__main__":
    unittest.main()
