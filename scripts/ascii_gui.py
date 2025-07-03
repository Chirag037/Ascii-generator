import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from ascii_generator import ASCIIArtGenerator
import threading

class ASCIIArtGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Art Generator")
        self.root.geometry("800x600")
        
        self.generator = ASCIIArtGenerator()
        self.current_image_path = None
        self.ascii_art = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection
        ttk.Label(main_frame, text="Select Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly").grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="5")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        
        # Width setting
        ttk.Label(settings_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.width_var = tk.IntVar(value=80)
        width_spinbox = ttk.Spinbox(settings_frame, from_=20, to=200, textvariable=self.width_var, width=10)
        width_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Character set setting
        ttk.Label(settings_frame, text="Character Set:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.charset_var = tk.StringVar(value="standard")
        charset_combo = ttk.Combobox(settings_frame, textvariable=self.charset_var, 
                                   values=list(self.generator.char_sets.keys()), 
                                   state="readonly", width=15)
        charset_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Contrast setting
        self.contrast_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Enhance Contrast", 
                       variable=self.contrast_var).grid(row=0, column=4, sticky=tk.W)
        
        # Generate button
        self.generate_btn = ttk.Button(settings_frame, text="Generate ASCII Art", 
                                     command=self.generate_ascii_threaded)
        self.generate_btn.grid(row=1, column=0, columnspan=5, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(settings_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="ASCII Art Output", padding="5")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Text area with scrollbars
        self.text_area = scrolledtext.ScrolledText(output_frame, wrap=tk.NONE, 
                                                  font=("Courier", 8))
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons frame
        buttons_frame = ttk.Frame(output_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(buttons_frame, text="Save ASCII Art", 
                  command=self.save_ascii).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Clear", 
                  command=self.clear_output).pack(side=tk.LEFT)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.current_image_path = file_path
    
    def generate_ascii_threaded(self):
        if not self.current_image_path:
            messagebox.showerror("Error", "Please select an image file first")
            return
        
        # Start progress bar and disable button
        self.progress.start()
        self.generate_btn.config(state="disabled")
        
        # Run generation in separate thread
        thread = threading.Thread(target=self.generate_ascii)
        thread.daemon = True
        thread.start()
    
    def generate_ascii(self):
        try:
            self.ascii_art = self.generator.generate_ascii_art(
                self.current_image_path,
                width=self.width_var.get(),
                char_set=self.charset_var.get(),
                enhance_contrast=self.contrast_var.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self.update_output)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate ASCII art: {str(e)}"))
        finally:
            self.root.after(0, self.generation_complete)
    
    def update_output(self):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, self.ascii_art)
    
    def generation_complete(self):
        self.progress.stop()
        self.generate_btn.config(state="normal")
    
    def save_ascii(self):
        if not self.ascii_art:
            messagebox.showwarning("Warning", "No ASCII art to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save ASCII Art",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            result = self.generator.save_ascii_art(self.ascii_art, file_path)
            if result.startswith("ASCII art saved"):
                messagebox.showinfo("Success", result)
            else:
                messagebox.showerror("Error", result)
    
    def copy_to_clipboard(self):
        if not self.ascii_art:
            messagebox.showwarning("Warning", "No ASCII art to copy")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(self.ascii_art)
        messagebox.showinfo("Success", "ASCII art copied to clipboard")
    
    def clear_output(self):
        self.text_area.delete(1.0, tk.END)
        self.ascii_art = ""

def main():
    root = tk.Tk()
    app = ASCIIArtGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
