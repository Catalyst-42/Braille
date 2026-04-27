# Braille
A simple tool to translate Russian and Latin (English) text to the Braille encoded image and translate this images back to human readable text. Engine are separated from GUI, so you also may to use it directly. 

## Images
Encoding tab

![Braille text encoding](<img/Braille - Encode.png>)

Decoding tab

![Braille text decoding](<img/Braille - Decode.png>) 

## Installation
Application build on Python of version 3.14. Uses Pillow and numpy for image generation and recognition. To install dependencies use pip:

```sh
pip3 install -r requirements.txt
```

> [!NOTE]
> To run GUI application you also need to have Tkinter installed. Installation method depends on your operating system and Python installation type

## Usage
After installation simply run `gui.py` as common script:

```sh
python3 gui.py
```

Also you may use engine directly just by importing function you need:

```python
from braille import (
    braille_to_image,
    braille_to_text,
    image_to_braille,
    image_to_text,
    text_to_braille,
    text_to_image,
)

# Text to image
text = input('Text: ')
braille = text_to_braille(text)
image = text_to_image(text)
print('Braille:', braille)
print('Image:', image)

print()

# Image to text
braille = image_to_braille(image)
text = image_to_text(image)
print("Decoding image:", image)
print("Decoded text:", text)
print("Decoded braille:", braille)

print()

# Codes manupulation
braille = ["NEXT_CAPITAL_LATIN", "e", "x", "a", "m", "p", "l", "e"]
text = braille_to_text(braille)
image = braille_to_image(braille)
print("Custom codes:", braille)
print("Custom text:", text)
print("Custom image", image)
```

## Notes
Braille may use one key representation for different letters. Do distinct the language, we use the `NEXT_` / `SMALL_` or `CAPITAL_` / `LATIN` or `RUSSIAN` letter codes. To better understand how this codes works in system, check the `braille_test` file.

To test the app, you should additionally install `pytest`:

```sh
pip install pytest
```

And run them in project root folder:

```
pytest
```
