import tkinter as tk
from tkinter import filedialog, ttk, colorchooser
from PIL import Image, ImageTk
import numpy as np
import os
import sys

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover")
        self.root.geometry("1000x700")
        
        # Variables
        self.input_path = None
        self.output_path = None
        self.image = None
        self.display_image = None
        self.tk_image = None
        self.original_size = (0, 0)
        self.selected_color = (0, 255, 0)  # Default: green
        self.tolerance = 30
        self.result_image = None
        self.picking_color = False
        self.preview_displayed = False
        
        # Create UI
        self.create_ui()
        
        # Initial state
        self.update_ui_state()
    
    def create_ui(self):
        # Main frames
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        image_frame = ttk.Frame(self.root)
        image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control elements
        # File selection
        file_frame = ttk.LabelFrame(control_frame, text="Image Selection", padding=5)
        file_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="Open Image (PNG/JPG)", command=self.open_image).pack(side=tk.LEFT, padx=5)
        self.filepath_label = ttk.Label(file_frame, text="No file selected")
        self.filepath_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Color selection
        color_frame = ttk.LabelFrame(control_frame, text="Color Selection", padding=5)
        color_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.color_button = ttk.Button(color_frame, text="Pick Color from Image", command=self.toggle_color_picker)
        self.color_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(color_frame, text="Choose Color", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        self.color_preview = tk.Canvas(color_frame, width=30, height=20, bg="#00FF00", relief="ridge", bd=1)
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        self.color_label = ttk.Label(color_frame, text="RGB: (0, 255, 0)")
        self.color_label.pack(side=tk.LEFT, padx=5)
        
        # Tolerance slider
        tolerance_frame = ttk.LabelFrame(control_frame, text="Color Tolerance", padding=5)
        tolerance_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.tolerance_slider = ttk.Scale(tolerance_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                                         value=30, command=self.update_tolerance)
        self.tolerance_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.tolerance_label = ttk.Label(tolerance_frame, text="30")
        self.tolerance_label.pack(side=tk.LEFT, padx=5)
        
        # Processing buttons
        process_frame = ttk.Frame(control_frame)
        process_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.preview_button = ttk.Button(process_frame, text="Preview Result", command=self.preview_result)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(process_frame, text="Save Result", command=self.save_result)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(process_frame, text="")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Image display
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.on_image_click)
        
        # Scrollbar setup
        self.image_canvas = tk.Canvas(image_frame)
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y = ttk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.image_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.image_canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.image_frame = ttk.Frame(self.image_canvas)
        self.image_canvas.create_window((0, 0), window=self.image_frame, anchor=tk.NW)
        
        self.display_label = ttk.Label(self.image_frame)
        self.display_label.pack()
        self.display_label.bind("<Button-1>", self.on_image_click)
        
    def update_ui_state(self):
        # Update UI based on current state
        has_image = self.image is not None
        
        # Enable/disable buttons
        self.color_button["state"] = "normal" if has_image else "disabled"
        self.preview_button["state"] = "normal" if has_image else "disabled"
        self.save_button["state"] = "normal" if self.result_image is not None else "disabled"
    
    def open_image(self):
        # Open file dialog
        filetypes = [
            ("Image files", "*.png;*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if not file_path:
            return
        
        try:
            # Load and display the image
            self.input_path = file_path
            self.filepath_label.config(text=os.path.basename(file_path))
            
            # Reset state
            self.result_image = None
            self.preview_displayed = False
            
            # Load image
            self.image = Image.open(file_path).convert("RGBA")
            self.original_size = self.image.size
            
            # Display image (resize if too large)
            self.display_image = self.image.copy()
            self.update_image_display()
            
            # Update UI state
            self.status_label.config(text=f"Image loaded: {self.original_size[0]}x{self.original_size[1]} pixels")
            self.update_ui_state()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def update_image_display(self):
        if self.display_image:
            # Resize for display if needed
            max_width = 900
            max_height = 500
            
            width, height = self.display_image.size
            ratio = min(max_width/width, max_height/height)
            
            if ratio < 1:
                new_size = (int(width * ratio), int(height * ratio))
                display_img = self.display_image.resize(new_size, Image.LANCZOS)
            else:
                display_img = self.display_image
            
            # Create Tkinter-compatible image
            self.tk_image = ImageTk.PhotoImage(display_img)
            self.display_label.config(image=self.tk_image)
            
            # Update canvas scrolling region
            self.image_frame.update_idletasks()
            self.image_canvas.config(scrollregion=self.image_canvas.bbox(tk.ALL))
    
    def on_canvas_configure(self, event):
        # Update canvas scrolling region when resized
        self.image_canvas.config(scrollregion=self.image_canvas.bbox(tk.ALL))
    
    def toggle_color_picker(self):
        self.picking_color = not self.picking_color
        
        if self.picking_color:
            self.color_button.config(text="Click on Image")
            self.status_label.config(text="Click on the image to pick a color")
        else:
            self.color_button.config(text="Pick Color from Image")
            self.status_label.config(text="")
    
    def on_image_click(self, event):
        if not self.picking_color or not self.image:
            return
        
        # Get click coordinates relative to the image
        x = event.x
        y = event.y
        
        # Need to convert coordinates based on display scale
        display_width, display_height = self.tk_image.width(), self.tk_image.height()
        orig_width, orig_height = self.original_size
        
        # Calculate scale factors
        scale_x = orig_width / display_width
        scale_y = orig_height / display_height
        
        # Convert to original image coordinates
        orig_x = int(x * scale_x)
        orig_y = int(y * scale_y)
        
        # Make sure coordinates are within bounds
        orig_x = min(max(0, orig_x), orig_width - 1)
        orig_y = min(max(0, orig_y), orig_height - 1)
        
        # Get pixel color (convert to RGB to ensure consistent format)
        pixel = self.image.convert("RGB").getpixel((orig_x, orig_y))
        self.selected_color = pixel
        
        # Update UI
        hex_color = f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
        self.color_preview.config(bg=hex_color)
        self.color_label.config(text=f"RGB: {pixel}")
        
        self.status_label.config(text=f"Color selected at ({orig_x}, {orig_y}): RGB{pixel}")
        self.picking_color = False
        self.color_button.config(text="Pick Color from Image")
    
    def choose_color(self):
        # Open color chooser dialog
        color = colorchooser.askcolor(
            title="Choose Background Color",
            initialcolor=f"#{self.selected_color[0]:02x}{self.selected_color[1]:02x}{self.selected_color[2]:02x}"
        )
        
        if color[0]:  # If a color was selected (not canceled)
            self.selected_color = (int(color[0][0]), int(color[0][1]), int(color[0][2]))
            self.color_preview.config(bg=color[1])
            self.color_label.config(text=f"RGB: {self.selected_color}")
    
    def update_tolerance(self, value):
        self.tolerance = int(float(value))
        self.tolerance_label.config(text=str(self.tolerance))
    
    def remove_background(self):
        if not self.image:
            return None
        
        try:
            # Convert image to numpy array for faster processing
            data = np.array(self.image)
            
            # Extract RGB components from data
            r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
            
            # Extract target color components
            target_r, target_g, target_b = self.selected_color
            
            # Calculate Euclidean distance
            distance = np.sqrt(
                (r.astype(np.int16) - target_r) ** 2 +
                (g.astype(np.int16) - target_g) ** 2 +
                (b.astype(np.int16) - target_b) ** 2
            )
            
            # Create mask where distance is within tolerance
            mask = distance <= self.tolerance
            
            # Set alpha channel to 0 (transparent) where mask is True
            data[:, :, 3] = np.where(mask, 0, a)
            
            # Create a new image from the modified array
            return Image.fromarray(data)
            
        except Exception as e:
            self.status_label.config(text=f"Error processing image: {str(e)}")
            return None
    
    def preview_result(self):
        if not self.image:
            return
        
        # Process the image
        self.result_image = self.remove_background()
        
        if self.result_image:
            # Show the result
            self.display_image = self.result_image
            self.update_image_display()
            self.preview_displayed = True
            self.status_label.config(text="Preview generated - click 'Save Result' to save")
            self.update_ui_state()
        else:
            self.status_label.config(text="Error generating preview")
    
    def save_result(self):
        if not self.result_image:
            if not self.preview_displayed:
                self.preview_result()
            
            if not self.result_image:
                return
        
        # Get save location
        file_path = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        
        if not file_path:
            return
        
        try:
            # Save the result
            self.result_image.save(file_path, "PNG")
            self.status_label.config(text=f"Result saved to {os.path.basename(file_path)}")
        except Exception as e:
            self.status_label.config(text=f"Error saving file: {str(e)}")

def main():
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
