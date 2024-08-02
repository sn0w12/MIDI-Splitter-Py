import argparse
import os
import string
import mido
from mido import MidiFile
from glob import glob
from threading import Thread
from tqdm import tqdm

# Instrument names list
INSTRUMENTS = [
    "Acoustic Grand Piano",
    "Bright Acoustic Piano",
    "Electric Grand Piano",
    "Honky-Tonk Piano",
    "Rhodes Piano",
    "Chorused Piano",
    "Harpsichord",
    "Clavinet",
    "Celesta",
    "Glockenspiel",
    "Music Box",
    "Vibraphone",
    "Marimba",
    "Xylophone",
    "Tubular Bells",
    "Dulcimer",
    "Hammond Organ",
    "Percussive Organ",
    "Rock Organ",
    "Church Organ",
    "Reed Organ",
    "Accordion",
    "Harmonica",
    "Tango Accordion",
    "Acoustic Guitar - Nylon",
    "Acoustic Guitar - Steel",
    "Electric Guitar - Jazz",
    "Electric Guitar - Clean",
    "Electric Guitar - Muted",
    "Overdriven Guitar",
    "Distortion Guitar",
    "Guitar Harmonics",
    "Acoustic Bass",
    "Electric Bass - Finger",
    "Electric Bass - Pick",
    "Fretless Bass",
    "Slap Bass 1",
    "Slap Bass 2",
    "Synth Bass 1",
    "Synth Bass 2",
    "Violin",
    "Viola",
    "Cello",
    "Contrabass",
    "Tremolo Strings",
    "Pizzicato Strings",
    "Orchestral Harp",
    "Timpani",
    "String Ensemble 1",
    "String Ensemble 2",
    "Synth. Strings 1",
    "Synth. Strings 2",
    "Choir Aahs",
    "Voice Oohs",
    "Synth Voice",
    "Orchestra Hit",
    "Trumpet",
    "Trombone",
    "Tuba",
    "Muted Trumpet",
    "French Horn",
    "Brass Section",
    "Synth. Brass 1",
    "Synth. Brass 2",
    "Soprano Sax",
    "Alto Sax",
    "Tenor Sax",
    "Baritone Sax",
    "Oboe",
    "English Horn",
    "Bassoon",
    "Clarinet",
    "Piccolo",
    "Flute",
    "Recorder",
    "Pan Flute",
    "Bottle Blow",
    "Shakuhachi",
    "Whistle",
    "Ocarina",
    "Synth Lead 1 - Square",
    "Synth Lead 2 - Sawtooth",
    "Synth Lead 3 - Calliope",
    "Synth Lead 4 - Chiff",
    "Synth Lead 5 - Charang",
    "Synth Lead 6 - Voice",
    "Synth Lead 7 - Fifths",
    "Synth Lead 8 - Brass + Lead",
    "Synth Pad 1 - New Age",
    "Synth Pad 2 - Warm",
    "Synth Pad 3 - Polysynth",
    "Synth Pad 4 - Choir",
    "Synth Pad 5 - Bowed",
    "Synth Pad 6 - Metallic",
    "Synth Pad 7 - Halo",
    "Synth Pad 8 - Sweep",
    "FX 1 - Rain",
    "FX 2 - Soundtrack",
    "FX 3 - Crystal",
    "FX 4 - Atmosphere",
    "FX 5 - Brightness",
    "FX 6 - Goblins",
    "FX 7 - Echoes",
    "FX 8 - Sci-Fi",
    "Sitar",
    "Banjo",
    "Shamisen",
    "Koto",
    "Kalimba",
    "Bagpipe",
    "Fiddle",
    "Shanai",
    "Tinkle Bell",
    "Agogo",
    "Steel Drums",
    "Woodblock",
    "Taiko Drum",
    "Melodic Tom",
    "Synth Drum",
    "Reverse Cymbal",
    "Guitar Fret Noise",
    "Breath Noise",
    "Seashore",
    "Bird Tweet",
    "Telephone Ring",
    "Helicopter",
    "Applause",
    "Gunshot",
]


