import pandas as pd
import argparse
import ast

def parse_target_atoms(target_atoms_str):
    """
    Parse the target_atoms string into a dictionary using literal_eval.
    This is safer than using eval.
    """
    try:
        target_atoms = ast.literal_eval(target_atoms_str)
        if not isinstance(target_atoms, dict):
            raise ValueError("Target atoms must be a dictionary.")
        return target_atoms
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing target_atoms: {e}")
        return None

def extract_density_from_dscf_log(file_path, target_atoms, output_file):
    """
    Extract electron densities from the specified dscf log file.
    """
    extracted_data = {atom_num: {'Element': element, 'Densities': []} for atom_num, element in target_atoms.items()}
    within_target_section = False  # Flag to track section of interest in the log

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Start extracting after this line
                if "atomic populations from spin  density:" in line:
                    within_target_section = True
                    continue
                # Stop at the separator line
                elif within_target_section and "=====" in line:
                    break
                # Process only relevant lines in target section
                elif within_target_section:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            atom_number = int(parts[0])
                            element = parts[1].lower()
                            densities = [float(d) for d in parts[2:]]
                            
                            # Check if atom matches target
                            if atom_number in target_atoms and target_atoms[atom_number] == element:
                                extracted_data[atom_number]['Densities'] = densities
                        except ValueError:
                            continue  # Skip lines that don't match expected format

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return

    # Convert extracted data to DataFrame
    extracted_df = pd.DataFrame({
        'Atom Number': list(extracted_data.keys()),
        'Element': [data['Element'] for data in extracted_data.values()],
        'sum': [data['Densities'][0] if data['Densities'] else None for data in extracted_data.values()],
        'n(s)': [data['Densities'][1] if len(data['Densities']) > 1 else None for data in extracted_data.values()],
        'n(p)': [data['Densities'][2] if len(data['Densities']) > 2 else None for data in extracted_data.values()],
        'n(d)': [data['Densities'][3] if len(data['Densities']) > 3 else None for data in extracted_data.values()],
        'n(f)': [data['Densities'][4] if len(data['Densities']) > 4 else None for data in extracted_data.values()],
        'n(g)': [data['Densities'][5] if len(data['Densities']) > 5 else None for data in extracted_data.values()],
    })

    with open(output_file, "w") as f:
        f.write(extracted_df.to_string(index=False))
    print(f"Extraction complete. Data saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Extract electron densities from dscf log file.")
    parser.add_argument("-i", "--input_file", required=True, help="Path to the dscf log file.")
    parser.add_argument("-t", "--target_atoms", required=True, type=str, 
                        help="Dictionary of target atoms in the format '{66: \"s\", 67: \"s\", ...}'.")
    parser.add_argument('-o', '--output_file', type=str, default='extracted_df.log')

    args = parser.parse_args()
    file_path = args.input_file
    target_atoms = parse_target_atoms(args.target_atoms)
    output_file = args.output_file

    if target_atoms is not None:
        extract_density_from_dscf_log(file_path, target_atoms, output_file)
    else:
        print("Invalid target_atoms format. Please provide a dictionary in the correct format.")

if __name__ == "__main__":
    main()
