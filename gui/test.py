import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
from mysql.connector import Error
from difflib import SequenceMatcher
import requests
import pubchempy as pcp
from analysis.database import DatabaseManager
from utils.pubchem_api import get_compound_by_name

class SkincareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skincare Analysis System")

        self.db_manager = DatabaseManager()
        self.create_widgets()

    def create_widgets(self):
        # Ingredient Analysis Section
        ttk.Label(self.root, text="Ingredient Name:").grid(row=0, column=0, padx=10, pady=10)
        self.ingredient_name_var = tk.StringVar()
        self.ingredient_entry = ttk.Entry(self.root, textvariable=self.ingredient_name_var)
        self.ingredient_entry.grid(row=0, column=1, padx=10, pady=10)

        self.analyze_button = ttk.Button(self.root, text="Analyze Ingredient", command=self.analyze_ingredient)
        self.analyze_button.grid(row=0, column=2, padx=10, pady=10)

        self.result_text = tk.Text(self.root, height=15, width=60)
        self.result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Product Details Section
        ttk.Label(self.root, text="Product Barcode:").grid(row=2, column=0, padx=10, pady=10)
        self.barcode_var = tk.StringVar()
        self.barcode_entry = ttk.Entry(self.root, textvariable=self.barcode_var)
        self.barcode_entry.grid(row=2, column=1, padx=10, pady=10)

        self.get_product_button = ttk.Button(self.root, text="Get Product Details", command=self.get_product_details)
        self.get_product_button.grid(row=2, column=2, padx=10, pady=10)

        self.product_result_text = tk.Text(self.root, height=15, width=60)
        self.product_result_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Compare Products Section
        ttk.Label(self.root, text="Barcode 1:").grid(row=4, column=0, padx=10, pady=10)
        self.barcode1_var = tk.StringVar()
        self.barcode1_entry = ttk.Entry(self.root, textvariable=self.barcode1_var)
        self.barcode1_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(self.root, text="Barcode 2:").grid(row=5, column=0, padx=10, pady=10)
        self.barcode2_var = tk.StringVar()
        self.barcode2_entry = ttk.Entry(self.root, textvariable=self.barcode2_var)
        self.barcode2_entry.grid(row=5, column=1, padx=10, pady=10)

        self.compare_button = ttk.Button(self.root, text="Compare Products", command=self.compare_products)
        self.compare_button.grid(row=5, column=2, padx=10, pady=10)

        self.compare_result_text = tk.Text(self.root, height=15, width=60)
        self.compare_result_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def analyze_ingredient(self):
        ingredient_name = self.ingredient_name_var.get()
        if not ingredient_name:
            messagebox.showwarning("Input Error", "Please enter an ingredient name.")
            return

        compound_info = self.get_ingredient_info(ingredient_name)
        safety_rating = self.get_safety_rating(ingredient_name)
        
        if compound_info and 'error' in compound_info:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error analyzing ingredient '{ingredient_name}': {compound_info['error']}")
        else:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Compound Information for '{ingredient_name}':\n{compound_info}")
            self.result_text.insert(tk.END, f"\nSafety Rating: {safety_rating}")

    def get_ingredient_info(self, ingredient):
        try:
            response = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{ingredient}/JSON")
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 404:
                return {"error": "Not Found"}
            elif response.status_code == 400:
                return {"error": "Bad Request"}
            else:
                return {"error": "Error"}
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}

    def get_safety_rating(self, ingredient):
        # Implement the logic to fetch the safety rating
        # This is a placeholder function
        try:
            # Simulated response; replace with actual logic to fetch safety rating
            safety_rating = "Safe"  # or fetch from your database or API
            return safety_rating
        except Exception as e:
            return f"Error: {str(e)}"

    def get_product_details(self):
        barcode = self.barcode_var.get()
        if not barcode:
            messagebox.showwarning("Input Error", "Please enter a barcode.")
            return

        product = self.db_manager.get_product_by_barcode(barcode)
        if product:
            self.product_result_text.delete(1.0, tk.END)
            product_details = f"Product Details:\n{product}"
            # Append safety rating if available
            safety_rating = self.get_product_safety_rating(barcode)
            if safety_rating:
                product_details += f"\nSafety Rating: {safety_rating}"
            self.product_result_text.insert(tk.END, product_details)
        else:
            self.product_result_text.delete(1.0, tk.END)
            self.product_result_text.insert(tk.END, f"Product with barcode '{barcode}' not found.")

    def get_product_safety_rating(self, barcode):
        # Implement the logic to fetch the safety rating for the product
        # This is a placeholder function
        try:
            # Simulated response; replace with actual logic to fetch safety rating
            safety_rating = "Safe"  # or fetch from your database or API
            return safety_rating
        except Exception as e:
            return f"Error: {str(e)}"

    def compare_products(self):
        barcode1 = self.barcode1_var.get()
        barcode2 = self.barcode2_var.get()
        if not barcode1 or not barcode2:
            messagebox.showwarning("Input Error", "Please enter both barcodes.")
            return

        result = self.compare_product_ingredients(barcode1, barcode2)
        if 'error' in result:
            self.compare_result_text.delete(1.0, tk.END)
            self.compare_result_text.insert(tk.END, result['error'])
        else:
            self.compare_result_text.delete(1.0, tk.END)
            self.compare_result_text.insert(tk.END, f"Comparison Result:\n{result}")

    def get_ingredients_from_product(self, barcode):
        product = self.db_manager.get_product_by_barcode(barcode)
        if product:
            ingredient_list = product.get('ingredient_list', '')
            return [ingredient.strip() for ingredient in ingredient_list.split(',')] if ingredient_list else []
        return []

    def compare_ingredients(self, ingredients1, ingredients2):
        combined_ingredients1 = ' '.join(ingredients1)
        combined_ingredients2 = ' '.join(ingredients2)
        return SequenceMatcher(None, combined_ingredients1, combined_ingredients2).ratio()

    def compare_product_ingredients(self, barcode1, barcode2):
        ingredients1 = self.get_ingredients_from_product(barcode1)
        ingredients2 = self.get_ingredients_from_product(barcode2)

        if ingredients1 and ingredients2:
            similarity_score = self.compare_ingredients(ingredients1, ingredients2)

            set1 = set(ingredients1)
            set2 = set(ingredients2)
            common_ingredients = list(set1.intersection(set2))
            unique_ingredients1 = list(set1.difference(set2))
            unique_ingredients2 = list(set2.difference(set1))

            return {
                'barcode1': barcode1,
                'barcode2': barcode2,
                'similarity_score': similarity_score,
                'ingredients1': ingredients1,
                'ingredients2': ingredients2,
                'common_ingredients': common_ingredients,
                'unique_ingredients1': unique_ingredients1,
                'unique_ingredients2': unique_ingredients2
            }
        else:
            return {'error': 'One or both products not found or have no ingredients'}

if __name__ == "__main__":
    root = tk.Tk()
    app = SkincareApp(root)
    root.mainloop()
