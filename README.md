# MIDI Splitter Py

MIDI Splitter Py is a command-line tool designed to split MIDI files into separate tracks, processing multiple files or directories concurrently for efficiency. It offers features such as duplicating the first track across all tracks, reading and displaying track and instrument names, and removing empty tracks.

## Features

- **Batch Processing:** Process multiple MIDI files or entire directories at once.
- **Duplicate First Track:** Option to duplicate the first track onto all tracks, useful for preserving tempo and other settings.
- **Track and Instrument Names:** Read and display names for each track and their assigned instruments.
- **Remove Empty Tracks:** Detection and removal of tracks that do not contain meaningful MIDI events.
- **Concurrency:** Utilizes threading to improve processing time for batches of MIDI files.

## Installation

Before running MIDI Splitter Lite, you need to install the required Python libraries:

```
pip install -r requirements.txt
```

## Usage
To use MIDI Splitter Lite, run the script from the command line, providing the path to the MIDI file(s) or directory(ies) you wish to process, and specify the output directory using the -o or --output_path option. Other options are available for additional functionality:

```
python midi_splitter.py [input MIDI files or directories] -o [output directory] [options]
```

## Options
- -o, --output_path: Specify the output directory for the split MIDI files (required).
- -d, --duplicate-first-track: Duplicate the first track onto all tracks.
- -t, --track-names: Read and display track names.
- -i, --instrument-names: Read and display instrument names.
- -r, --remove-empty-tracks: Remove tracks that do not contain meaningful MIDI events.
- -v, --verbose: Enable verbose output.
### Example

```
python midi_splitter.py input.mid -o ./output -t -i -r
```
This command processes input.mid, reads and displays track and instrument names, removes empty tracks, and saves the split tracks to the ./output directory.
