import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'skincare_db',
    'user': 'root',
    'password': ''
}

class DatabaseManager:
    def __init__(self):
        self.connection = self.create_connection()
    
    def create_connection(self):
        """Create and return a database connection."""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            print("Database connection successful")
            return connection
        except Error as e:
            print(f"Error: '{e}'")
            return None

    def create_table(self):
        """Create tables in the database."""
        cursor = self.connection.cursor()
        create_product_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            barcode VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            ingredient_list TEXT,
            safety_rating VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_product_table_query)
        create_similarity_table_query = """
        CREATE TABLE IF NOT EXISTS product_similarity (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id1 INT,
            product_id2 INT,
            similarity_score FLOAT,
            FOREIGN KEY (product_id1) REFERENCES products(id),
            FOREIGN KEY (product_id2) REFERENCES products(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_similarity_table_query)
        self.connection.commit()
        print("Tables created successfully")

    def insert_product(self, barcode, name, ingredient_list, safety_rating):
        """Insert a new product into the database."""
        cursor = self.connection.cursor()
        insert_product_query = """
        INSERT INTO products (barcode, name, ingredient_list, safety_rating)
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor.execute(insert_product_query, (barcode, name, ingredient_list, safety_rating))
            self.connection.commit()
            print("Product inserted successfully")
        except Error as e:
            print(f"Error: '{e}'")

    def get_product_by_barcode(self, barcode):
        """Retrieve a product by barcode."""
        cursor = self.connection.cursor(dictionary=True)
        select_product_query = """
        SELECT * FROM products WHERE barcode = %s
        """
        cursor.execute(select_product_query, (barcode,))
        result = cursor.fetchone()
        return result

    def insert_similarity(self, product_id1, product_id2, similarity_score):
        """Insert a similarity record into the database."""
        cursor = self.connection.cursor()
        insert_similarity_query = """
        INSERT INTO product_similarity (product_id1, product_id2, similarity_score)
        VALUES (%s, %s, %s)
        """
        try:
            cursor.execute(insert_similarity_query, (product_id1, product_id2, similarity_score))
            self.connection.commit()
            print("Similarity record inserted successfully")
        except Error as e:
            print(f"Error: '{e}'")

    def update_product_safety_rating(self, barcode, safety_rating):
        """Update the safety rating of a product in the database."""
        cursor = self.connection.cursor()
        update_query = """
        UPDATE products
        SET safety_rating = %s
        WHERE barcode = %s
        """
        try:
            cursor.execute(update_query, (safety_rating, barcode))
            self.connection.commit()
            print(f"Safety rating for product with barcode '{barcode}' updated to '{safety_rating}'")
        except Error as e:
            print(f"Error: '{e}'")

    def close_connection(self):
        """Close the database connection."""
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.create_table()
    # Further operations can be called on db_manager
