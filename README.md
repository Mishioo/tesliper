<img align="right" width="100" height="100" src="https://raw.githubusercontent.com/Mishioo/tesliper/master/tesliper/tesliper.ico">

# Tesliper

Tesliper: Theoretical Spectroscopist Little Helper is a program for batch processing of Gaussian output files. It is focused on calculation of vibrational and electronic spectra from Gaussian-calculated quantum poroperties of molecule conformers. Please note, that this project is still under developenemt, thus it may be prone to errors.
Tesliper is written in Python 3.6.4 and makes use of some additional third party packages (see below or requirements.txt). It may be used as a package or as a stand-alone application with dedicated GUI. It was tested on Windows 10 and Ubuntu 16.04 LTS. Any feedback will be highly appreciated! (you can contact me at wieclawmm@gmail.com)

## Getting Started

You can use Tesliper from python or as standalone application with dedicated graphical user inteface. See below for details.

### Requirements

```
Python 3.6+
numpy
openpyxl
matplotlib (needed only for gui)
```
This package is written in Python 3.6.4. and was not tested on previous relases. It will not work with Python 2.

### Installing to your Python distribution

To install Tesliper to your python distribution you will need to download (and extract zip) or clone the repository. From the resulting directory run:

`$ python setup.py install`

### Installing as standalone application

This option is currently available only for Windows users. To get your copy of Tesliper up and running, download and run a Windows installer from [latest relase](https://github.com/Mishioo/tesliper/releases/tag/0.7.1). It will extract all needed files, including Python iterpreter, to choosen directory and create shortcut on desktop.

## Build With

Installer for standalone was created with InnoSetup and uses WinPython.