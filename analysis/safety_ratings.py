import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pubchempy as pcp
from analysis.database import DatabaseManager
from utils.pubchem_api import get_compound_by_name
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define safety rating thresholds
SAFETY_THRESHOLDS = {
    'High': 0.8,
    'Medium': 0.5,
    'Low': 0.2,
    'None': 0.0
}

def get_safety_and_toxicity_info(cid: int) -> Dict[str, Any]:
    """
    Retrieve safety and toxicity information for a compound from PubChem.
    Parameters:
        cid (int): The CID of the compound.
    Returns:
        Dict[str, Any]: A dictionary containing safety and toxicity information.
    """
    try:
        compound = pcp.Compound.from_cid(cid)
        safety_info = {
            'CID': compound.cid,
            'Toxicity': compound.toxicity or 'Unknown',
            'Safety': compound.safety or 'Unknown'
        }
        return safety_info
    except Exception as e:
        logging.error(f"Error retrieving safety and toxicity info: {e}")
        return {}

def determine_safety_rating(safety_info: Dict[str, Any]) -> str:
    """
    Determine the safety rating based on safety information.
    Parameters:
        safety_info (Dict[str, Any]): The safety information of the compound.
    Returns:
        str: The safety rating.
    """
    toxicity = safety_info.get('Toxicity', 'Unknown')
    if toxicity == 'Unknown':
        return 'None'
    elif toxicity in ['Very Low', 'Low']:
        return 'High'
    elif toxicity in ['Medium']:
        return 'Medium'
    elif toxicity in ['High', 'Very High']:
        return 'Low'
    else:
        return 'None'

def display_traffic_light(safety_rating: str) -> None:
    """
    Display the safety rating using a traffic light system.
    Parameters:
        safety_rating (str): The safety rating to display.
    """
    traffic_lights = {
        'High': '🟢',  # Green
        'Medium': '🟠', # Orange
        'Low': '🔴',   # Red
        'None': '⚫'   # Black
    }
    traffic_light = traffic_lights.get(safety_rating, '⚫')
    logging.info(f"Safety Rating: {safety_rating} {traffic_light}")

def analyze_product_safety(barcode: str) -> None:
    """
    Analyze the safety of a product based on its ingredients.
    Parameters:
        barcode (str): The barcode of the product to analyze.
    """
    conn = create_connection()
    if conn:
        product = get_product_by_barcode(conn, barcode)
        if product:
            ingredients = product['ingredient_list'].split(', ')
            for ingredient in ingredients:
                info = get_compound_by_name(ingredient)
                if info:
                    cid = info.get('CID')
                    if cid:
                        safety_info = get_safety_and_toxicity_info(cid)
                        if safety_info:
                            safety_rating = determine_safety_rating(safety_info)
                            update_product_safety_rating(barcode, safety_rating)
                            display_traffic_light(safety_rating)
        else:
            logging.warning(f"No product found with barcode '{barcode}'")
        close_connection(conn)
    else:
        logging.error("Failed to connect to the database")

def main():
    """
    Main function for demonstration purposes.
    """
    barcode = '012345678932'  # Replace with actual barcode
    analyze_product_safety(barcode)

if __name__ == "__main__":
    main()
