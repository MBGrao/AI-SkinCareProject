import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import cv2
from PIL import Image, ImageTk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import numpy as np
import pytesseract
from datetime import datetime
import requests
from analysis.database import DatabaseManager
from analysis.ingredient_analysis import get_ingredient_info
from analysis.safety_ratings import determine_safety_rating
from analysis.nlp_similarity import compare_product_ingredients_nlp
from utils.pubchem_api import get_compound_by_name

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SkincareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skincare Analysis System")
        self.root.geometry("800x600")
        
        # Database Manager
        self.db_manager = DatabaseManager()
        self.db_manager.create_table()
        
        # Video capture setup
        self.video_source = 0
        self.vid = MyVideoCapture(self.video_source)
        self.canvas = tk.Canvas(self.root, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # GUI buttons
        self.btn_capture = tk.Button(self.root, text="Capture Image", width=20, command=self.capture_image)
        self.btn_capture.pack(anchor=tk.CENTER, expand=True)

        self.btn_upload = tk.Button(self.root, text="Upload Image", width=20, command=self.upload_image)
        self.btn_upload.pack(anchor=tk.CENTER, expand=True)

        self.btn_detect_text = tk.Button(self.root, text="Detect Text", width=20, command=self.detect_text)
        self.btn_detect_text.pack(anchor=tk.CENTER, expand=True)

        self.btn_analyze_ingredients = tk.Button(self.root, text="Analyze Ingredients", width=20, command=self.analyze_ingredients)
        self.btn_analyze_ingredients.pack(anchor=tk.CENTER, expand=True)

        self.btn_quit = tk.Button(self.root, text="Quit", width=20, command=self.quit_app)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

        # Text output widget
        self.text_output = tk.Text(self.root, wrap=tk.WORD, height=10, width=80)
        self.text_output.pack(pady=10)

        # Results TreeView
        self.results_tree = ttk.Treeview(self.root, columns=("Ingredient", "Info", "Safety Rating"), show='headings')
        self.results_tree.heading("Ingredient", text="Ingredient")
        self.results_tree.heading("Info", text="Info")
        self.results_tree.heading("Safety Rating", text="Safety Rating")
        self.results_tree.pack(fill=tk.BOTH, expand=True)

        self.update()

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.root.after(10, self.update)

    def capture_image(self):
        ret, frame = self.vid.get_frame()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(os.getcwd(), "product_images", f"captured_image_{timestamp}.jpg")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            self.image_path = save_path
            messagebox.showinfo("Image Capture", f"Image saved to {save_path}")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")])
        if file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(os.getcwd(), "product_images", f"uploaded_image_{timestamp}.jpg")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            shutil.copy(file_path, save_path)
            self.image_path = save_path
            messagebox.showinfo("Image Upload", f"Image uploaded and saved to {save_path}")

    def detect_text(self):
        if not hasattr(self, 'image_path') or not self.image_path:
            messagebox.showerror("Error", "No image loaded or captured")
            return

        try:
            image = cv2.imread(self.image_path)
            # Load the pre-trained EAST text detector model
            east_model_path = "../models/frozen_east_text_detection.pb"
            net = cv2.dnn.readNet(east_model_path)

            orig = image.copy()
            (H, W) = orig.shape[:2]
            newW, newH = (W // 32) * 32, (H // 32) * 32
            resized_image = cv2.resize(orig, (newW, newH))

            layer_names = [
                "feature_fusion/Conv_7/Sigmoid",
                "feature_fusion/concat_3"
            ]

            blob = cv2.dnn.blobFromImage(resized_image, 1.0, (newW, newH), (123.68, 116.78, 103.94), swapRB=True, crop=False)
            net.setInput(blob)
            (scores, geometry) = net.forward(layer_names)

            rects, confidences = self.decode_predictions(scores, geometry)
            boxes = cv2.dnn.NMSBoxes(rects, confidences, 0.5, 0.4)

            self.detected_text_boxes = []
            text_output = []
            if len(boxes) > 0:
                for i in boxes.flatten():
                    startX, startY, endX, endY = rects[i]
                    cv2.rectangle(resized_image, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    self.detected_text_boxes.append((startX, startY, endX, endY))

                    # Extract text from each detected box
                    roi = resized_image[startY:endY, startX:endX]
                    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    text = pytesseract.image_to_string(roi_rgb, lang='eng')
                    text_output.append(text.strip())

            detected_text = "\n".join(text_output)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, detected_text)

            self.display_image(resized_image)
        except Exception as e:
            messagebox.showerror("OCR Processing Error", f"An error occurred: {str(e)}")

    def decode_predictions(self, scores, geometry):
        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []

        for y in range(0, numRows):
            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]

            for x in range(0, numCols):
                if scoresData[x] < 0.5:
                    continue

                (offsetX, offsetY) = (x * 4.0, y * 4.0)
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])

        return rects, confidences

    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def analyze_ingredients(self):
        if not hasattr(self, 'detected_text_boxes') or not self.detected_text_boxes:
            messagebox.showerror("Error", "No text detected to analyze")
            return

        detected_text = self.text_output.get(1.0, tk.END).strip()
        ingredients = detected_text.split('\n')

        self.results_tree.delete(*self.results_tree.get_children())
        self.display_results(ingredients)

    def display_results(self, ingredients):
        for ingredient in ingredients:
            try:
                ingredient_info = get_ingredient_info(ingredient)
                safety_rating = determine_safety_rating(ingredient_info)
                self.results_tree.insert("", "end", values=(ingredient, ingredient_info, safety_rating))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while analyzing ingredient '{ingredient}': {str(e)}")

    def quit_app(self):
        self.root.destroy()

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            print("Error: Unable to open video source.")
            sys.exit()

        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame(self):
        ret, frame = self.vid.read()
        if ret:
            return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = SkincareApp(root)
    root.mainloop()
