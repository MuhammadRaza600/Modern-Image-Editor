import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Function to apply filters
def apply_filter(image, filter_type, brightness=1.0, contrast=1.0):
    if image is None:
        return None

    img = image.copy()

    if filter_type == "grayscale":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    elif filter_type == "blur":
        img = cv2.GaussianBlur(img, (15, 15), 0)

    elif filter_type == "sharpen":
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    elif filter_type == "sepia":
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        img = cv2.transform(img.astype(np.float32), sepia_filter)
        img = np.clip(img, 0, 255).astype(np.uint8)

    elif filter_type == "edge":
        edges = cv2.Canny(img, 100, 200)
        img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    elif filter_type == "cartoon":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 250, 250)
        img = cv2.bitwise_and(color, color, mask=edges)

    elif filter_type == "sketch":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        img = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    # Apply brightness and contrast
    img = cv2.convertScaleAbs(img, alpha=contrast, beta=int((brightness - 1.0) * 100))
    return img

# Load image
def open_image():
    global img, display_img
    path = filedialog.askopenfilename()
    if path:
        img = cv2.imread(path)
        display_img = img.copy()
        show_image(display_img)

# Save image
def save_image():
    if display_img is not None:
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            cv2.imwrite(path, display_img)
            messagebox.showinfo("Saved", f"Image saved at {path}")

# Update display image with selected filter
def update_image(filter_name=None):
    global display_img
    brightness = brightness_scale.get()
    contrast = contrast_scale.get()
    display_img = apply_filter(img, filter_name, brightness, contrast)
    show_image(display_img)

# Display image in panel
def show_image(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(rgb)
    img_pil = img_pil.resize((450, 350))
    imgtk = ImageTk.PhotoImage(img_pil)
    panel.config(image=imgtk)
    panel.image = imgtk

# --- GUI Setup ---
root = tk.Tk()
root.title("Image Processing Application")
root.geometry("1000x600")

btn_frame = tk.Frame(root)
btn_frame.pack(side="left", padx=10)

tk.Button(btn_frame, text="Open Image", command=open_image, width=20).pack(pady=5)
tk.Button(btn_frame, text="Grayscale", command=lambda: update_image("grayscale"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Blur", command=lambda: update_image("blur"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Sharpen", command=lambda: update_image("sharpen"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Sepia", command=lambda: update_image("sepia"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Edge Detection", command=lambda: update_image("edge"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Cartoon", command=lambda: update_image("cartoon"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Sketch", command=lambda: update_image("sketch"), width=20).pack(pady=5)
tk.Button(btn_frame, text="Save Image", command=save_image, width=20).pack(pady=10)

# Brightness/Contrast sliders
brightness_scale = tk.Scale(btn_frame, from_=0.5, to=2.0, resolution=0.1,
                            label="Brightness", orient="horizontal", length=180)
brightness_scale.set(1.0)
brightness_scale.pack(pady=10)

contrast_scale = tk.Scale(btn_frame, from_=0.5, to=2.0, resolution=0.1,
                          label="Contrast", orient="horizontal", length=180)
contrast_scale.set(1.0)
contrast_scale.pack(pady=10)

# Image display panel
panel = tk.Label(root)
panel.pack(padx=10, pady=10, side="right")

img = None
display_img = None

root.mainloop()
