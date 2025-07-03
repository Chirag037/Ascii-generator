from PIL import Image, ImageEnhance
import colorsys

class ColorASCIIGenerator:
    def __init__(self):
        self.char_sets = {
            'standard': "@%#*+=-:. ",
            'detailed': "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
            'blocks': "██▓▒░  "
        }
        
        # ANSI color codes
        self.colors = {
            'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
            'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37
        }
    
    def rgb_to_ansi(self, r, g, b):
        """Convert RGB to closest ANSI color"""
        # Convert to HSV for better color matching
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        if v < 0.3:
            return 30  # black
        elif s < 0.3:
            return 37 if v > 0.7 else 30  # white or black
        else:
            # Map hue to color
            hue_ranges = [
                (0, 30, 31),    # red
                (30, 90, 33),   # yellow
                (90, 150, 32),  # green
                (150, 210, 36), # cyan
                (210, 270, 34), # blue
                (270, 330, 35), # magenta
                (330, 360, 31)  # red
            ]
            
            h_deg = h * 360
            for start, end, color in hue_ranges:
                if start <= h_deg < end:
                    return color
            return 31  # default to red
    
    def colorize_char(self, char, r, g, b):
        """Add ANSI color codes to character"""
        color_code = self.rgb_to_ansi(r, g, b)
        return f"\033[{color_code}m{char}\033[0m"
    
    def generate_color_ascii(self, image_path, width=80, char_set='standard'):
        """Generate colored ASCII art"""
        try:
            image = Image.open(image_path)
            image = image.resize((width, int(width * image.height / image.width * 0.55)))
            
            # Keep original for color info
            color_image = image.convert('RGB')
            # Convert to grayscale for character mapping
            gray_image = image.convert('L')
            
            chars = self.char_sets.get(char_set, self.char_sets['standard'])
            
            ascii_lines = []
            for y in range(image.height):
                line = ""
                for x in range(image.width):
                    # Get grayscale value for character selection
                    gray_pixel = gray_image.getpixel((x, y))
                    char_index = gray_pixel * len(chars) // 256
                    char = chars[char_index]
                    
                    # Get RGB values for coloring
                    r, g, b = color_image.getpixel((x, y))
                    colored_char = self.colorize_char(char, r, g, b)
                    
                    line += colored_char
                ascii_lines.append(line)
            
            return '\n'.join(ascii_lines)
            
        except Exception as e:
            return f"Error: {str(e)}"

# Example usage function
def demo_color_ascii():
    generator = ColorASCIIGenerator()
    
    # This would work with an actual image file
    print("Color ASCII Generator Demo")
    print("Usage: generator.generate_color_ascii('path/to/image.jpg', width=60)")
    print("\nNote: Colored output works best in terminals that support ANSI colors")

if __name__ == "__main__":
    demo_color_ascii()
