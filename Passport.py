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
        master.title("Passport Photo Maker Studio | V0.2")

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

        self.remove_bg_var = IntVar(value=1)
        self.remove_bg_check = Checkbutton(master, text="Remove Background", variable=self.remove_bg_var)
        self.remove_bg_check.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        self.denoise_var = IntVar()
        self.denoise_check = Checkbutton(master, text="Remove Grain", variable=self.denoise_var)
        self.denoise_check.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        # Grain Removal Level Slider
        self.denoise_level_label = Label(master, text="Adjust Level:")
        self.denoise_level_label.grid(row=4, column=1, padx=5, pady=5, sticky="e")

        self.denoise_level_var = IntVar(value=5)  # Default level is 5
        self.denoise_level_slider = Scale(master, from_=0, to=50, orient="horizontal", variable=self.denoise_level_var)
        self.denoise_level_slider.grid(row=4, column=2, padx=5, pady=5)

        self.passport_size_var = IntVar(value=1)
        self.passport_size_check = Checkbutton(master, text="Passport size (413px X 531px)", variable=self.passport_size_var)
        self.passport_size_check.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        self.resize_300px_var = IntVar()
        self.resize_300px_check = Checkbutton(master, text="Application size  300px X 300px", variable=self.resize_300px_var)
        self.resize_300px_check.grid(row=7, column=1, columnspan=2, padx=5, pady=5)

        self.resize_200px_var = IntVar()
        self.resize_200px_check = Checkbutton(master, text="Application size 200px X 200px", variable=self.resize_200px_var)
        self.resize_200px_check.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

        self.process_button = Button(master, text="Process", command=self.start_process_thread)
        self.process_button.grid(row=8, column=1, columnspan=2, padx=5, pady=5)

        self.save_button = Button(master, text="Save Image", command=self.save_image, state="disabled")
        self.save_button.grid(row=9, column=1, columnspan=2, padx=5, pady=5)

        self.progress_label = Label(master, text="")
        self.progress_label.grid(row=10, column=1, columnspan=2, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=11, column=1, columnspan=2, padx=5, pady=5)

        self.copyright_label = Label(
            master, text="Nayem Uddin Chowdhury © Reserved | V0.2",
            fg="blue", cursor="hand2"
        )
        self.copyright_label.grid(row=12, column=1, columnspan=2, padx=5, pady=5)
        self.copyright_label.bind("<Button-1>", lambda e: self.open_link())

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
                processed_img = self.original_image.copy()

                # Only perform face detection, cropping, and resizing if any size is selected
                if self.passport_size_var.get() or self.resize_200px_var.get() or self.resize_300px_var.get():
                    self.update_progress(10, "Detecting face...")
                    gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
                    )

                    if len(faces) > 0:
                        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])  # Largest face
                        cropped_img = self.original_image[max(0, y - int(h * 0.5)):y + h + int(h * 1.0),
                                                          max(0, x - int(w * 0.5)):x + w + int(w * 0.5)]
                    else:
                        cropped_img = self.original_image
                    processed_img = cropped_img

                # Background removal
                if self.remove_bg_var.get():
                    self.update_progress(30, "Removing background...")
                    pil_img = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
                    transparent_bg_img = remove(pil_img)
                    new_bg_img = Image.new("RGBA", transparent_bg_img.size, (3, 177, 252, 255))
                    final_img = Image.alpha_composite(new_bg_img, transparent_bg_img).convert("RGB")
                    processed_img = cv2.cvtColor(np.array(final_img), cv2.COLOR_RGB2BGR)

                # Denoising
                if self.denoise_var.get():
                    self.update_progress(50, "Removing grain...")
                    denoise_level = self.denoise_level_var.get()  # Get slider value
                    processed_img = cv2.fastNlMeansDenoisingColored(processed_img, None, denoise_level, denoise_level, 7, 21)

                # Upscaling
                self.update_progress(70, "Upscaling image...")
                scale = self.scale_var.get()
                processed_img = cv2.resize(processed_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

                # Resizing based on size checkboxes
                if self.passport_size_var.get():
                    processed_img = cv2.resize(processed_img, (413, 531), interpolation=cv2.INTER_AREA)
                elif self.resize_200px_var.get():
                    processed_img = cv2.resize(processed_img, (200, 200), interpolation=cv2.INTER_AREA)
                elif self.resize_300px_var.get():
                    processed_img = cv2.resize(processed_img, (300, 300), interpolation=cv2.INTER_AREA)

                # Display the final processed image
                self.upscaled_image = processed_img
                self.display_image(self.upscaled_image, self.output_image_label)
                self.update_progress(100, "Processing complete!")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.update_progress(0, "An error occurred")

    def save_image(self):
        if self.upscaled_image is not None:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*"))
            )
            if save_path:
                cv2.imwrite(save_path, self.upscaled_image)

    def display_image(self, image, label):
        resized = cv2.resize(image, (250, 250), interpolation=cv2.INTER_AREA)
        img = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

    def open_link(self):
        webbrowser.open_new("https://github.com/nayem121")

if __name__ == "__main__":
    root = Tk()
    app = PassportPhoto(root)
    root.mainloop()
