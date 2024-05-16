# emay2medview

Convert a CSV file from an EMAY&trade; SleepO2&trade; or Wellue&trade; O2Ring&trade; pulse oximeter into ChoiceMMed&trade;'s MedView&trade; (.DAT) format, which can be imported into [OSCAR](https://www.sleepfiles.com/OSCAR/), the Open Source CPAP Analysis Reporter.

## Install

Requires Python 3.6 or newer.

Install the code either by cloning the repo or downloading a ZIP.

### Clone the `git` repository

```shell
git clone https://github.com/ElectricalPaul/emay2medview.git
```

### Download and DIY

1. Go to the [emay2medview repo](https://github.com/ElectricalPaul/emay2medview) on Github
1. Click on "Clone or Download"
1. Click on "Download ZIP" and save the ZIP file
1. Unzip the file
1. _Optional (recommended):_ create a virtual environment: `virtualenv venv && source venv/bin/activate`
1. Install the package, e.g. `pip install <zipfile>` or `cd <extracted zip> && pip install .`
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
1. Run `emay2medview` from the shell/Terminal/Command Prompt and give it the name of the CSV file, e.g. `emay2medview 20240226.csv`
1. Import the resulting `DAT` file (e.g. `20240226.DAT`) into OSCAR with the Oximetry Wizard

### Options

The only required argument is the input CSV filename in EMAY format.

Optionally, specify:

* `--output-file`, `-o` Path to a custom filename for the MedView output data file. If unspecified, the output file will use the CSV's filename and location but with a _.dat_ extension.
* `--input-format`, `-f` Data format of the input CSV file. Defaults to `emay` but `o2insight` may be specified for O2Ring data exported from O2 Insight Pro. You may also invoke the script using the `o2insight2medview` command in lieu of specifying this option.

## Future Plans

* Add a GUI, possibly with `tkinter` directly, or [PySimpleGUI](https://realpython.com/pysimplegui-python/)
* Make a standalone program using [PyInstaller](https://pyinstaller.org/en/stable/)

## Notes

Format code with `black` and default settings.

Check version requirements with `vermin -vvv *.py`.

## Acknowledgments

This program is based on [code posted on the Apnea Board forums by user "joeblough"](https://www.apneaboard.com/forums/Thread-python-file-converter-for-EMAY-sleep-pulse-oximeter),
and is used by permission.

EMAY and SleepO2 are trademarks of EMAY (HK) Limited.

ChoiceMMed and MedView are trademarks of Beijing Choice Electronic Tech Co.

O2Ring, O2 Insight Pro, and Wellue are trademarks of Shenzhen Viatom Technology Co., Ltd. (Viatom).
