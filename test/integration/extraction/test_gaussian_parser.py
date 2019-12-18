import os
import unittest
from unittest.mock import Mock, patch
from tesliper.extraction import gaussian_parser as gprs

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class ParserTestCase(unittest.TestCase):
    """This is mix-in class for test cases for gaussian files parsing."""

    # name of gaussian output file in fixtures dir
    file = ""  # molecule is formaldehyde by default

    @classmethod
    def setUpClass(cls):
        if cls is ParserTestCase:
            raise unittest.SkipTest("Base class for gaussian files parser test cases.")
        patchers = []
        parser = gprs.GaussianParser()
        for name in dir(parser):
            method = getattr(parser, name)
            if hasattr(method, "is_state"):
                patcher = patch.object(parser, name, wraps=method)
                mock = patcher.start()
                # need to manually patch the reference in parser.states dictionary
                parser.states[name] = mock
                patchers.append(patcher)
        try:
            cls.parser = parser
            path = os.path.join(THIS_DIR, os.pardir, "fixtures", cls.file)
            with open(path, "r") as file:
                cls.data = parser.parse(file)
        except Exception:
            # import pdb; pdb.set_trace()
            for patcher in patchers:
                patcher.stop()
                parser.states[patcher.attribute] = getattr(parser, patcher.attribute)
            raise

    def test_normal_termination(self):
        self.assertTrue(self.data["normal_termination"])

    def test_version(self):
        self.assertEqual(self.data["version"], "Gaussian 09, Revision E.01")

    def test_charge(self):
        self.assertEqual(self.data["charge"], 0.0)

    def test_multiplicity(self):
        self.assertEqual(self.data["multiplicity"], 1.0)

    def test_stoichiometry(self):
        self.assertEqual(self.data["stoichiometry"], "CH2O")

    def test_atoms(self):
        self.assertSequenceEqual(self.data["molecule_atoms"], [6, 1, 1, 8])


class TestFreq(ParserTestCase):
    file = "fal-freq.out"

    @unittest.skip("Doesn't work as expected, see GaussianParser.optimization")
    def test_methods_called(self):
        self.parser.initial.assert_called()
        self.parser.wait.assert_called()
        self.parser.frequencies.assert_called()
        self.parser.excited.assert_not_called()
        self.parser.optimization.assert_not_called()
        self.parser.geometry.assert_called()

    def test_keys(self):
        self.assertSetEqual(
            set(self.data.keys()),
            {
                "normal_termination",
                "version",
                "command",
                "charge",
                "multiplicity",
                "input_geom",
                "scf",
                "stoichiometry",
                "zpecorr",
                "tencorr",
                "entcorr",
                "gibcorr",
                "zpe",
                "ten",
                "ent",
                "gib",
                "freq",
                "mass",
                "frc",
                "iri",
                "depolarp",
                "depolaru",
                "ramanactiv",
                "geometry",
                "molecule_atoms",
            },
        )

    def test_command(self):
        self.assertEqual(self.data["command"], "freq hf/3-21g")

    def test_scf(self):
        self.assertEqual(self.data["scf"], -113.217409254)

    def test_zpecorr(self):
        self.assertEqual(self.data["zpecorr"], 0.028669)

    def test_tencorr(self):
        self.assertEqual(self.data["tencorr"], 0.031529)

    def test_entcorr(self):
        self.assertEqual(self.data["entcorr"], 0.032474)

    def test_gibcorr(self):
        self.assertEqual(self.data["gibcorr"], 0.006971)

    def test_zpe(self):
        self.assertEqual(self.data["zpe"], -113.188740)

    def test_ten(self):
        self.assertEqual(self.data["ten"], -113.185880)

    def test_ent(self):
        self.assertEqual(self.data["ent"], -113.184936)

    def test_gib(self):
        self.assertEqual(self.data["gib"], -113.210438)

    def test_freq(self):
        self.assertSequenceEqual(
            self.data["freq"],
            [1279.9047, 1337.9260, 1548.4195, 1717.9022, 3288.8988, 3411.2493],
        )

    def test_mass(self):
        self.assertSequenceEqual(
            self.data["mass"], [1.3348, 1.3041, 2.9470, 1.4267, 1.0451, 1.1203]
        )

    def test_frc(self):
        self.assertSequenceEqual(
            self.data["frc"], [1.2883, 1.3753, 4.1630, 2.4808, 6.6606, 7.6808]
        )

    def test_iri(self):
        self.assertSequenceEqual(
            self.data["iri"], [11.0336, 11.8913, 50.4624, 10.5434, 9.5817, 67.3121]
        )

    def test_depolarp(self):
        self.assertSequenceEqual(
            self.data["depolarp"], [0.7500, 0.7499, 0.4706, 0.2785, 0.1912, 0.7500]
        )

    def test_depolaru(self):
        self.assertSequenceEqual(
            self.data["depolaru"], [0.8571, 0.8571, 0.6400, 0.4357, 0.3211, 0.8571]
        )

    def test_ramanactiv(self):
        self.assertSequenceEqual(
            self.data["ramanactiv"],
            [0.0218, 6.0244, 21.4502, 1.3596, 110.6841, 38.7779],
        )

    def test_geometry(self):
        self.assertSequenceEqual(
            self.data["geometry"],
            [
                (0.000199, 0.562211, 0.000000),
                (0.924720, 1.100877, 0.000000),
                (-0.927506, 1.095374, 0.000000),
                (0.000199, -0.696189, 0.000000),
            ],
        )


