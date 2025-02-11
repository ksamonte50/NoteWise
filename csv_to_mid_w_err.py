from copy import deepcopy
import py_midicsv as pm
import os
import shutil
import argparse

def pitchbend_quantization_decoder(pitchbend_value):

    if pitchbend_value < 15:
        return pitchbend_value*512
    
    if pitchbend_value < 31:
        return 7680 + (pitchbend_value-15)*64
    
    if pitchbend_value < 47:
        return 8704 + (pitchbend_value-31)*512

    return 16384

def create_midi_file(input_file_path, output_file_path, header, pitchbend=False):
    with open(input_file_path, "r") as file:
        simplified_midi = file.read()[:-1]

    l = simplified_midi.split(' ')
    
    for i in range(len(l)):
        l[i] = l[i].split(':')
    
    for i in range(len(l)):
        if pitchbend:
            # Parse 6 values including error value
            for j in range(6):
                print(f"Before conversion: l[{i}][{j}] = '{l[i][j]}'")  # Debug print
                l[i][j] = int(l[i][j][1:])
        else:
            # Parse 5 values including error value
            for j in range(5):
                print(f"Before conversion: l[{i}][{j}] = '{l[i][j]}'")  # Debug print
                l[i][j] = int(l[i][j][1:])

    t_abs = 0
    for i in range(len(l)):
        l[i].append(t_abs)
        t_abs += l[i][3]
    j = deepcopy(l)

    unfinished_notes = {}  # dictionary pitch:endtime
    if pitchbend:
        for line in j:
            if line[0] in unfinished_notes and line[5] == unfinished_notes[line[0]]:
                unfinished_notes[line[0]] = unfinished_notes[line[0]] + line[2]
            if line[0] not in unfinished_notes:
                unfinished_notes[line[0]] = line[5] + line[2]

            temp_del_list = []
            for pitch in unfinished_notes:
                if unfinished_notes[pitch] < line[5]:
                    l.append([pitch, 0, 0, 0, 0, unfinished_notes[pitch], line[5]])  # Added error value
                    temp_del_list.append(pitch)
            
            for pitch in temp_del_list:
                del unfinished_notes[pitch]

    l = sorted(l, key=lambda x: x[5])
    l.append([0, 0, 0, 0, 0, l[-1][5], 0])  # Added error value

    csv_string = deepcopy(header)
    temp_bended_notes = {}  # dictionary pitch:time

    for i in range(len(l)):
        if pitchbend:
            if l[i][1] == 0:  # Note off
                if l[i][0] in temp_bended_notes:
                    del temp_bended_notes[l[i][0]]
                csv_string.append(f"2, {l[i][5]}, Note_off_c, 0, {l[i][0]}, {l[i][1]}\n")
            else:
                if l[i][0] in temp_bended_notes:
                    csv_string.append(f"2, {l[i][5]}, Pitch_bend_c, 0, {str(pitchbend_quantization_decoder(int(l[i][4])))}\n")
                csv_string.append(f"2, {l[i][5]}, Note_on_c, 0, {l[i][0]}, {l[i][1]}\n")
                temp_bended_notes[l[i][0]] = l[i][5]

    csv_string.append(f"2, {l[len(l)-1][5]}, End_track\n")
    csv_string.append("0, 0, End_of_file")

    midi_object = pm.csv_to_midi(csv_string)
    with open(output_file_path, "wb") as output_file:
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)

def dataset_text_to_midi(output_dir_path, input_dir_path, header):
    files = os.listdir(input_dir_path)
    for input_file_name in files:
        id, _ = os.path.splitext(input_file_name)
        output_file_name = f"{id}_converted.mid"
        input_file_path = os.path.join(input_dir_path, input_file_name)
        output_file_path = os.path.join(output_dir_path, output_file_name)
        create_midi_file(input_file_path, output_file_path, header)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert CSV to MIDI format')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('output_file', help='Output MIDI file')
    parser.add_argument('--pitchbend', action='store_true', help='Include pitch bend information')
    parser.add_argument('--batch', action='store_true', help='Process entire directory')
    
    args = parser.parse_args()

    # Define standard MIDI header
    header = [
        "0, 0, Header, 1, 2, 480\n",
        "1, 0, Start_track\n",
        "1, 0, Time_signature, 4, 2, 24, 8\n",
        "1, 0, End_track\n",
        "2, 0, Start_track\n"
    ]

    if args.batch:
        dataset_text_to_midi(args.output_file, args.input_file, header)
    else:
        create_midi_file(args.input_file, args.output_file, header, pitchbend=args.pitchbend)