# IMPORTS
import os
import logging as lgg
import re

from . import gaussian_parser
from . import spectra_parser


# LOGGER
logger = lgg.getLogger(__name__)
logger.setLevel(lgg.DEBUG)


# CLASSES
# TODO: Consider integration with gauopen interface: http://gaussian.com/interfacing/
class Soxhlet:
    """A tool for data extraction from files in specific directory. Typical
    use:

    >>> s = Soxhlet('absolute/path_to/working/directory')
    >>> data = s.extract()

    Attributes
    ----------
    path: str
        Path of directory bounded to Soxhlet instance.
    files: list
        List of files present in directory bounded to Soxhlet instance.
    output_files
    bar_files
    """

    def __init__(self, path=None, wanted_files=None, extension=None):
        """Initialization of Soxhlet object.

        Parameters
        ----------
        path: str
            String representing absolute path to directory containing files,
            which will be the subject of data extraction.
        wanted_files: list, optional
            List of files, that should be loaded for further extraction. If
            omitted, all files present in directory will be taken.
        extension: str
            String representing file extension of output files, that are to be
            parsed. If omitted, Soxhlet will try to resolve it based on
            contents of directory pointed by path.

        Raises
        ------
        FileNotFoundError
            If path passed as argument to constructor doesn't exist.
        """
        self.path = path
        self.files = os.listdir(path)
        # TODO: change wanted_files to be  given priority over guess_extension
        #       or to ignore file extensions
        self.wanted_files = wanted_files
        self.extension = extension
        self.parser = gaussian_parser.GaussianParser()
        self.spectra_parser = spectra_parser.SpectraParser()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value is None:
            self._path = os.getcwd()
        elif not os.path.isdir(value):
            raise FileNotFoundError(f"Path not found: {value}")
        else:
            self.files = os.listdir(value)
            self._path = value

    @property
    def output_files(self):
        """List of (sorted by file name) gaussian output files from files
        list associated with Soxhlet instance.
        """
        try:
            ext = (
                self.extension if self.extension is not None else self.guess_extension()
            )
            gf = sorted(self.filter_files(ext))
        except ValueError:
            gf = []
        return gf

    def filter_files(self, ext=None):
        """Filters files from filenames list.

        Function filters file names in list associated with Soxhlet object
        instance. It returns list of file names ending with provided ext
        string, representing file extension and starting with any of filenames
        associated with instance as wanted_files if those were provided.

        Parameters
        ----------
        ext : str
            Strings representing file extension.

        Returns
        -------
        list
            List of filtered filenames as strings.

        Raises
        ------
        ValueError
            If parameter `ext` is not given and attribute `extension` in None.
        """
        ext = ext if ext is not None else self.extension
        files = self.wanted_files if self.wanted_files else self.files
        try:
            filtered = [f for f in files if f.endswith(ext)]
        except TypeError as error:
            raise ValueError(
                "Parameter `ext` must be given if attribute `extension` is None."
            ) from error
        return filtered

    def guess_extension(self):
        """Checks list of file extensions in list of file names.

        Function checks for .log and .out files in passed list of file names.
        If both are present, it raises TypeError exception.
        If either is present, it raises ValueError exception.
        It returns string representing file extension present in files list.

        Returns
        -------
        str
            '.log' if *.log files are present in filenames list or '.out' if
            *.out files are present in filenames list.

        Raises
        ------
        ValueError
            If both *.log and *.out files are present in list of filenames.
        TypeError
            If neither *.log nor *.out files are present in list of filenames.

        TO DO
        -----
        add support for other extensions when new parsers implemented
        """
        files = self.wanted_files if self.wanted_files else self.files
        logs, outs = (any(f.endswith(ext) for f in files) for ext in (".log", ".out"))
        if outs and logs:
            raise ValueError(".log and .out files mixed in directory.")
        elif not outs and not logs:
            raise TypeError("Didn't found any .log or .out files.")
        else:
            return ".log" if logs else ".out"

    def extract_iter(self):
        """Extracts data from gaussian files associated with Soxhlet instance.
        Implemented as generator.

        Yields
        ------
        tuple
            Two item tuple with name of parsed file as first and extracted
            data as second item, for each file associated with Soxhlet instance.
        """
        for num, file in enumerate(self.output_files):
            logger.debug(f"Starting extraction from file: {file}")
            with open(os.path.join(self.path, file)) as handle:
                data = self.parser.parse(handle)
            logger.debug("file done.\n")
            yield file, data

    def extract(self):
        """Extracts data from gaussian files associated with Soxhlet instance.

        Returns
        ------
        dict of dicts
            dictionary of extracted data, with name of parsed file as key and
            data as value, for each file associated with Soxhlet instance.
        """
        return {f: d for f, d in self.extract_iter()}

    def load_settings(self):
        """Parses Setup.txt file associated with object and returns dict with
        extracted values. Prefers Setup.txt file over *Setup.txt files.
        Settings values should be placed one for line in this order: hwhm, start, stop,
        step, fitting. Anything beside a number and "lorentzian" or "gaussian" word
        is ignored.

        Returns
        -------
        dict
            Dictionary with extracted settings data.

        Raises
        ------
        FileNotFoundError
            If no or multiple setup.txt files found.

        """
        # TODO: make it use keys instead of order
        # TODO?: implement ConfigParser-based solution
        try:
            f = open("Setup.txt", "r")
        except FileNotFoundError:
            fls = [file.endswith("Setup.txt") for file in self.files]
            if len(fls) != 1:
                raise FileNotFoundError("No or multiple setup files in directory.")
            else:
                f = open(fls[0], "r")
        text = f.read()
        regex = r"(-?\d+.?d\*|lorentzian|gaussian)"
        sett = re.findall(regex, text.lower())
        sett = {k: v for k, v in zip(("hwhm start stop step fitting".split(" "), sett))}
        f.close()
        return sett

    def load_spectrum(self, filename):
        # TO DO: add support for .spc and .csv files
        # TO DO: add docstring
        appended = os.path.join(self.path, filename)
        if os.path.isfile(appended):
            path = appended
        elif os.path.isfile(filename):
            path = filename
        else:
            raise FileNotFoundError(f"Cannot find such file: '{filename}'.")
        spectrum = self.spectra_parser.parse(path)
        return spectrum