class TestFreqRoa(ParserTestCase):
    file = "fal-freq-roa.out"

    @unittest.skip("Doesn't work as expected, see GaussianParser.optimization")
    def test_methods_called(self):
        self.parser.initial.assert_called()
        self.parser.wait.assert_called()
        self.parser.frequencies.assert_called()
        self.parser.excited.assert_not_called()
        self.parser.optimization.assert_not_called()
        self.parser.geometry.assert_called()

    def test_keys(self):
        self.assertSetEqual(
            set(self.data.keys()),
            {
                "normal_termination",
                "version",
                "command",
                "charge",
                "multiplicity",
                "input_geom",
                "scf",
                "stoichiometry",
                "geometry",
                "molecule_atoms",
                "zpecorr",
                "tencorr",
                "entcorr",
                "gibcorr",
                "zpe",
                "ten",
                "ent",
                "gib",
                "freq",
                "mass",
                "frc",
                "iri",
                "ramact",
                "depp",
                "depu",
                "alpha2",
                "beta2",
                "alphag",
                "gamma2",
                "delta2",
                "raman1",
                "roa1",
                "cid1",
                "raman2",
                "roa2",
                "cid2",
                "raman3",
                "roa3",
                "cid3",
                "rc180",
            },
        )

    def test_command(self):
        self.assertEqual(self.data["command"], "freq=roa hf/3-21g")

    def test_freq(self):
        self.assertSequenceEqual(
            self.data["freq"],
            [1279.9047, 1337.9260, 1548.4195, 1717.9022, 3288.8988, 3411.2493],
        )

    def test_mass(self):
        self.assertSequenceEqual(
            self.data["mass"], [1.3348, 1.3041, 2.9470, 1.4267, 1.0451, 1.1203]
        )

    def test_frc(self):
        self.assertSequenceEqual(
            self.data["frc"], [1.2883, 1.3753, 4.1630, 2.4808, 6.6606, 7.6808]
        )

    def test_iri(self):
        self.assertSequenceEqual(
            self.data["iri"], [11.0336, 11.8913, 50.4623, 10.5434, 9.5818, 67.3121]
        )

    def test_ramact(self):
        self.assertSequenceEqual(
            self.data["ramact"], [0.0681, 6.1822, 25.3142, 1.4865, 119.9701, 41.7021]
        )

    def test_depp(self):
        self.assertSequenceEqual(
            self.data["depp"], [0.7500, 0.7499, 0.4633, 0.1772, 0.1971, 0.7500]
        )

    def test_depu(self):
        self.assertSequenceEqual(
            self.data["depu"], [0.8571, 0.8571, 0.6332, 0.3010, 0.3293, 0.8571]
        )

    def test_alpha2(self):
        self.assertSequenceEqual(
            self.data["alpha2"], [0.0000, 0.0000, 0.1470, 0.0214, 1.6417, 0.0000]
        )

    def test_beta2(self):
        self.assertSequenceEqual(
            self.data["beta2"], [0.0097, 0.8831, 2.6716, 0.0746, 6.5849, 5.9574]
        )

    def test_alphag(self):
        self.assertSequenceEqual(
            self.data["alphag"], [0.0000, -0.0000, -0.0000, 0.0000, 0.0000, 0.0000]
        )

    def test_gamma2(self):
        self.assertSequenceEqual(
            self.data["gamma2"], [0.0000, -0.0000, -0.0000, 0.0000, 0.0000, 0.0000]
        )

    def test_delta2(self):
        self.assertSequenceEqual(
            self.data["delta2"], [-0.0000, 0.0000, -0.0000, -0.0000, -0.0000, -0.0000]
        )

    def test_raman1(self):
        self.assertSequenceEqual(
            self.data["raman1"], [0.272, 24.729, 101.257, 5.946, 479.880, 166.808]
        )

    def test_roa1(self):
        self.assertSequenceEqual(
            self.data["roa1"], [0.000, -0.000, -0.000, 0.000, 0.000, 0.000]
        )

    def test_cid1(self):
        self.assertSequenceEqual(
            self.data["cid1"], [0.000, -0.000, -0.000, 0.000, 0.000, 0.000]
        )

    def test_raman2(self):
        self.assertSequenceEqual(
            self.data["raman2"], [0.117, 10.597, 32.059, 0.895, 79.019, 71.489]
        )

    def test_roa2(self):
        self.assertSequenceEqual(
            self.data["roa2"], [0.000, -0.000, 0.000, 0.000, 0.000, 0.000]
        )

    def test_cid2(self):
        self.assertSequenceEqual(
            self.data["cid2"], [0.000, -0.000, 0.000, 0.000, 0.000, 0.000]
        )

    def test_raman3(self):
        self.assertSequenceEqual(
            self.data["raman3"], [0.233, 21.194, 64.118, 1.790, 158.038, 142.978]
        )

    def test_roa3(self):
        self.assertSequenceEqual(
            self.data["roa3"], [0.000, -0.000, -0.000, 0.000, 0.000, 0.000]
        )

    def test_cid3(self):
        self.assertSequenceEqual(
            self.data["cid3"], [0.000, -0.000, -0.000, 0.000, 0.000, 0.000]
        )

    def test_rc180(self):
        self.assertSequenceEqual(
            self.data["rc180"], [0.714, 0.714, 0.266, -0.398, -0.341, 0.714]
        )


