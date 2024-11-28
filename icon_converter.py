import customtkinter as ctk
from PIL import Image
import tkinter.filedialog as filedialog
from pathlib import Path
import os

class IconConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Dark Mode Icon Converter")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.label = ctk.CTkLabel(
            self.main_frame,
            text="Select an icon to convert for dark mode",
            font=("Arial", 16)
        )
        self.label.grid(row=0, column=0, pady=20)

        self.select_button = ctk.CTkButton(
            self.main_frame,
            text="Select Icon",
            command=self.select_file
        )
        self.select_button.grid(row=1, column=0, pady=10)

        # Create frame for image previews
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(1, weight=1)

        # Original image preview
        self.original_label = ctk.CTkLabel(
            self.preview_frame,
            text="Original Icon",
            font=("Arial", 12)
        )
        self.original_label.grid(row=0, column=0, pady=5)
        
        self.original_image_label = ctk.CTkLabel(
            self.preview_frame,
            text="",
            image=None
        )
        self.original_image_label.grid(row=1, column=0, pady=5)

        # Converted image preview
        self.converted_label = ctk.CTkLabel(
            self.preview_frame,
            text="Converted Icon",
            font=("Arial", 12)
        )
        self.converted_label.grid(row=0, column=1, pady=5)
        
        self.converted_image_label = ctk.CTkLabel(
            self.preview_frame,
            text="",
            image=None
        )
        self.converted_image_label.grid(row=1, column=1, pady=5)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 12)
        )
        self.status_label.grid(row=3, column=0, pady=10)

        # Store image references to prevent garbage collection
        self.original_photo = None
        self.converted_photo = None

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.ico *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.status_label.configure(text="Processing image...")
            self.process_image(file_path)

    def create_preview(self, image, label):
        # Resize image for preview (max 200x200 while maintaining aspect ratio)
        preview_size = (200, 200)
        image.thumbnail(preview_size, Image.Resampling.LANCZOS)
        
        # Convert PIL image to CTkImage
        photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
        
        # Update label with new image
        label.configure(image=photo)
        return photo

    def process_image(self, file_path):
        try:
            # Open the image
            img = Image.open(file_path)
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create preview of original image
            self.original_photo = self.create_preview(img.copy(), self.original_image_label)

            # Get image data
            data = img.getdata()
            
            # Process each pixel
            new_data = []
            for item in data:
                # Check if pixel is not transparent
                if item[3] > 0:  # Alpha channel > 0
                    r, g, b, a = item
                    
                    # Check if the color is dark/grayish
                    # Calculate how gray the color is by checking if R,G,B values are close to each other
                    avg_color = (r + g + b) / 3
                    color_variance = max(abs(r - avg_color), abs(g - avg_color), abs(b - avg_color))
                    
                    # If color is grayish (low variance between RGB) and dark
                    if color_variance < 30 and avg_color < 160:
                        # Convert to a whitish color while preserving slight color tint
                        factor = (255 - avg_color) / 255  # How much to whiten
                        r = int(r + (255 - r) * factor)
                        g = int(g + (255 - g) * factor)
                        b = int(b + (255 - b) * factor)
                    
                    new_data.append((r, g, b, a))
                else:
                    new_data.append(item)  # Keep transparent pixels as is

            # Create new image with processed data
            new_img = Image.new('RGBA', img.size)
            new_img.putdata(new_data)

            # Create preview of converted image
            self.converted_photo = self.create_preview(new_img.copy(), self.converted_image_label)

            # Save the processed image
            output_path = self.get_output_path(file_path)
            new_img.save(output_path)
            
            self.status_label.configure(
                text=f"Success! Saved to:\n{output_path}"
            )

        except Exception as e:
            self.status_label.configure(
                text=f"Error processing image: {str(e)}"
            )

    def get_output_path(self, input_path):
        # Create output path with '_dark_mode' suffix
        path = Path(input_path)
        output_filename = f"{path.stem}_dark_mode{path.suffix}"
        return str(path.parent / output_filename)

if __name__ == "__main__":
    app = IconConverter()
    app.mainloop()
