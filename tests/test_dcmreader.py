import os
import sys
import unittest
import pytest

import numpy as np

from dcmReader.dcm_reader import DcmReader


testdir = os.path.dirname(__file__)
srcdir = "../src"
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))


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


@pytest.mark.parametrize("path", [r"./Sample.dcm", r"./Sample_written.dcm"])
@pytest.mark.parametrize(
    "name, attrs, values, coords",
    [
        (
            "valueParameter",
            {
                "comment": "Sample comment\nSecond comment line",
                "description": "Sample value parameter",
                "function": "ParameterFunction",
                "display_name": "ParameterDisplayname",
                "units": "°C",
                "variants": {"VariantA": 27.5},
            },
            np.array(25.0),
            (),
        ),
        (
            "textParameter",
            {
                "description": "Sample text parameter",
                "function": "ParameterFunction",
                "display_name": "ParameterDisplayname",
                "units": "-",
                "variants": {"VariantA": "ParameterB"},
            },
            np.array("ParameterA", dtype=np.dtype("<U32")),
            (),
        ),
        (
            "blockParameter1D",
            {
                "comment": "Sample comment",
                "description": "Sample block parameters",
                "function": "BlockParameterFunction",
                "display_name": "BlockParameterDisplayname",
                "units": "°C",
            },
            np.array([0.75, -0.25, 0.5, 1.5]),
            (),
        ),
        (
            "blockParameter2D",
            {
                "description": "Sample block parameters",
                "function": "BlockParameterFunction",
                "display_name": "BlockParameterDisplayname",
                "units": "°C",
            },
            np.array([[0.75, -0.25, 0.5, 1.5], [10.75, -10.25, 10.5, 11.5]]),
            (),
        ),
        (
            "characteristicLine",
            {
                "comment": "Sample comment",
                "description": "Sample characteristic line",
                "function": "CharacteristicLineFunction",
                "display_name": "CharacteristicLineDisplayname",
                "units_x": "s",
                "units": "°",
                "name_x": "DISTRIBUTION X8",
            },
            np.array([0.0, 80.0, 120.0, 180.0, 220.0, 260.0, 300.0, 340.0]),
            (np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]),),
        ),
        (
            "fixedCharacteristicLine",
            {
                "comment": "Sample comment",
                "description": "Sample fixed characteristic line",
                "function": "FixedCharacteristicLineFunction",
                "display_name": "FixedCharacteristicLineDisplayname",
                "units_x": "s",
                "units": "°",
                "name_x": "DISTRIBUTION X6",
            },
            np.array([45.0, 90.0, 135.0, 180.0, 225.0, 270.0]),
            (np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]),),
        ),
        (
            "groupCharacteristicLine",
            {
                "comment": "Sample comment",
                "description": "Sample group characteristic line",
                "function": "GroupCharacteristicLineFunction",
                "display_name": "GroupCharacteristicLineDisplayname",
                "units_x": "s",
                "units": "°",
                "name_x": "DISTRIBUTION X3",
            },
            np.array([-45.0, -90.0, -135.0]),
            (np.array([1.0, 2.0, 3.0]),),
        ),
        (
            "characteristicMap",
            {
                "comment": "Sample comment",
                "description": "Sample characteristic map",
                "function": "CharacteristicMapFunction",
                "display_name": "CharacteristicMapDisplayname",
                "units_x": "°C",
                "units_y": "m/s",
                "units": "bar",
                "name_x": "DISTRIBUTION X6",
                "name_y": "DISTRIBUTION Y2",
            },
            np.array([[0.0, 0.4, 0.8, 1.0, 1.4, 1.8], [1.0, 2.0, 3.0, 2.0, 3.0, 4.0]]),
            (np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])),
        ),
        (
            "fixedCharacteristicMap",
            {
                "comment": "Sample comment",
                "description": "Sample fixed characteristic map",
                "function": "FixedCharacteristicMapFunction",
                "display_name": "FixedCharacteristicMapDisplayname",
                "units_x": "°C",
                "units_y": "m/s",
                "units": "bar",
                "name_x": "DISTRIBUTION X6",
                "name_y": "DISTRIBUTION Y2",
            },
            np.array([[0.0, 0.4, 0.8, 1.0, 1.4, 1.8], [1.0, 2.0, 3.0, 2.0, 3.0, 4.0]]),
            (np.array([0.0, 1.0]), np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])),
        ),
        (
            "groupCharacteristicMap",
            {
                "comment": "Sample comment",
                "description": "Sample group characteristic map",
                "function": "GroupCharacteristicMapFunction",
                "display_name": "GroupCharacteristicMapDisplayname",
                "units_x": "°C",
                "units_y": "m/s",
                "units": "bar",
                "name_x": "DISTRIBUTION X6",
                "name_y": "DISTRIBUTION Y3",
            },
            np.array(
                [
                    [1.0, 2.0, 3.0, 2.0, 3.0, 4.0],
                    [2.0, 4.0, 6.0, 3.0, 4.0, 5.0],
                    [3.0, 6.0, 9.0, 7.0, 8.0, 9.0],
                ]
            ),
            (np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])),
        ),
        (
            "distrib",
            {
                "comment": "SST",
                "description": "Sample distribution",
                "function": "DistributionFunction",
                "display_name": "DistributionDisplayname",
                "units_x": "mm",
                "name_x": "distrib",
            },
            np.array([1.0, 2.0, 3.0]),
            (np.array([1.0, 2.0, 3.0]),),
        ),
    ],
)
def test_elements(
    path: str,
    name: str,
    attrs: dict,
    values: np.typing.ArrayLike,
    coords: tuple[np.typing.ArrayLike, ...],
):
    """
    Test elements.

    Examples
    --------
    >>> # Generate expected results:
    >>> name = "valueParameter"
    >>> x = dcm[name]
    >>> print((x.name, x.attrs, x.values, x.coords))
    """

    def test_element(
        name: str,
        attrs: dict,
        values: np.ndarray,
        coords: tuple[np.ndarray, ...],
        characteristic,
    ) -> None:
        # Check name
        np.testing.assert_array_equal(name, characteristic.name)

        # Check attrs:
        np.testing.assert_array_equal(len(attrs), len(characteristic.attrs))
        for k, expected in attrs.items():
            actual = characteristic.attrs[k]
            np.testing.assert_array_equal(expected, actual)

        # Check values:
        if values.dtype.kind in {"U", "S"}:
            # Strings:
            np.testing.assert_array_equal(values, characteristic.values)
        else:
            # Numbers:
            np.testing.assert_allclose(values, characteristic.values)

        # Check coords:
        np.testing.assert_array_equal(len(coords), len(characteristic.coords))
        [np.testing.assert_allclose(e, a) for e, a in zip(coords, characteristic.coords)]

    dcm = DcmReader()
    dcmWritten = DcmReader()
    # dcm.read("./Sample.dcm")
    # dcmWritten.read("./Sample_written.dcm")

    dcm.read(path)

    characteristic = dcm[name]
    test_element(name, attrs, values, coords, characteristic)

    # characteristicWritten = dcmWritten[name]
    # test_element(name, attrs, values, coords, characteristicWritten)

    # self.assertEqual(1, len(dcm.get_group_characteristic_maps()))
    # np.testing.assert_array_equal(1, len(dcmWritten.get_group_characteristic_maps()))


if __name__ == "__main__":
    # unittest.main()
    pytest.main()