class TestOpt(ParserTestCase):
    file = "fal-opt.out"

    def test_methods_called(self):
        self.parser.initial.assert_called()
        self.parser.wait.assert_called()
        self.parser.frequencies.assert_not_called()
        self.parser.excited.assert_not_called()
        self.parser.optimization.assert_called()
        self.parser.geometry.assert_called()

    def test_keys(self):
        self.assertSetEqual(
            set(self.data.keys()),
            {
                "normal_termination",
                "version",
                "command",
                "charge",
                "multiplicity",
                "input_geom",
                "scf",
                "stoichiometry",
                "geometry",
                "molecule_atoms",
                "optimization_completed",
            },
        )

    def test_optimization_completed(self):
        self.assertTrue(self.data["optimization_completed"])

    def test_command(self):
        self.assertEqual(self.data["command"], "opt hf/3-21g")

    def test_scf(self):
        self.assertEqual(self.data["scf"], -113.221819992)

    def test_geometry(self):
        self.assertSequenceEqual(
            self.data["geometry"],
            [
                (-0.000016, 0.530659, 0.000000),
                (0.913392, 1.112945, 0.000000),
                (-0.913174, 1.113406, 0.000000),
                (-0.000016, -0.676288, 0.000000),
            ],
        )


class TestOptFreq(ParserTestCase):
    file = "fal-opt-freq.out"

    def test_methods_called(self):
        self.parser.initial.assert_called()
        self.parser.wait.assert_called()
        self.parser.frequencies.assert_called()
        self.parser.excited.assert_not_called()
        self.parser.optimization.assert_called()
        self.parser.geometry.assert_called()

    def test_keys(self):
        self.assertSetEqual(
            set(self.data.keys()),
            {
                "normal_termination",
                "version",
                "command",
                "charge",
                "multiplicity",
                "input_geom",
                "scf",
                "stoichiometry",
                "zpecorr",
                "tencorr",
                "entcorr",
                "gibcorr",
                "zpe",
                "ten",
                "ent",
                "gib",
                "freq",
                "mass",
                "frc",
                "iri",
                "depolarp",
                "depolaru",
                "ramanactiv",
                "geometry",
                "molecule_atoms",
                "optimization_completed",
            },
        )

    def test_command(self):
        self.assertEqual(self.data["command"], "opt freq hf/3-21g")


