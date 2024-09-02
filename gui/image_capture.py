import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
import shutil

class ImageCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Capture")
        self.root.geometry("800x600")

        self.video_source = 0
        self.vid = MyVideoCapture(self.video_source)

        self.canvas = tk.Canvas(self.root, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        self.btn_capture = tk.Button(self.root, text="Capture", width=20, command=self.capture_image)
        self.btn_capture.pack(anchor=tk.CENTER, expand=True)

        self.btn_upload = tk.Button(self.root, text="Upload Image", width=20, command=self.upload_image)
        self.btn_upload.pack(anchor=tk.CENTER, expand=True)

        self.btn_quit = tk.Button(self.root, text="Quit", width=20, command=self.quit_app)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

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
            messagebox.showinfo("Image Capture", f"Image saved to {save_path}")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")])
        if file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(os.getcwd(), "product_images", f"uploaded_image_{timestamp}.jpg")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            shutil.copy(file_path, save_path)
            messagebox.showinfo("Image Upload", f"Image uploaded and saved to {save_path}")

    def quit_app(self):
        self.vid.__del__()
        self.root.quit()

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (False, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCaptureApp(root)
    root.mainloop()
