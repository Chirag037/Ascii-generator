from PIL import Image, ImageEnhance
import argparse
import os

class ASCIIArtGenerator:
    def __init__(self):
        # Different character sets for different styles
        self.char_sets = {
            'standard': "@%#*+=-:. ",
            'detailed': "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
            'simple': "█▉▊▋▌▍▎▏ ",
            'blocks': "██▓▒░  ",
            'minimal': "#+-. "
        }
        
    def resize_image(self, image, new_width=100):
        """Resize image while maintaining aspect ratio"""
        width, height = image.size
        aspect_ratio = height / width
        new_height = int(aspect_ratio * new_width * 0.55)  # 0.55 to account for character height
        return image.resize((new_width, new_height))
    
    def grayscale_image(self, image):
        """Convert image to grayscale"""
        return image.convert('L')
    
    def enhance_contrast(self, image, factor=1.5):
        """Enhance image contrast for better ASCII conversion"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    def pixels_to_ascii(self, image, char_set='standard'):
        """Convert pixels to ASCII characters"""
        chars = self.char_sets.get(char_set, self.char_sets['standard'])
        pixels = image.getdata()
        
        # Map each pixel to a character based on brightness
        ascii_chars = []
        for pixel in pixels:
            ascii_chars.append(chars[pixel * len(chars) // 256])
        
        return ascii_chars
    
    def format_ascii(self, ascii_chars, width):
        """Format ASCII characters into lines"""
        ascii_lines = []
        for i in range(0, len(ascii_chars), width):
            ascii_lines.append(''.join(ascii_chars[i:i+width]))
        return '\n'.join(ascii_lines)
    
    def generate_ascii_art(self, image_path, width=100, char_set='standard', 
                          enhance_contrast=True, contrast_factor=1.5):
        """Main function to generate ASCII art from image"""
        try:
            # Load and process image
            image = Image.open(image_path)
            image = self.resize_image(image, width)
            image = self.grayscale_image(image)
            
            if enhance_contrast:
                image = self.enhance_contrast(image, contrast_factor)
            
            # Convert to ASCII
            ascii_chars = self.pixels_to_ascii(image, char_set)
            ascii_art = self.format_ascii(ascii_chars, width)
            
            return ascii_art
            
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def save_ascii_art(self, ascii_art, output_path):
        """Save ASCII art to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(ascii_art)
            return f"ASCII art saved to {output_path}"
        except Exception as e:
            return f"Error saving file: {str(e)}"
    
    def preview_char_sets(self):
        """Show available character sets"""
        print("Available character sets:")
        for name, chars in self.char_sets.items():
            print(f"  {name}: {chars}")

def main():
    parser = argparse.ArgumentParser(description='Convert images to ASCII art')
    parser.add_argument('image_path', help='Path to input image')
    parser.add_argument('-w', '--width', type=int, default=100, 
                       help='Width of ASCII art (default: 100)')
    parser.add_argument('-c', '--charset', default='standard',
                       choices=['standard', 'detailed', 'simple', 'blocks', 'minimal'],
                       help='Character set to use (default: standard)')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--no-contrast', action='store_true',
                       help='Disable contrast enhancement')
    parser.add_argument('--contrast-factor', type=float, default=1.5,
                       help='Contrast enhancement factor (default: 1.5)')
    parser.add_argument('--preview-chars', action='store_true',
                       help='Show available character sets')
    
    args = parser.parse_args()
    
    generator = ASCIIArtGenerator()
    
    if args.preview_chars:
        generator.preview_char_sets()
        return
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        return
    
    print(f"Processing image: {args.image_path}")
    print(f"Width: {args.width}, Character set: {args.charset}")
    
    ascii_art = generator.generate_ascii_art(
        args.image_path,
        width=args.width,
        char_set=args.charset,
        enhance_contrast=not args.no_contrast,
        contrast_factor=args.contrast_factor
    )
    
    if ascii_art.startswith("Error"):
        print(ascii_art)
        return
    
    # Display ASCII art
    print("\nGenerated ASCII Art:")
    print("-" * 50)
    print(ascii_art)
    print("-" * 50)
    
    # Save to file if specified
    if args.output:
        result = generator.save_ascii_art(ascii_art, args.output)
        print(f"\n{result}")

if __name__ == "__main__":
    main()