class TestInputError(ParserTestCase):
    file = "fal-input-error.out"

    def test_keys(self):
        self.assertSetEqual(
            set(self.data.keys()),
            {
                "normal_termination",
                "version",
                "command",
                "charge",
                "multiplicity",
                "input_geom",
            },
        )

    def test_normal_termination(self):
        self.assertFalse(self.data["normal_termination"])

    def test_stoichiometry(self):
        self.assertNotIn("stoichiometry", self.data)

    def test_atoms(self):
        self.assertNotIn("molecule_atoms", self.data)


class TestTd(ParserTestCase):
    file = "fal-td.out"

    def test_methods_called(self):
        self.parser.initial.assert_called()
        self.parser.wait.assert_called()
        self.parser.frequencies.assert_not_called()
        self.parser.excited.assert_called()
        self.parser.optimization.assert_not_called()
        self.parser.geometry.assert_called()

    def test_keys(self):
        self.assertSetEqual(
            set(self.data.keys()),
            {
                "normal_termination",
                "version",
                "command",
                "charge",
                "multiplicity",
                "input_geom",
                "scf",
                "stoichiometry",
                "vdip",
                "vosc",
                "ldip",
                "losc",
                "vrot",
                "lrot",
                "eemang",
                "wavelen",
                "ex_en",
                "transitions",
                "geometry",
                "molecule_atoms",
            },
        )

    def test_command(self):
        self.assertEqual(self.data["command"], "td hf/3-21g")

    def test_vdip(self):
        self.assertSequenceEqual(self.data["vdip"], [0.0000, 0.0100, 0.0360])

    def test_vosc(self):
        self.assertSequenceEqual(self.data["vosc"], [0.0000, 0.0218, 0.0714])

    def test_ldip(self):
        self.assertSequenceEqual(self.data["ldip"], [0.0000, 0.0199, 0.8344])

    def test_losc(self):
        self.assertSequenceEqual(self.data["losc"], [0.0000, 0.0040, 0.1869])

    def test_vrot(self):
        self.assertSequenceEqual(self.data["vrot"], [0.0000, 0.0000, 0.0000])

    def test_lrot(self):
        self.assertSequenceEqual(self.data["lrot"], [0.0000, 0.0000, 0.0000])

    def test_eemang(self):
        self.assertSequenceEqual(self.data["eemang"], [90.00, 90.00, 90.00])

    def test_wavelen(self):
        self.assertSequenceEqual(self.data["wavelen"], [326.42, 149.31, 135.60])

    def test_ex_en(self):
        self.assertSequenceEqual(self.data["ex_en"], [3.7983, 8.3039, 9.1437])

    def test_transitions(self):
        self.assertSequenceEqual(
            self.data["transitions"],
            [
                ((5, 9, 0.10410), (8, 9, 0.69982)),
                ((6, 9, 0.70461),),
                ((6, 12, 0.12121), (7, 9, 0.68192), (8, 11, -0.11535)),
            ],
        )


@unittest.skip("To be created.")
class TestUnfinished(ParserTestCase):
    # TODO: create test suite for interrupted jobs
    file = ""

    def test_normal_termination(self):
        self.assertTrue(self.data["normal_termination"])
