import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk

def swap_and_preview():
    """
    Allow the user to select an image, swap color channels, and preview the result.
    """
    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    def preview_images():
        file_path = file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an image file.")
            return

        swap_option = swap_var.get()
        if swap_option not in ["RG", "RB", "GB"]:
            messagebox.showerror("Error", "Invalid swap option. Please select RG, RB, or GB.")
            return

        try:
            # Open the image
            img = Image.open(file_path)

            # Convert to RGB if it's not already
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Split into channels
            r, g, b = img.split()

            # Swap based on the option
            if swap_option == 'RG':
                swapped_img = Image.merge('RGB', (g, r, b))
            elif swap_option == 'RB':
                swapped_img = Image.merge('RGB', (b, g, r))
            elif swap_option == 'GB':
                swapped_img = Image.merge('RGB', (r, b, g))

            # Display the images side by side
            display_side_by_side(img, swapped_img)

#test bla

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_side_by_side(original, swapped):
        """
        Display the original and swapped images side by side in a new window.
        """
        # Create a new window
        preview_window = tk.Toplevel()
        preview_window.title("Preview")

        # Resize images to fit the screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        max_width = screen_width // 2 - 50
        max_height = screen_height - 100

        def resize_image(image):
            width_ratio = max_width / image.width
            height_ratio = max_height / image.height
            scale_factor = min(width_ratio, height_ratio)
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            return image.resize((new_width, new_height), Image.LANCZOS)

        original_resized = resize_image(original)
        swapped_resized = resize_image(swapped)

        # Convert images to Tkinter format
        original_tk = ImageTk.PhotoImage(original_resized)
        swapped_tk = ImageTk.PhotoImage(swapped_resized)

        # Create labels to display the images
        original_label = tk.Label(preview_window, image=original_tk)
        swapped_label = tk.Label(preview_window, image=swapped_tk)
        original_label.image = original_tk  # Keep a reference!
        swapped_label.image = swapped_tk  # Keep a reference!

        # Pack the labels side by side
        original_label.pack(side=tk.LEFT, padx=10, pady=10)
        swapped_label.pack(side=tk.LEFT, padx=10, pady=10)

    # Create the main window
    root = tk.Tk()
    root.title("Color Switcher")

    # File selection
    file_frame = tk.Frame(root)
    file_frame.pack(pady=10)

    file_label = tk.Label(file_frame, text="Select an image file:")
    file_label.pack(side=tk.LEFT, padx=5)

    file_entry = tk.Entry(file_frame, width=50)
    file_entry.pack(side=tk.LEFT, padx=5)

    browse_button = tk.Button(file_frame, text="Browse", command=select_file)
    browse_button.pack(side=tk.LEFT, padx=5)

    # Swap option selection
    swap_frame = tk.Frame(root)
    swap_frame.pack(pady=10)

    swap_label = tk.Label(swap_frame, text="Select swap option:")
    swap_label.pack(side=tk.LEFT, padx=5)

    swap_var = tk.StringVar(value="RG")
    swap_dropdown = ttk.Combobox(swap_frame, textvariable=swap_var, values=["RG", "RB", "GB"], state="readonly")
    swap_dropdown.pack(side=tk.LEFT, padx=5)

    # Preview button
    preview_button = tk.Button(root, text="Preview", command=preview_images)
    preview_button.pack(pady=20)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    swap_and_preview()