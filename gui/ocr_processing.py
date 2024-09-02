import cv2
import numpy as np
import pytesseract
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class OCRProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Processing")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack()

        self.btn_load_image = tk.Button(self.root, text="Load Image", width=20, command=self.load_image)
        self.btn_load_image.pack(anchor=tk.CENTER, expand=True)

        self.btn_detect_text = tk.Button(self.root, text="Detect Text", width=20, command=self.detect_text)
        self.btn_detect_text.pack(anchor=tk.CENTER, expand=True)

        self.btn_process_ocr = tk.Button(self.root, text="Process OCR", width=20, command=self.process_ocr)
        self.btn_process_ocr.pack(anchor=tk.CENTER, expand=True)

        self.image_path = None
        self.image = None
        self.detected_text_boxes = None
        self.text_result = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")])
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(file_path)
            self.display_image(self.image)

    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def detect_text(self):
        if self.image is None:
            messagebox.showerror("Error", "No image loaded")
            return

        try:
            # Load the pre-trained EAST text detector model
            east_model_path = "../models/frozen_east_text_detection.pb"
            net = cv2.dnn.readNet(east_model_path)

            orig = self.image.copy()

            # Ensure that the image size is a multiple of 32
            (H, W) = orig.shape[:2]
            newW, newH = (W // 32) * 32, (H // 32) * 32
            resized_image = cv2.resize(orig, (newW, newH))

            # Determine the output layer names that we need from the EAST model
            layer_names = [
                "feature_fusion/Conv_7/Sigmoid",
                "feature_fusion/concat_3"
            ]

            # Construct a blob from the image and perform a forward pass of the model
            blob = cv2.dnn.blobFromImage(resized_image, 1.0, (newW, newH), (123.68, 116.78, 103.94), swapRB=True, crop=False)
            net.setInput(blob)
            (scores, geometry) = net.forward(layer_names)

            # Decode the predictions
            rects, confidences = self.decode_predictions(scores, geometry)

            # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
            boxes = cv2.dnn.NMSBoxes(rects, confidences, 0.5, 0.4)

            self.detected_text_boxes = []
            if len(boxes) > 0:
                for i in boxes.flatten():
                    startX, startY, endX, endY = rects[i]
                    cv2.rectangle(resized_image, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    self.detected_text_boxes.append((startX, startY, endX, endY))

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

    def process_ocr(self):
        if self.image is None or self.detected_text_boxes is None:
            messagebox.showerror("Error", "No image or text detected")
            return

        # Initialize Tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

        (H, W) = self.image.shape[:2]  # Image dimensions
        text_output = []

        for (startX, startY, endX, endY) in self.detected_text_boxes:
            # Ensure the ROI is within image bounds
            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(W, endX)
            endY = min(H, endY)

            if startX < endX and startY < endY:
                roi = self.image[startY:endY, startX:endX]
                try:
                    text = pytesseract.image_to_string(roi, lang='eng')
                    text_output.append(text.strip())
                except Exception as e:
                    messagebox.showerror("OCR Processing Error", f"An error occurred while processing OCR: {str(e)}")
                    return

        self.text_result = "\n".join(text_output)
        self.show_text_result()

    def show_text_result(self):
        if self.text_result:
            text_window = tk.Toplevel(self.root)
            text_window.title("OCR Result")
            text_display = tk.Text(text_window, wrap=tk.WORD)
            text_display.insert(tk.END, self.text_result)
            text_display.pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("OCR Result", "No text detected")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRProcessingApp(root)
    root.mainloop()
