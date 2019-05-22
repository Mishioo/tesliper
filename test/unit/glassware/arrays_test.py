import unittest as ut
from unittest import mock
import tesliper.glassware.arrays as ar
import numpy as np


class TestFloatArray(ut.TestCase):

    def test_dtype(self):
        self.arr = ar.FloatArray(
            genre='bla', filenames=['f1', 'f2', 'f3'], values=[3, 12, 15]
        )
        self.assertEqual(self.arr.values.dtype, np.float)


@mock.patch(
    'tesliper.glassware.array_base.ArrayBase.get_args',
    return_value={
        'genre': 'bla', 'filenames': ['f1', 'f2', 'f3'],
        'values': [3, 12, 15], 'allow_data_inconsistency': False
    }
)
@mock.patch('tesliper.datawork.calculate_average', return_value=10)
@mock.patch('tesliper.glassware.arrays.logger')
class TestFloatArrayAverageConformers(ut.TestCase):

    def setUp(self):
        self.arr = ar.FloatArray(
            genre='bla', filenames=['f1', 'f2', 'f3'], values=[3, 12, 15]
        )

    def test_average_conformers_energies_object(self, lggr, clav, args):
        en = mock.Mock(genre='foo', populations=[1, 1, 1])
        out = self.arr.average_conformers(en)
        self.assertIs(type(out), ar.FloatArray)
        self.assertSequenceEqual(out.values.tolist(), [10])
        self.assertSequenceEqual(
            clav.call_args[0][0].tolist(), [3, 12, 15]
        )
        self.assertSequenceEqual(clav.call_args[0][1], [1, 1, 1])
        args.assert_called()
        lggr.debug.assert_called_with('bla averaged by foo.')

    def test_average_conformers_list(self, lggr, clav, args):
        out = self.arr.average_conformers([1, 1, 1])
        self.assertIs(type(out), ar.FloatArray)
        self.assertSequenceEqual(out.values.tolist(), [10])
        self.assertSequenceEqual(
            clav.call_args[0][0].tolist(), [3, 12, 15]
        )
        self.assertSequenceEqual(
            clav.call_args[0][1].tolist(), [1, 1, 1]
        )
        args.assert_called()
        lggr.debug.assert_called_with('bla averaged by unknown.')


@mock.patch(
    'tesliper.glassware.arrays.Energies.values',
    new_callable=mock.PropertyMock, return_value=[3, 12, 15]
)
@mock.patch(
    'tesliper.glassware.arrays.Energies.filenames',
    new_callable=mock.PropertyMock, return_value=['f1', 'f2', 'f3']
)
class TestEnergies(ut.TestCase):

    def setUp(self):
        self.en = ar.Energies(
            genre='bla', filenames=['f1', 'f2', 'f3'], values=[3, 12, 15], t=10
        )

    @mock.patch('tesliper.glassware.arrays.dw.calculate_deltas')
    def test_deltas(self, deltas, fnms, vals):
        out = self.en.deltas
        vals.assert_called()
        deltas.assert_called_with(self.en.values)

    @mock.patch('tesliper.glassware.arrays.dw.calculate_min_factors')
    def test_min_factors(self, factors, fnms, vals):
        out = self.en.min_factors
        vals.assert_called()
        factors.assert_called_with(self.en.values, self.en.t)

    @mock.patch('tesliper.glassware.arrays.dw.calculate_populations')
    def test_populations(self, populs, fnms, vals):
        out = self.en.populations
        vals.assert_called()
        populs.assert_called_with(self.en.values, self.en.t)

    @mock.patch('tesliper.glassware.arrays.dw.calculate_populations')
    def test_calculate_populations(self, populs, fnms, vals):
        out = self.en.calculate_populations(20)
        vals.assert_called()
        populs.assert_called_with(self.en.values, 20)

