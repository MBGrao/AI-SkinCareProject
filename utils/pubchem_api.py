import pubchempy as pcp
import json

def get_compound_by_name(name):
    """
    Retrieve compound information by name from PubChem.
    Parameters:
        name (str): The name of the compound to search for.
    Returns:
        dict: A dictionary containing compound information.
    """
    try:
        compounds = pcp.get_compounds(name, namespace='name')
        if compounds:
            compound = compounds[0]
            compound_info = {
                'CID': compound.cid,
                'Name': compound.iupac_name,
                'Molecular_Formula': compound.molecular_formula,
                'Molecular_Weight': compound.molecular_weight,
                'InChI': compound.inchi,
                'InChIKey': compound.inchikey,
                'Canonical_SMILES': compound.canonical_smiles,
                'Synonyms': compound.synonyms
            }
            return compound_info
        else:
            print(f"No compound found for name '{name}'")
            return None
    except pcp.PubChemPyError as e:
        print(f"Error retrieving compound by name: {e}")
        return None

def get_compound_by_cid(cid):
    """
    Retrieve compound information by CID from PubChem.
    Parameters:
        cid (int): The CID of the compound to search for.
    Returns:
        dict: A dictionary containing compound information.
    """
    try:
        compound = pcp.Compound.from_cid(cid)
        compound_info = {
            'CID': compound.cid,
            'Name': compound.iupac_name,
            'Molecular_Formula': compound.molecular_formula,
            'Molecular_Weight': compound.molecular_weight,
            'InChI': compound.inchi,
            'InChIKey': compound.inchikey,
            'Canonical_SMILES': compound.canonical_smiles,
            'Synonyms': compound.synonyms
        }
        return compound_info
    except pcp.PubChemPyError as e:
        print(f"Error retrieving compound by CID: {e}")
        return None

def get_safety_and_toxicity_info(cid):
    """
    Retrieve safety and toxicity information for a compound from PubChem.
    Parameters:
        cid (int): The CID of the compound.
    Returns:
        dict: A dictionary containing safety and toxicity information.
    """
    try:
        # Retrieve compound information (for reference)
        compound = pcp.Compound.from_cid(cid)
        
        # Example placeholders for safety and toxicity information
        # Note: Actual retrieval may require different API calls or additional data sources
        safety_info = {
            'CID': compound.cid,
            'Toxicity': "Not directly available in PubChemPy API",
            'Safety': "Not directly available in PubChemPy API"
        }
        return safety_info
    except pcp.PubChemPyError as e:
        print(f"Error retrieving safety and toxicity info: {e}")
        return None

def save_compound_info_to_json(compound_info, filename):
    """
    Save compound information to a JSON file.
    Parameters:
        compound_info (dict): The compound information to save.
        filename (str): The name of the file to save the information.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(compound_info, file, indent=4)
        print(f"Compound information saved to {filename}")
    except Exception as e:
        print(f"Error saving compound info to JSON: {e}")

def main():
    """
    Main function for demonstration purposes.
    """
    # Example usage:
    name = 'Aspirin'
    compound_info = get_compound_by_name(name)
    if compound_info:
        print("Compound Info by Name:", compound_info)
        save_compound_info_to_json(compound_info, 'aspirin_info.json')
    
    cid = 2244  # Example CID for Aspirin
    compound_info = get_compound_by_cid(cid)
    if compound_info:
        print("Compound Info by CID:", compound_info)
        save_compound_info_to_json(compound_info, 'aspirin_cid_info.json')
    
    safety_info = get_safety_and_toxicity_info(cid)
    if safety_info:
        print("Safety and Toxicity Info:", safety_info)
        save_compound_info_to_json(safety_info, 'aspirin_safety_info.json')

if __name__ == "__main__":
    main()
