import random
import argparse
from pathlib import Path
import os

def inject_error(input_file, output_file, error_ratio):
    """
    Inject errors into the CSV file based on error ratio
    error_ratio: float between 0 and 1 (e.g., 0.1 for 10% error)
    """
    try:
        with open(input_file, 'r') as f:
            content = f.read().strip()
        
        # Split into individual note events
        notes = content.split()
        
        modified_notes = []
        for note in notes:
            # Split into components (pitch, velocity, duration, time, bend, error)
            components = note.split(':')
            
            # Randomly decide whether to inject error based on error_ratio
            if random.random() < error_ratio:
                # Modify pitch value (first component)
                pitch_val = int(components[0][1:])  # Remove 'p' and convert to int
                # Add random error between -2 and 2 semitones
                new_pitch = max(0, min(127, pitch_val + random.randint(-2, 2)))
                components[0] = f'p{new_pitch}'
                
                # Set error flag to 1
                components[-1] = 'e1'
            
            modified_notes.append(':'.join(components))
        
        # Write modified content to output file
        with open(output_file, 'w') as f:
            f.write(' '.join(modified_notes))
            
        print(f"Error injection complete. Modified file saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def process_directory(input_dir, output_dir, error_ratio):
    """
    Process all CSV files in the input directory
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Process each CSV file
    for input_file in Path(input_dir).glob('*.csv'):
        output_file = Path(output_dir) / f"{input_file.stem}_error{error_ratio}.csv"
        print(f"Processing: {input_file.name}")
        inject_error(str(input_file), str(output_file), error_ratio)

def main():
    parser = argparse.ArgumentParser(description='Inject errors into CSV file(s)')
    parser.add_argument('input_path', help='Input CSV file or directory')
    parser.add_argument('output_path', help='Output CSV file or directory')
    parser.add_argument('--error_ratio', type=float, default=0.1, help='Ratio of notes to modify (0.0 to 1.0)')
    parser.add_argument('--batch', action='store_true', help='Process entire directory')
    
    args = parser.parse_args()
    
    if not 0 <= args.error_ratio <= 1:
        print("Error ratio must be between 0 and 1")
        return
    
    if args.batch:
        process_directory(args.input_path, args.output_path, args.error_ratio)
    else:
        inject_error(args.input_path, args.output_path, args.error_ratio)

if __name__ == "__main__":
    main()

# Example usage: 
#
# Single file: python3 err_injection.py input.csv output.csv --error_ratio (ratio)
# Multiple files: python3 err_injection.py input_directory output_directory --error_ratio (ratio) --batch