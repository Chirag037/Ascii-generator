import os
import glob
from ascii_generator import ASCIIArtGenerator
import concurrent.futures
from pathlib import Path

class BatchASCIIProcessor:
    def __init__(self):
        self.generator = ASCIIArtGenerator()
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    
    def find_images(self, directory):
        """Find all supported image files in directory"""
        image_files = []
        for ext in self.supported_formats:
            pattern = os.path.join(directory, f"**/*{ext}")
            image_files.extend(glob.glob(pattern, recursive=True))
            # Also check uppercase extensions
            pattern = os.path.join(directory, f"**/*{ext.upper()}")
            image_files.extend(glob.glob(pattern, recursive=True))
        return image_files
    
    def process_single_image(self, image_path, output_dir, width, char_set):
        """Process a single image"""
        try:
            # Generate ASCII art
            ascii_art = self.generator.generate_ascii_art(
                image_path, width=width, char_set=char_set
            )
            
            if ascii_art.startswith("Error"):
                return f"Failed: {image_path} - {ascii_art}"
            
            # Create output filename
            input_name = Path(image_path).stem
            output_path = os.path.join(output_dir, f"{input_name}_ascii.txt")
            
            # Save ASCII art
            result = self.generator.save_ascii_art(ascii_art, output_path)
            return f"Success: {image_path} -> {output_path}"
            
        except Exception as e:
            return f"Failed: {image_path} - {str(e)}"
    
    def process_batch(self, input_dir, output_dir, width=100, char_set='standard', 
                     max_workers=4):
        """Process multiple images in parallel"""
        # Find all images
        image_files = self.find_images(input_dir)
        
        if not image_files:
            return "No supported image files found"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Found {len(image_files)} images to process")
        print(f"Output directory: {output_dir}")
        print(f"Settings: width={width}, charset={char_set}")
        print("-" * 50)
        
        # Process images in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_image = {
                executor.submit(
                    self.process_single_image, 
                    img_path, output_dir, width, char_set
                ): img_path for img_path in image_files
            }
            
            for future in concurrent.futures.as_completed(future_to_image):
                result = future.result()
                results.append(result)
                print(result)
        
        # Summary
        successful = len([r for r in results if r.startswith("Success")])
        failed = len(results) - successful
        
        print("-" * 50)
        print(f"Processing complete!")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch convert images to ASCII art')
    parser.add_argument('input_dir', help='Input directory containing images')
    parser.add_argument('output_dir', help='Output directory for ASCII files')
    parser.add_argument('-w', '--width', type=int, default=100,
                       help='Width of ASCII art (default: 100)')
    parser.add_argument('-c', '--charset', default='standard',
                       choices=['standard', 'detailed', 'simple', 'blocks', 'minimal'],
                       help='Character set to use (default: standard)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers (default: 4)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' not found")
        return
    
    processor = BatchASCIIProcessor()
    processor.process_batch(
        args.input_dir,
        args.output_dir,
        width=args.width,
        char_set=args.charset,
        max_workers=args.workers
    )

if __name__ == "__main__":
    main()
