import os
import sys
import argparse
import py_midicsv as pm
from pathlib import Path

def texte(lieu, pitchbend=False):
    csv_string = pm.midi_to_csv(r"{}".format(lieu))
    lmidi = []
    temp_pitchbend_value = '8192'  # initial value of pitchbend that has no effect on sound

    # Initialize with error value (0 for default)
    if pitchbend:
        lfinal = [["0","0","0","0","0","0","0"]]  # Added error value column
    if not pitchbend:
        lfinal = [["0","0","0","0","0","0"]]  # Added error value column

    for i in csv_string:
        intermediaire = i.split(', ')
        if pitchbend:
            if 'Pitch_bend' in intermediaire[2]:
                temp_pitchbend_value = intermediaire[4][:-1]
        if 'Note' in intermediaire[2]:
            if not pitchbend:
                # Added 0 as default error value
                lmidi.append([intermediaire[1], intermediaire[4], intermediaire[5][:-1], "0"])
            else:
                # Added 0 as default error value
                lmidi.append([intermediaire[1], intermediaire[4], intermediaire[5][:-1], temp_pitchbend_value, "0"])

    lmidi = sorted(lmidi, key=lambda x: int(x[0]))
  
    unfinished_notes = {}
    for i in range(len(lmidi)):
        if lmidi[i][2] != "0":
            if pitchbend:
                # Added error value (last element from lmidi)
                lfinal.append([lmidi[i][0], lmidi[i][1], lmidi[i][2], "", "", lmidi[i][3], lmidi[i][4]])
            else:
                # Added error value (last element from lmidi)
                lfinal.append([lmidi[i][0], lmidi[i][1], lmidi[i][2], "", "", lmidi[i][3]])
            
            lfinal[-2][4] = (str(int(lfinal[-1][0]) - int(lfinal[-2][0])))
            if ((lmidi[i][1] in unfinished_notes)):
                unfinished_notes[lmidi[i][1]].append(len(lfinal) - 1)
            else:
                unfinished_notes[lmidi[i][1]] = [len(lfinal) - 1]
        
        if lmidi[i][2] == "0":
            if ((lmidi[i][1] in unfinished_notes) and (unfinished_notes[lmidi[i][1]] != [])):
                idx = unfinished_notes[lmidi[i][1]][-1]
                lfinal[idx][3] = str(int(lmidi[i][0]) - int(lfinal[idx][0]))
                unfinished_notes[lmidi[i][1]].pop()

    lfinal.pop(0)
    for i in range(len(lfinal)):
        lfinal[i].pop(0)
    lfinal[-1][3] = "0"
    
    s = ''
    for i in lfinal:
        if pitchbend:
            # Added error value 'e' in output string
            s += f'p{i[0]}:v{i[1]}:d{i[2]}:t{i[3]}:b{i[4]}:e{i[5]} '
        else:
            # Added error value 'e' in output string
            s += f'p{i[0]}:v{i[1]}:d{i[2]}:t{i[3]}:e{i[4]} '
    
    return s

def main(input_file, output_file, pitchbend=False):
    with open(output_file, "w") as file:
        file.write(texte(input_file, pitchbend=pitchbend))

# Single file input
# if __name__ == "__main__":
#     input_file = "test-files/4pf.mid"
#     output_file = "output.csv"
#     main(input_file, output_file, pitchbend=False)

# Example usage:
# main("input.mid", "output.txt", pitchbend=False)


# Subset input
def process_midi_folder(input_folder, output_folder, pitchbend=False):
    """Process all MIDI files in a folder and convert to CSV format"""
    # Create output directory if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Process each MIDI file
    for midi_file in Path(input_folder).glob('*.mid'):
        output_file = Path(output_folder) / f"{midi_file.stem}.csv"
        try:
            main(str(midi_file), str(output_file), pitchbend)
            print(f"Processed: {midi_file.name}")
        except Exception as e:
            print(f"Error processing {midi_file.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert MIDI files to CSV format')
    parser.add_argument('input_folder', help='Input folder containing MIDI files')
    parser.add_argument('output_folder', help='Output folder for CSV files')
    parser.add_argument('--pitchbend', action='store_true', help='Include pitch bend information')
    
    args = parser.parse_args()
    process_midi_folder(args.input_folder, args.output_folder, args.pitchbend)

# Example usage:
# python3 mid_to_csv_w_err.py /path/to/midi/folder /path/to/output/folder --pitchbend