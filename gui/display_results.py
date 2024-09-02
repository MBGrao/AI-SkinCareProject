import tkinter as tk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tkinter import ttk, messagebox
from analysis.ingredient_analysis import get_ingredient_info
from analysis.safety_ratings import get_safety_rating
from analysis.nlp_similarity import get_similar_products
from utils.pubchem_api import get_compound_by_name

class DisplayResults:
    def __init__(self, root, ingredients):
        self.root = root
        self.ingredients = ingredients
        self.create_widgets()

    def create_widgets(self):
        self.root.title("Skincare Analysis Results")

        self.tree = ttk.Treeview(self.root, columns=("Ingredient", "Info", "Safety Rating"), show='headings')
        self.tree.heading("Ingredient", text="Ingredient")
        self.tree.heading("Info", text="Info")
        self.tree.heading("Safety Rating", text="Safety Rating")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_tree()

        self.similar_products_button = ttk.Button(self.root, text="Find Similar Products", command=self.find_similar_products)
        self.similar_products_button.pack(pady=10)

    def populate_tree(self):
        for ingredient in self.ingredients:
            try:
                ingredient_info = get_ingredient_info(ingredient)
                safety_rating = get_safety_rating(ingredient)
                self.tree.insert("", "end", values=(ingredient, ingredient_info, safety_rating))
            except Exception as e:
                print(f"Error retrieving information for {ingredient}: {e}")
                self.tree.insert("", "end", values=(ingredient, "Error retrieving info", "Unknown"))

    def find_similar_products(self):
        try:
            similar_products = get_similar_products(self.ingredients)
            if similar_products:
                self.show_similar_products(similar_products)
            else:
                messagebox.showinfo("No Results", "No similar products found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching for similar products: {e}")

    def show_similar_products(self, similar_products):
        top = tk.Toplevel(self.root)
        top.title("Similar Products")

        tree = ttk.Treeview(top, columns=("Product Name", "Similarity Score"), show='headings')
        tree.heading("Product Name", text="Product Name")
        tree.heading("Similarity Score", text="Similarity Score")
        tree.pack(fill=tk.BOTH, expand=True)

        for product, score in similar_products:
            tree.insert("", "end", values=(product, score))

        close_button = ttk.Button(top, text="Close", command=top.destroy)
        close_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    ingredients = ["Water", "Glycerin", "Aloe Vera"]  # Example ingredients
    app = DisplayResults(root, ingredients)
    root.mainloop()
