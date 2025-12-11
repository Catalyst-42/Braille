import numpy as np
from PIL import Image
from pathlib import Path

# 'A' means that next glyph is capital
# 'N' means that next glyph is numerical
ALPHABET = " abcdefghijklmnopqrstuvwxyzAN.,?;!''()-"

# In Braille numbers described with letters
NUMBERS = 'jabcdefghi'  # 0-9

# Get parts and create tilemap
PARTS = Path('./parts/2_3_english_tight.png')

tile_width, tile_height, *_ = PARTS.stem.split('_')
tile_width = int(tile_width)
tile_height = int(tile_height)

image_array = np.array(Image.open(PARTS))
img_height, img_width = image_array.shape[:2]

# Get list of tiles
tiles = []
for i in range(img_width // tile_width):
    left = i * tile_width
    right = left + tile_width

    tile = image_array[:, left:right]
    tiles.append(tile)

# Ensure all alphabet in tiles
assert len(tiles) == len(ALPHABET), 'Tiles not cover alphabet'

# Create mappings char on tile and a more efficient lookup structure
char_to_tile = {}
tile_data_to_char = {}  # Map tile data to character

for char, tile in zip(ALPHABET, tiles):
    char_to_tile[char] = tile

    # Create hashable representation of tile data for exact matching
    tile_bytes = tile.tobytes()
    tile_data_to_char[tile_bytes] = char

def extract_tiles_from_image(image: np.ndarray) -> list:
    """Extract individual braille tiles from image."""
    image_height, image_width = image.shape[:2]
    
    # Validate image dimensions
    if image_height != tile_height:
        raise ValueError(f"Image height {image_height} doesn't match tile height {tile_height}")
    
    tiles_count = image_width // tile_width
    extracted_tiles = []
    
    for i in range(tiles_count):
        left = i * tile_width
        right = left + tile_width
        tile = image[:, left:right]
        extracted_tiles.append(tile)
    
    return extracted_tiles

def tile_to_char(tile: np.ndarray) -> str:
    """Find exact match for tile using byte representation."""
    tile_bytes = tile.tobytes()
    
    # Direct lookup in the dictionary
    if tile_bytes in tile_data_to_char:
        return tile_data_to_char[tile_bytes]
    
    # If not found (should not happen with noise-free images)
    return '?'

def braille_to_text(image_path: str) -> str:
    """Convert braille image back to text."""
    # Load the braille image
    braille_image = np.array(Image.open(image_path))
    
    # Extract individual braille tiles
    braille_tiles = extract_tiles_from_image(braille_image)
    
    # Convert tiles to characters using exact matching
    braille_chars = [tile_to_char(tile) for tile in braille_tiles]
    
    # Process special symbols and reconstruct text
    text_chars = []
    is_capital_next = False
    is_numerical_mode = False
    
    for char in braille_chars:
        # Handle capital letter prefix
        if char == 'A':
            is_capital_next = True
            continue
        
        # Handle numerical mode prefix
        if char == 'N':
            is_numerical_mode = True
            continue
        
        # Handle numerical mode exit
        if char == ';' and is_numerical_mode:
            is_numerical_mode = False
            continue
        
        # Convert number back from letter representation
        if is_numerical_mode and char in NUMBERS:
            digit = str(NUMBERS.index(char))
            text_chars.append(digit)
            continue
        
        # Apply capital letter if needed
        if is_capital_next and char.isalpha():
            text_chars.append(char.upper())
            is_capital_next = False
        else:
            text_chars.append(char)
            is_capital_next = False
        
        # Exit numerical mode on space
        if char == ' ':
            is_numerical_mode = False
    
    # Join all characters into final text
    result_text = ''.join(text_chars)
    return result_text

# Decode braille image back to text
output_image_path = 'output.png'
decoded_text = braille_to_text(output_image_path)

print("Decoded text:", decoded_text)
print("Done")
