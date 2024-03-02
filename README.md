# emay2medview

Convert a CSV file from an EMAY\[TM\] SleepO2\[TM\] pulse oximeter into ChoiceMMed\[TM\]'s MedView\[TM\] (.DAT) format, which can be imported into [OSCAR](https://www.sleepfiles.com/OSCAR/), the Open Source CPAP Analysis Reporter.

## Install

Requires Python 3.6 or newer. The default Python installation should have all required packages.

Install the code either by cloning the repo or downloading a ZIP.

### Clone the `git` repository

```
$ git clone https://github.com/ElectricalPaul/emay2medview.git
```

### Download and DIY

1. Go to the [emay2medview repo](https://github.com/ElectricalPaul/emay2medview) on Github
1. Click on "Clone or Download"
1. Click on "Download ZIP" and save the ZIP file
1. Unzip the file
1. ???
1. ~Profit!~ Convert data files!

## Usage

1. First you need some data from your EMAY SleepO2
    1. Open the EMAY app on your phone
    1. Select a recorded session to open the "Detail" view
    1. Select "Report"
    1. Select "Data List"
    1. Select "Share"
    1. Save the file to Google Drive or iCloud, or email it to yourself
    1. Transfer the file from the cloud or email to your local system, e.g. `Downloads`
1. Run `emay2medview.py` from the shell/Terminal/Command Prompt and give it the name of the CSV file, e.g. `python3 ./emay2medview.pt 20240226.csv`
1. Import the resulting `DAT` file (e.g. `20240226.DAT`) into OSCAR with the Oximetry Wizard

## Future Plans

* Add a GUI, possibly with `tkinter` directly, or [PySimpleGUI](https://realpython.com/pysimplegui-python/)
* Make the code installable with `pip3`
* Make a standalone program using [PyInstaller](https://pyinstaller.org/en/stable/)

## Notes

Format code with `black` and default settings.

Check version requirements with `vermin -vvv *.py`.

## Acknowledgments

This program is based on [code posted on the Apnea Board forums by user "joeblough"](https://www.apneaboard.com/forums/Thread-python-file-converter-for-EMAY-sleep-pulse-oximeter),
and is used by permission.

EMAY and SleepO2 are trademarks of EMAY (HK) Limited.

ChoiceMMed and MedView are trademarks of Beijing Choice Electronic Tech Co.
