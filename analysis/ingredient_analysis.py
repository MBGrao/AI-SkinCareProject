import requests
import mysql.connector
from difflib import SequenceMatcher
import sys
import os

# Adding the parent directory to sys.path to ensure the correct imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importing get_compound_by_name from utils.pubchem_api
from utils.pubchem_api import get_compound_by_name

# Importing DatabaseManager from the analysis.database module
from analysis.database import DatabaseManager

def get_product_by_barcode(connection, barcode):
    """
    Retrieve product details by barcode from the database.
    Parameters:
        connection (mysql.connector.connection.MySQLConnection): The database connection.
        barcode (str): The barcode of the product to retrieve.
    Returns:
        dict: A dictionary containing product details.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE barcode = %s"
        cursor.execute(query, (barcode,))
        product = cursor.fetchone()
        cursor.close()
        return product
    except mysql.connector.Error as err:
        print(f"Error fetching product by barcode: {err}")
        return None

def get_ingredient_info(ingredient):
    try:
        response = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{ingredient}/JSON")
        if response.status_code == 200:
            data = response.json()
            # Process data
            return data  # Return the actual data here
        elif response.status_code == 404:
            print(f"Ingredient '{ingredient}' not found.")
            return {"error": "Not Found"}
        elif response.status_code == 400:
            print(f"Bad request for ingredient '{ingredient}'.")
            return {"error": "Bad Request"}
        else:
            print(f"Unexpected status code {response.status_code} for ingredient '{ingredient}'.")
            return {"error": "Error"}
    except Exception as e:
        print(f"Exception occurred while fetching data for ingredient '{ingredient}': {str(e)}")
        return {"error": "Exception"}

def analyze_ingredient(ingredient_name):
    """
    Analyze a single ingredient to get its compound information from PubChem.
    Parameters:
        ingredient_name (str): The name of the ingredient to analyze.
    Returns:
        dict: A dictionary containing compound information.
    """
    compound_info = get_ingredient_info(ingredient_name)
    if compound_info and 'error' in compound_info:
        print(f"Error analyzing ingredient '{ingredient_name}': {compound_info['error']}")
    return compound_info if compound_info is not None else {"error": "No information available"}


def compare_ingredients(ingredients1, ingredients2):
    """
    Compare two lists of ingredients to calculate similarity.
    Parameters:
        ingredients1 (list): The first list of ingredient names.
        ingredients2 (list): The second list of ingredient names.
    Returns:
        float: A similarity score between 0 and 1.
    """
    combined_ingredients1 = ' '.join(ingredients1)
    combined_ingredients2 = ' '.join(ingredients2)
    return SequenceMatcher(None, combined_ingredients1, combined_ingredients2).ratio()

def get_ingredients_from_product(barcode, connection):
    """
    Retrieve ingredient list from a product by barcode.
    Parameters:
        barcode (str): The barcode of the product to retrieve.
        connection (mysql.connector.connection.MySQLConnection): The database connection.
    Returns:
        list: A list of ingredient names.
    """
    product = get_product_by_barcode(connection, barcode)
    if product:
        ingredient_list = product.get('ingredient_list', '')
        return [ingredient.strip() for ingredient in ingredient_list.split(',')] if ingredient_list else []
    print(f"Product with barcode '{barcode}' not found.")
    return []

def compare_product_ingredients(barcode1, barcode2, connection):
    """
    Compare the ingredients of two products.
    Parameters:
        barcode1 (str): The barcode of the first product.
        barcode2 (str): The barcode of the second product.
        connection (mysql.connector.connection.MySQLConnection): The database connection.
    Returns:
        dict: A dictionary containing the similarity score, ingredient details, unique ingredients, and common ingredients.
    """
    ingredients1 = get_ingredients_from_product(barcode1, connection)
    ingredients2 = get_ingredients_from_product(barcode2, connection)
    
    if ingredients1 and ingredients2:
        similarity_score = compare_ingredients(ingredients1, ingredients2)
        
        # Calculate unique and common ingredients
        set1 = set(ingredients1)
        set2 = set(ingredients2)
        common_ingredients = list(set1.intersection(set2))
        unique_ingredients1 = list(set1.difference(set2))
        unique_ingredients2 = list(set2.difference(set1))
        
        result = {
            'barcode1': barcode1,
            'barcode2': barcode2,
            'similarity_score': similarity_score,
            'ingredients1': ingredients1,
            'ingredients2': ingredients2,
            'common_ingredients': common_ingredients,
            'unique_ingredients1': unique_ingredients1,
            'unique_ingredients2': unique_ingredients2
        }
        return result
    else:
        return {'error': 'One or both products not found or have no ingredients'}

def analyze_ingredient_list(ingredient_list):
    """
    Analyze a list of ingredients to get compound information for each.
    Parameters:
        ingredient_list (list): A list of ingredient names.
    Returns:
        dict: A dictionary containing compound information for each ingredient.
    """
    analysis_results = {}
    for ingredient in ingredient_list:
        compound_info = analyze_ingredient(ingredient)
        if compound_info:
            analysis_results[ingredient] = compound_info
        else:
            analysis_results[ingredient] = {'error': 'Compound information not found'}
    return analysis_results

def main():
    """
    Main function for demonstration purposes.
    """
    # Example usage:
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='skincare_db',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            # Compare ingredients of two products
            barcode1 = '012345678932'
            barcode2 = '012345678912'
            comparison_result = compare_product_ingredients(barcode1, barcode2, connection)
            print("Comparison Result:", comparison_result)
            
            # Analyze a list of ingredients
            ingredients = ['Aspirin']
            analysis_results = analyze_ingredient_list(ingredients)
            print("Ingredient Analysis Results:", analysis_results)
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
