import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image
import os

def swap_channels(input_path, output_path, swap_option):
    """
    Swap color channels in an image based on the swap_option.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path to save the output image
        swap_option (str): Which channels to swap (RG, RB, GB)
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Convert to RGB if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Split into channels
        r, g, b = img.split()
        
        # Swap based on the option
        if swap_option == 'RG':
            new_img = Image.merge('RGB', (g, r, b))
        elif swap_option == 'RB':
            new_img = Image.merge('RGB', (b, g, r))
        elif swap_option == 'GB':
            new_img = Image.merge('RGB', (r, b, g))
        else:
            raise ValueError(f"Invalid swap option: {swap_option}")
        
        # Save the result
        new_img.save(output_path)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def main():
    # Create a root window but hide it
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog to select an image
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All files", "*.*")
        ]
    )
    
    if not file_path:
        print("No file selected. Exiting.")
        return
    
    # Ask which channels to swap
    swap_options = ["RG", "RB", "GB"]
    swap_option = simpledialog.askstring(
        "Swap Channels",
        "Which channels to swap? (RG, RB, GB):",
        initialvalue="RG"
    )
    
    if not swap_option or swap_option.upper() not in swap_options:
        messagebox.showerror("Error", "Invalid swap option. Please choose from RG, RB, or GB.")
        return
    
    # Generate output path
    file_dir, file_name = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file_name)
    output_path = os.path.join(file_dir, f"{file_name}_swapped_{swap_option.upper()}{file_ext}")
    
    # Ask for save location
    save_path = filedialog.asksaveasfilename(
        title="Save the swapped image",
        initialfile=os.path.basename(output_path),
        defaultextension=file_ext,
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
    )
    
    if not save_path:
        print("No save location selected. Exiting.")
        return
    
    # Process the image
    if swap_channels(file_path, save_path, swap_option.upper()):
        messagebox.showinfo("Success", f"Image processed successfully and saved to:\n{save_path}")
        
        # Ask if the user wants to open the image
        if messagebox.askyesno("Open Image", "Do you want to open the processed image?"):
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == 'Windows':
                    os.startfile(save_path)
                elif system == 'Darwin':  # macOS
                    subprocess.call(['open', save_path])
                else:  # Linux and other Unix-like
                    subprocess.call(['xdg-open', save_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open the image: {str(e)}")

if __name__ == "__main__":
    main()