def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return "".join(c for c in filename if c in valid_chars)


def unique_filename(output_path, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(output_path, unique_filename)):
        unique_filename = f"{base}_{counter}{extension}"
        counter += 1
    return unique_filename


def get_instrument_name(program_number):
    if 0 <= program_number < len(INSTRUMENTS):
        return INSTRUMENTS[program_number]
    return "Unknown Instrument"


def is_track_empty(track):
    # Define which message types are considered meaningful
    meaningful_message_types = {"note_on", "note_off", "control_change"}
    for msg in track:
        if msg.type in meaningful_message_types:
            # Consider track not empty if a meaningful message is found
            return False
    return True


def process_midi_file(midi_file, output_path, args):
    try:
        midi = MidiFile(midi_file)
        if args.verbose:
            print(f"Successfully loaded MIDI file: {midi_file}")
    except IOError:
        print(f"Error: Could not open MIDI file: {midi_file}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    base_name = os.path.splitext(os.path.basename(midi_file))[0]
    specific_output_path = os.path.join(output_path, sanitize_filename(base_name))
    if not os.path.exists(specific_output_path) and args.verbose:
        os.makedirs(specific_output_path)
        print(f"Created directory: {specific_output_path}")
    elif not os.path.exists(specific_output_path):
        os.makedirs(specific_output_path)

    for i, track in enumerate(midi.tracks):
        if args.remove_empty_tracks and is_track_empty(track) and args.verbose:
            print(f"Skipping empty track: Track {i+1}")
            continue
        elif args.remove_empty_tracks and is_track_empty(track):
            continue

        new_midi = MidiFile()
        if args.duplicate_first_track and i > 0:
            new_midi.tracks.append(midi.tracks[0])

        new_midi.tracks.append(track)

        track_name = f"Track {i+1}"
        instrument_name = "No Instrument"
        if args.track_names or args.instrument_names:
            for msg in track:
                if msg.type == "track_name" and args.track_names:
                    track_name = msg.name
                if msg.type == "program_change" and args.instrument_names:
                    instrument_name = get_instrument_name(msg.program)
                    break

        if instrument_name != "No Instrument":
            filename = f"{sanitize_filename(track_name)}_{sanitize_filename(instrument_name)}.mid"
        else:
            filename = f"{sanitize_filename(track_name)}.mid"
        filename = unique_filename(specific_output_path, filename)
        file_path = os.path.join(specific_output_path, filename)
        new_midi.save(file_path)

        if args.verbose:
            print(f"Track saved: {file_path} - Instrument: {instrument_name}")


def process_files(midi_files, args):
    threads = []
    for midi_file in midi_files:
        thread = Thread(
            target=process_midi_file, args=(midi_file, args.output_path, args)
        )
        thread.start()
        threads.append(thread)
    for thread in tqdm(threads, desc="Processing MIDI files"):
        thread.join()


def main():
    parser = argparse.ArgumentParser(
        description="MIDI Splitter Py with Threading and Progress Bar"
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="+",
        help="Path to MIDI files or directories to process.",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        required=True,
        help="Output directory for the split MIDI files.",
    )
    parser.add_argument(
        "-d",
        "--duplicate-first-track",
        action="store_true",
        help="Duplicate the first track onto all tracks.",
    )
    parser.add_argument(
        "-t", "--track-names", action="store_true", help="Read and display track names."
    )
    parser.add_argument(
        "-i",
        "--instrument-names",
        action="store_true",
        help="Read and display instrument names.",
    )
    parser.add_argument(
        "-r",
        "--remove-empty-tracks",
        action="store_true",
        help="Remove tracks that do not contain meaningful MIDI events.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )

    args = parser.parse_args()

    midi_files = []
    for input_path in args.input:
        if os.path.isdir(input_path):
            midi_files.extend(glob(os.path.join(input_path, "*.mid")))
        elif os.path.isfile(input_path) and input_path.endswith(".mid"):
            midi_files.append(input_path)

    process_files(midi_files, args)


if __name__ == "__main__":
    main()
