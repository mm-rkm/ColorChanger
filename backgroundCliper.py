import os
import sys
import numpy as np
import cv2
from PIL import Image
import tkinter as tk
from tkinter import filedialog, Scale, Button, Label, Frame
from tkinter.ttk import Progressbar
import threading

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover")
        self.root.geometry("800x600")
        
        # Variables
        self.input_path = None
        self.output_path = None
        self.target_color = None
        self.color_range = 30
        self.img = None
        self.img_display = None
        self.preview_img = None
        self.is_processing = False
        
        # Main frames
        self.control_frame = Frame(root, padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.image_frame = Frame(root)
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control elements
        self.create_controls()
        
        # Image display
        self.image_label = Label(self.image_frame, text="No image selected")
        self.image_label.pack(expand=True)
        
        # Status bar
        self.status_bar = Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Progress bar (hidden initially)
        self.progress = Progressbar(root, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        
    def create_controls(self):
        # Button to select input image
        self.select_btn = Button(self.control_frame, text="Select Image", command=self.select_image)
        self.select_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Color range slider
        self.range_label = Label(self.control_frame, text="Color Range:")
        self.range_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.range_slider = Scale(self.control_frame, from_=1, to=200, orient=tk.HORIZONTAL, 
                                  length=200, command=self.update_range)
        self.range_slider.set(self.color_range)
        self.range_slider.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Process button
        self.process_btn = Button(self.control_frame, text="Process & Save", 
                                 command=self.process_image, state=tk.DISABLED)
        self.process_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Color indicator
        self.color_indicator = Label(self.control_frame, text="   ", bg="white", 
                                    relief=tk.SUNKEN, width=3)
        self.color_indicator.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.color_label = Label(self.control_frame, text="Selected Color:")
        self.color_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
    def select_image(self):
        self.input_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if not self.input_path:
            return
        
        self.img = cv2.imread(self.input_path)
        if self.img is None:
            self.status_bar.config(text=f"Error: Could not read image at {self.input_path}")
            return
            
        self.img_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.update_display(self.img_rgb)
        self.status_bar.config(text=f"Image loaded: {os.path.basename(self.input_path)}")
        self.process_btn.config(state=tk.DISABLED)
        
    def update_display(self, img, resize=True):
        h, w = img.shape[:2]
        
        # Resize image to fit in the frame if needed
        if resize:
            max_height = self.image_frame.winfo_height() or 400
            max_width = self.image_frame.winfo_width() or 700
            
            # Calculate resize ratio
            ratio = min(max_width/w, max_height/h)
            if ratio < 1:
                new_width = int(w * ratio)
                new_height = int(h * ratio)
                img = cv2.resize(img, (new_width, new_height))
        
        # Convert NumPy array to PhotoImage
        self.img_display = Image.fromarray(img)
        self.photo = tk.PhotoImage(master=self.root, data=self.img_display.tobytes())
        
        # Update label
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
        
        self.image_label = Label(self.image_frame, image=self.photo)
        self.image_label.image = self.photo  # Keep a reference
        self.image_label.bind("<Button-1>", self.pick_color)
        self.image_label.pack(expand=True)
        
    def pick_color(self, event):
        if self.img_rgb is None:
            return
            
        # Calculate the coordinates in the original image
        display_width = self.img_display.width
        display_height = self.img_display.height
        original_width = self.img_rgb.shape[1]
        original_height = self.img_rgb.shape[0]
        
        # Scale the event coordinates to the original image coordinates
        x_ratio = original_width / display_width
        y_ratio = original_height / display_height
        
        x = int(event.x * x_ratio)
        y = int(event.y * y_ratio)
        
        # Ensure coordinates are within bounds
        x = max(0, min(x, original_width - 1))
        y = max(0, min(y, original_height - 1))
        
        # Get the color at the clicked point
        self.target_color = self.img_rgb[y, x].tolist()
        
        # Update color indicator
        hex_color = f'#{self.target_color[0]:02x}{self.target_color[1]:02x}{self.target_color[2]:02x}'
        self.color_indicator.config(bg=hex_color)
        
        # Generate preview
        self.generate_preview()
        self.process_btn.config(state=tk.NORMAL)
        
        self.status_bar.config(text=f"Selected color: RGB{tuple(self.target_color)} at ({x}, {y})")
    
    def update_range(self, value):
        self.color_range = int(value)
        if self.target_color is not None:
            self.generate_preview()
            
    def generate_preview(self):
        if self.img_rgb is None or self.target_color is None:
            return
            
        # Create a preview with the current settings
        def process_preview():
            target_rgb = np.array(self.target_color, dtype=np.int32)
            img_copy = self.img_rgb.copy()
            
            # Only process every few pixels for speed
            step = 3
            for y in range(0, img_copy.shape[0], step):
                for x in range(0, img_copy.shape[1], step):
                    pixel_rgb = img_copy[y, x]
                    distance = np.sqrt(np.sum((pixel_rgb - target_rgb) ** 2))
                    if distance <= self.color_range:
                        # Mark the background pixels as bright pink
                        img_copy[y:y+step, x:x+step] = [255, 0, 255]
            
            self.update_display(img_copy)
        
        # Run the processing in a separate thread to avoid freezing the UI
        preview_thread = threading.Thread(target=process_preview)
        preview_thread.start()
    
    def process_image(self):
        if self.img_rgb is None or self.target_color is None:
            return
            
        # Ask for output filename
        self.output_path = filedialog.asksaveasfilename(
            title="Save Transparent PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        
        if not self.output_path:
            return
            
        # Show progress bar
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        self.progress.start()
        self.is_processing = True
        self.status_bar.config(text="Processing image...")
        
        # Process in a separate thread
        process_thread = threading.Thread(target=self.remove_background)
        process_thread.start()
    
    def remove_background(self):
        try:
            # Create an alpha channel (initially all opaque)
            height, width = self.img_rgb.shape[:2]
            alpha_channel = np.ones((height, width), dtype=np.uint8) * 255
            
            # Convert target_color to numpy array
            target_rgb = np.array(self.target_color, dtype=np.int32)
            
            # For each pixel, check if it's within the color range of the target color
            for y in range(height):
                for x in range(width):
                    pixel_rgb = self.img_rgb[y, x]
                    # Calculate color distance (Euclidean distance in RGB space)
                    distance = np.sqrt(np.sum((pixel_rgb - target_rgb) ** 2))
                    # If the distance is within the range, mark the pixel for transparency
                    if distance <= self.color_range:
                        alpha_channel[y, x] = 0  # Transparent
            
            # Convert to PIL Image with transparency
            img_pil = Image.fromarray(self.img_rgb)
            alpha_pil = Image.fromarray(alpha_channel)
            img_pil.putalpha(alpha_pil)
            
            # Save the image with transparency
            img_pil.save(self.output_path, 'PNG')
            
            # Update status
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Image saved to {os.path.basename(self.output_path)}"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Error: {str(e)}"
            ))
        
        finally:
            # Hide progress bar
            self.root.after(0, lambda: self.progress.pack_forget())
            self.root.after(0, lambda: self.progress.stop())
            self.is_processing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()