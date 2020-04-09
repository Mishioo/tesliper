# IMPORTS
import numpy as np
import logging as lgg
import os
from itertools import zip_longest


from ._writer import Writer

# LOGGER
logger = lgg.getLogger(__name__)
logger.setLevel(lgg.DEBUG)


# CLASSES
class TxtWriter(Writer):
    def write(self, data):
        data = self.distribute_data(data)
        if data["energies"]:
            file = os.path.join(self.destination, "distribution_overview.txt")
            self.energies_overview(
                file,
                data["energies"],
                frequencies=data["frequencies"],
                stoichiometry=data["stoichiometry"],
            )
            for ens in data["energies"]:
                file = os.path.join(self.destination, f"distribution.{ens.genre}.txt")
                self.energies(file, ens, corrections=data["corrections"].get(ens.genre))
        if data["vibra"]:
            self.bars(
                self.destination,
                band=data["frequencies"],
                bars=data["vibra"],
                interfix="vibra",
            )
        if data["electr"]:
            self.bars(
                self.destination,
                band=data["wavelengths"],
                bars=data["electr"],
                interfix="electr",
            )
        if data["other_bars"]:
            # TO DO
            pass
        if data["spectra"]:
            for spc in data["spectra"]:
                self.spectra(self.destination, spc, interfix=spc.genre)
        if data["single"]:
            for spc in data["single"]:
                interfix = f".{spc.averaged_by}" if spc.averaged_by else ""
                file = os.path.join(
                    self.destination, f"spectrum.{spc.genre+interfix}.txt"
                )
                self.single_spectrum(file, spc)
        if data["other"]:
            # TO DO
            pass

    def energies(self, filename, energies, corrections=None):
        """Writes Energies object to txt file.

        Parameters
        ----------
        filename: string
            path to file
        energies: glassware.Energies
            Energies object that is to be serialized
        corrections: glassware.DataArray, optional
            DataArray object, containing energies corrections"""
        max_fnm = max(np.vectorize(len)(energies.filenames).max(), 20)
        # file_path = os.path.join(self.path,
        #                          f'distribution.{energies.genre}.txt')
        header = [f"{'Gaussian output file':<{max_fnm}}"]
        header += ["Population/%", "Min.B.Factor", "DE/(kcal/mol)", "Energy/Hartree"]
        header += ["Corr/Hartree"] if corrections is not None else []
        header = " | ".join(header)
        align = ("<", ">", ">", ">", ">", ">")
        width = (max_fnm, 12, 12, 13, 14, 12)
        corrections = corrections.values if corrections is not None else []
        fmt = (
            "",
            ".4f",
            ".4f",
            ".4f",
            ".8f" if energies.genre == "scf" else ".6f",
            "f",
        )
        rows = zip_longest(
            energies.filenames,
            energies.populations * 100,
            energies.min_factors,
            energies.deltas,
            energies.values,
            corrections,
            fillvalue=None,
        )
        with open(self.destination.joinpath(filename), "w") as file_:
            file_.write(header + "\n")
            file_.write("-" * len(header) + "\n")
            for row in rows:
                new_row = [
                    f"{v:{a}{w}{f}}"
                    for v, a, w, f in zip(row, align, width, fmt)
                    if v is not None
                ]
                file_.write(" | ".join(new_row) + "\n")
        logger.info("Energies separate export to text files done.")

    def energies_overview(
        self, filename, energies, frequencies=None, stoichiometry=None
    ):
        """Writes essential information from multiple Energies objects to
         single txt file.

        Parameters
        ----------
        filename: string
            path to file
        energies: list of glassware.Energies
            Energies objects that is to be expored
        frequencies: glassware.DataArray, optional
            DataArray object containing frequencies
        stoichiometry: glassware.InfoArray, optional
            InfoArray object containing stoichiometry information"""
        filenames = energies[0].filenames
        imaginary = [] if frequencies is None else frequencies.imaginary
        stoichiometry = [] if stoichiometry is None else stoichiometry.values
        max_fnm = max(np.vectorize(len)(filenames).max(), 20)
        try:
            max_stoich = max(np.vectorize(len)(stoichiometry).max(), 13)
        except ValueError:
            max_stoich = 0
        values = np.array([en.values for en in energies]).T
        # deltas = np.array([en.deltas for en in ens])
        popul = np.array([en.populations * 100 for en in energies]).T
        _stoich = f" | {'Stoichiometry':<{max_stoich}}"
        names = [self._header[en.genre] for en in energies]
        population_widths = [max(8, len(n)) for n in names]
        population_subheader = "  ".join(
            [f"{n:<{w}}" for n, w in zip(names, population_widths)]
        )
        energies_widths = [14 if n == "SCF" else 12 for n in names]
        energies_subheader = "  ".join(
            [f"{n:<{w}}" for n, w in zip(names, energies_widths)]
        )
        precisions = [8 if n == "SCF" else 6 for n in names]
        header = (
            f"{'Gaussian output file':<{max_fnm}} | "
            f"{'Population / %':^{len(population_subheader)}} | "
            f"{'Energy / Hartree':^{len(energies_subheader)}}"
            f"{' | Imag' if frequencies is not None else ''}"
            f"{_stoich if max_stoich else ''}"
        )
        line_format = (
            f"{{:<{max_fnm}}} | {{}} | {{}}"
            f"{' | {:^ 4}' if frequencies is not None else '{}'}"
            f"{f' | {{:<{max_stoich}}}' if max_stoich else '{}'}\n"
        )
        # fname = 'distribution_overview.txt'
        with open(self.destination.joinpath(filename), "w") as file_:
            file_.write(header + "\n")
            names_line = (
                " " * max_fnm
                + " | "
                + population_subheader
                + " | "
                + energies_subheader
                + (" |     " if frequencies is not None else "")
                + (" | " if max_stoich else "")
                + "\n"
            )
            file_.write(names_line)
            file_.write("-" * len(header) + "\n")
            rows = zip_longest(
                filenames, values, popul, imaginary, stoichiometry, fillvalue=""
            )
            for fnm, vals, pops, imag, stoich in rows:
                p_line = "  ".join(
                    [f"{p:>{w}.4f}" for p, w in zip(pops, population_widths)]
                )
                v_line = "  ".join(
                    [
                        f"{v:> {w}.{p}f}"
                        for v, w, p in zip(vals, energies_widths, precisions)
                    ]
                )
                line = line_format.format(fnm, p_line, v_line, imag, stoich)
                file_.write(line)
        logger.info("Energies collective export to text file done.")

    def bars(self, band, bars, interfix=""):
        """Writes Bars objects to txt files (one for each conformer).

        Notes
        -----
        Filenames are generated in form of conformer_name[.interfix].txt

        Parameters
        ----------
        dest: string
            path to destination directory
        band: glassware.Bars
            object containing information about band at which transitions occur;
            it should be frequencies for vibrational data and wavelengths or
            excitation energies for electronic data
        bars: list of glassware.Bars
            Bars objects that are to be serialized; all should contain
            information for the same conformers
        interfix: string, optional
            string included in produced filenames, nothing is added if omitted
        """
        bars = [band] + bars
        genres = [bar.genre for bar in bars]
        headers = [self._header[genre] for genre in genres]
        widths = [self._formatters[genre][4:-4] for genre in genres]
        formatted = [f"{h: <{w}}" for h, w in zip(headers, widths)]
        values = zip(*[bar.values for bar in bars])
        for fname, values_ in zip(bars[0].filenames, values):
            filename = (
                f"{'.'.join(fname.split('.')[:-1])}"
                f"{'.' if interfix else ''}{interfix}.txt"
            )
            with open(self.destination.joinpath(filename), "w") as file:
                file.write("\t".join(formatted))
                file.write("\n")
                for vals in zip(*values_):
                    line = "\t".join(
                        self._formatters[g].format(v) for v, g in zip(vals, genres)
                    )
                    file.write(line + "\n")
        logger.info("Bars export to text files done.")

    def spectra(self, spectra, interfix=""):
        """Writes Spectra object to text files (one for each conformer).

        Notes
        -----
        Filenames are generated in form of conformer_name[.interfix].txt

        Parameters
        ----------
        dest: string
            path to destination directory
        spectra: glassware.Spectra
            Spectra object, that is to be serialized
        interfix: string, optional
            string included in produced filenames, nothing is added if omitted
        """
        abscissa = spectra.x
        title = (
            f"{spectra.genre} calculated with peak width = {spectra.width}"
            f' {spectra.units["width"]} and {spectra.fitting} '
            f'fitting, shown as {spectra.units["x"]} vs. '
            f'{spectra.units["y"]}'
        )
        for fnm, values in zip(spectra.filenames, spectra.y):
            filename = (
                f"{'.'.join(fnm.split('.')[:-1])}"
                f"{'.' if interfix else ''}{interfix}.txt"
            )
            file_path = self.destination.joinpath(filename)
            with open(file_path, "w") as file:
                file.write(title + "\n")
                file.write(
                    "\n".join(
                        f"{int(a):>4d}\t{v: .4f}" for a, v in zip(abscissa, values)
                    )
                )
        logger.info("Spectra export to text files done.")

    def single_spectrum(self, filename, spectrum, include_header=True):
        """Writes SingleSpectrum object to txt file.

        Parameters
        ----------
        file: string
            path to file
        spectrum: glassware.SingleSpectrum
            spectrum, that is to be serialized
        include_header: bool, optional
            determines if file should contain a header with metadata,
            True by default
        """
        title = (
            f"{spectrum.genre} calculated with peak width = "
            f'{spectrum.width} {spectrum.units["width"]} and '
            f'{spectrum.fitting} fitting, shown as {spectrum.units["x"]} '
            f'vs. {spectrum.units["y"]}'
        )
        with open(self.destination.joinpath(filename), "w") as file_:
            if include_header:
                file_.write(title + "\n")
                if spectrum.averaged_by:
                    file_.write(
                        f"{len(spectrum.filenames)} conformers averaged base on"
                        f" {self._header[spectrum.averaged_by]}\n"
                    )
            file_.write(
                "\n".join(
                    # TODO: probably should change when nmr introduced
                    f"{int(x):>4d}\t{y: .4f}"
                    for x, y in zip(spectrum.x, spectrum.y)
                )
            )
        logger.info("Spectrum export to text files done.")