import tensorflow_hub as hub
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.database import DatabaseManager

# Load the model once globally
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

def embed_sentences(sentences):
    """
    Embed a list of sentences using Universal Sentence Encoder.
    Parameters:
        sentences (list): A list of sentences to embed.
    Returns:
        np.ndarray: The embeddings of the sentences.
    """
    embeddings = embed(sentences)
    return embeddings.numpy()

def compute_similarity(embedding1, embedding2):
    """
    Compute the cosine similarity between two embeddings.
    Parameters:
        embedding1 (np.ndarray): The first embedding.
        embedding2 (np.ndarray): The second embedding.
    Returns:
        float: The cosine similarity score between the two embeddings.
    """
    return cosine_similarity([embedding1], [embedding2])[0][0]

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

def compare_product_ingredients_nlp(barcode1, barcode2, connection):
    """
    Compare the ingredients of two products using NLP-based similarity.
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
        combined_ingredients1 = ', '.join(ingredients1)
        combined_ingredients2 = ', '.join(ingredients2)
        embedding1 = embed_sentences([combined_ingredients1])[0]
        embedding2 = embed_sentences([combined_ingredients2])[0]
        similarity_score = compute_similarity(embedding1, embedding2)
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

def main():
    pass

if __name__ == "__main__":
    main()
