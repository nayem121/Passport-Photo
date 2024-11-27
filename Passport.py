import cv2
import os
import sys
import numpy as np
from tkinter import Tk, Label, Button, Scale, Checkbutton, IntVar, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from rembg import remove
import webbrowser
import threading
import queue


class PassportPhoto:
    def __init__(self, master):
        self.master = master
        master.title("Passport Photo Maker Studio | V0.1")

        # UI elements
        self.output_label = Label(master, text="Output Image:")
        self.output_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.output_image_label = Label(master)
        self.output_image_label.grid(row=1, column=0, rowspan=10, padx=5, pady=5, sticky="w")

        self.input_label = Label(master, text="Input Image:")
        self.input_label.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.input_button = Button(master, text="Choose Image", command=self.load_image)
        self.input_button.grid(row=0, column=2, padx=5, pady=5)

        self.scale_label = Label(master, text="Upscale Level:")
        self.scale_label.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        self.scale_var = IntVar(value=2)
        self.scale_slider = Scale(master, from_=2, to=8, orient="horizontal", variable=self.scale_var)
        self.scale_slider.grid(row=1, column=2, padx=5, pady=5)

        self.denoise_var = IntVar()
        self.denoise_check = Checkbutton(master, text="Remove Grain", variable=self.denoise_var)
        self.denoise_check.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        self.passport_size_var = IntVar(value=1)
        self.passport_size_check = Checkbutton(master, text="Passport size (413px X 531px)", variable=self.passport_size_var)
        self.passport_size_check.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        self.resize_200px_var = IntVar()
        self.resize_200px_check = Checkbutton(master, text="Application size 200px X 200px", variable=self.resize_200px_var)
        self.resize_200px_check.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

        self.resize_300px_var = IntVar()
        self.resize_300px_check = Checkbutton(master, text="Application size  300px X 300px", variable=self.resize_300px_var)
        self.resize_300px_check.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        self.process_button = Button(master, text="Process", command=self.start_process_thread)
        self.process_button.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

        self.save_button = Button(master, text="Save Image", command=self.save_image, state="disabled")
        self.save_button.grid(row=7, column=1, columnspan=2, padx=5, pady=5)

        self.progress_label = Label(master, text="")
        self.progress_label.grid(row=8, column=1, columnspan=2, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=9, column=1, columnspan=2, padx=5, pady=5)

        self.copyright_label = Label(
            master, text="Version 0.1 | © Reserved by Nayem Uddin Chowdhury",
            fg="blue", cursor="hand2"
        )
        self.copyright_label.grid(row=10, column=1, columnspan=2, padx=5, pady=5)
        self.copyright_label.bind("<Button-1>", lambda e: self.open_link())

        # Load Haarcascade dynamically based on execution environment
        haarcascade_path = os.path.join(sys._MEIPASS, 'haarcascade_frontalface_default.xml') \
            if hasattr(sys, '_MEIPASS') else 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(haarcascade_path)

        self.original_image = None
        self.upscaled_image = None
        self.progress_queue = queue.Queue()
        self.processing_thread = None

    def load_image(self):
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select an image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("all files", "*.*"))
        )

        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                print("Error loading image.")
                return

            self.display_image(self.original_image, self.output_image_label)
            self.save_button.config(state="normal")

    def start_process_thread(self):
        if self.processing_thread and self.processing_thread.is_alive():
            print("Processing already in progress.")
            return

        self.processing_thread = threading.Thread(target=self.process_image)
        self.processing_thread.start()
        self.master.after(100, self.check_queue)

    def check_queue(self):
        try:
            while not self.progress_queue.empty():
                step, message = self.progress_queue.get_nowait()
                self.progress_bar['value'] = step
                self.progress_label.config(text=message)
                self.master.update_idletasks()
        except queue.Empty:
            pass
        finally:
            if self.processing_thread.is_alive():
                self.master.after(100, self.check_queue)

    def update_progress(self, step, message):
        self.progress_queue.put((step, message))

    def process_image(self):
        if self.original_image is not None:
            try:
                self.update_progress(10, "Detecting face...")
                gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)

                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
                )

                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    cropped_img = self.original_image[max(0, y - int(h * 0.5)):y + h + int(h * 1.0),
                                                      max(0, x - int(w * 0.5)):x + w + int(w * 0.5)]
                else:
                    print("No faces detected.")
                    cropped_img = self.original_image

                self.update_progress(30, "Removing background...")
                pil_img = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
                transparent_bg_img = remove(pil_img)
                new_bg_img = Image.new("RGBA", transparent_bg_img.size, (3, 177, 252, 255))
                final_img = Image.alpha_composite(new_bg_img, transparent_bg_img).convert("RGB")
                processed_img = cv2.cvtColor(np.array(final_img), cv2.COLOR_RGB2BGR)

                self.update_progress(50, "Removing grain...")
                if self.denoise_var.get():
                    processed_img = cv2.fastNlMeansDenoisingColored(processed_img, None, 10, 10, 7, 21)

                self.update_progress(70, "Upscaling image...")
                scale = self.scale_var.get()
                self.upscaled_image = cv2.resize(processed_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

                if self.passport_size_var.get():
                    self.upscaled_image = cv2.resize(self.upscaled_image, (413, 531), interpolation=cv2.INTER_AREA)
                elif self.resize_200px_var.get():
                    self.upscaled_image = cv2.resize(self.upscaled_image, (200, 200), interpolation=cv2.INTER_AREA)
                elif self.resize_300px_var.get():
                    self.upscaled_image = cv2.resize(self.upscaled_image, (300, 300), interpolation=cv2.INTER_AREA)

                self.display_image(self.upscaled_image, self.output_image_label)
                self.update_progress(100, "Processing complete!")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.update_progress(0, "An error occurred")

    def save_image(self):
        if self.upscaled_image is not None:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=(("JPEG", "*.jpg"), ("PNG", "*.png"), ("All Files", "*.*"))
            )
            if save_path:
                cv2.imwrite(save_path, self.upscaled_image)

    def display_image(self, image, label, max_width=400, max_height=300):
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        width, height = pil_image.size
        aspect_ratio = width / height
        if width > max_width or height > max_height:
            if aspect_ratio > 1:
                width = max_width
                height = int(max_width / aspect_ratio)
            else:
                height = max_height
                width = int(max_height * aspect_ratio)
        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(pil_image)
        label.config(image=img_tk)
        label.image = img_tk

    def open_link(self):
        webbrowser.open("https://github.com/nayem121/")


if __name__ == "__main__":
    root = Tk()
    app = PassportPhoto(root)
    root.mainloop()
