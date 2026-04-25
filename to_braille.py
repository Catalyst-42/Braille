import numpy as np
from PIL import Image
from pathlib import Path

# English
# 'A' means that next glyph is capital
# 'N' means that next glyph is numerical
ALPHABET = ' abcdefghijklmnopqrstuvwxyzAN.,?;!""()-'

# In Braille numbers described with letters
NUMBERS = 'jabcdefghi'  # 0-9

# Get parts and create tilemap
PARTS = Path('./parts/2_3_english_tight.png')


# Russian
# 'A' means that next glyph is capital
# 'a' means that next glyph is small
# 'L' means that next glyph is capital latin
# 'l' means that next glyph is small latin
# 'G' means that next glyph is capital greek
# 'g' means that next glyph is small greek
# 'N' means that next glyph is numerical
# ALPHABET = ' абвгдеёжзийклмнопрстуфхцчшщъыьэюя.!-""(),?AaLlGgN;'
# NUMBERS = 'абвгдеёжзи'

# Get parts and create tilemap
# PARTS = Path('./parts/2_3_russian_tight.png')

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

# Create mappings char on tile
char_to_tile = {}
for char, tile in zip(ALPHABET, tiles):
    char_to_tile[char] = tile

def create_output_image(width_tiles: int) -> np.ndarray:
    out_width = width_tiles * tile_width
    out_height = tile_height

    return np.zeros(
        (out_height, out_width, image_array.shape[2]),
        dtype=image_array.dtype
    )

def insert_tile(image: np.ndarray, tile: np.ndarray, position: int) -> np.ndarray:
    """Inserts tile on image by given position."""
    left = position * tile_width
    right = left + tile_width

    # Insert the tile
    image[:, left:right] = tile
    return image

def text_to_braille(text: str) -> np.ndarray:
    """Convert text to braille image with dynamic width."""
    tiles_needed = []
    is_numerical_sequence = False

    # First pass: calculate needed tiles
    for char in text:
        # Check for capital letter prefix each before capital
        # AIR -> AaAiAr
        if char.isupper():
            tiles_needed.append('A')
            char = char.lower()

        # If text are combined with char, add semicolon
        # 123abc -> 123;abc
        if is_numerical_sequence and char.isalpha():
            tiles_needed.append(';')
            is_numerical_sequence = False

        # Check for numerical prefix
        # 12 -> Nab
        if char.isdigit():
            if not is_numerical_sequence:
                tiles_needed.append('N')
                is_numerical_sequence = True

            char = NUMBERS[int(char)]

        # Check on exit from numerical mode
        if is_numerical_sequence and char == ' ':
            is_numerical_sequence = False

        # Add character tile
        if char not in char_to_tile:
            print(f'Warning: char "{char}" not in alphabet')
            continue

        tiles_needed.append(char)

    # Create output image with calculated size
    out_image = create_output_image(len(tiles_needed))

    # Second pass: insert tiles
    print("Transmission:", ''.join(tiles_needed))
    for i, char in enumerate(tiles_needed):
        tile = char_to_tile[char]
        out_image = insert_tile(out_image, tile, i)

    return out_image

# Generate braille image
in_text: str = input('Input: ')
out_image = text_to_braille(in_text)

# Save result
result_pil = Image.fromarray(out_image)
result_pil.save('output.png')
print("Done")
