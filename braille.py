from pathlib import Path
from typing import Literal

from PIL import Image

CONTROLS = {
    'NEXT_NUMBER': 'NEXT_NUMBER',

    'NEXT_CAPITAL_LATIN': 'NEXT_CAPITAL_LATIN',
    'NEXT_SMALL_LATIN': 'NEXT_SMALL_LATIN',

    'NEXT_CAPITAL_RUSSIAN': 'NEXT_CAPITAL_RUSSIAN',
    'NEXT_SMALL_RUSSIAN': 'NEXT_SMALL_RUSSIAN',
}

NUMBERS = {
    '.': 'DOT',
    ',': 'COMMA',
    '1': 'a',
    '2': 'b',
    '3': 'c',
    '4': 'd',
    '5': 'e',
    '6': 'f',
    '7': 'g',
    '8': 'h',
    '9': 'i',
    '0': 'j',
}

SEPARATORS = {
    ' ': 'SPACE',
    '\n': 'NEWLINE',

}

PUNCTUATION = {
    '(': 'BRACKET',
    ')': 'BRACKET',
    '⌊': 'OPEN_QUOTE',
    '⌋': 'CLOSE_QUOTE',
    '?': 'QUESTION_MARK',
    ';': 'SEMICOLON',
    '.': 'DOT',
    '-': 'HYPHEN',
    '!': 'EXCLAMATION_MARK',
    ',': 'COMMA',
}

LATIN = {
    'a': 'a',
    'b': 'b',
    'c': 'c',
    'd': 'd',
    'e': 'e',
    'f': 'f',
    'g': 'g',
    'h': 'h',
    'i': 'i',
    'j': 'j',
    'k': 'k',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'o': 'o',
    'p': 'p',
    'q': 'q',
    'r': 'r',
    's': 's',
    't': 't',
    'u': 'u',
    'v': 'v',
    'w': 'w',
    'x': 'x',
    'y': 'y',
    'z': 'z',
}

RUSSIAN = {
    'а': 'а',
    'б': 'б',
    'в': 'в',
    'г': 'г',
    'д': 'д',
    'е': 'е',
    'ё': 'ё',
    'ж': 'ж',
    'з': 'з',
    'и': 'и',
    'й': 'й',
    'к': 'к',
    'л': 'л',
    'м': 'м',
    'н': 'н',
    'о': 'о',
    'п': 'п',
    'р': 'р',
    'с': 'с',
    'т': 'т',
    'у': 'у',
    'ф': 'ф',
    'х': 'х',
    'ц': 'ц',
    'ч': 'ч',
    'ш': 'ш',
    'щ': 'щ',
    'ъ': 'ъ',
    'ы': 'ы',
    'ь': 'ь',
    'э': 'э',
    'ю': 'ю',
    'я': 'я',
}

TILES = {
    image.stem: Image.open(image).convert('1')
    for image in Path('tiles').glob('*.png')
}

Language = Literal['latin', 'russian']


def key_for(dictionary: dict, value: str) -> str:
    """Returns key if inserted value of dict"""
    for k, v in dictionary.items():
        if v == value:
            return k

    raise KeyError


def quote(text: str) -> str:
    """Replace all quotes on system ones"""
    result = []
    counts = {'"': 0, "'": 0, '`': 0}

    for letter in text:
        if letter in ('"', "'", '`'):
            if counts[letter] % 2 == 0:
                result.append('⌊')
            else:
                result.append('⌋')
            counts[letter] += 1
        else:
            result.append(letter)

    return ''.join(result)


def unquote(text: str, open_quote='"', close_quote='"') -> str:
    """Returns text with replaced quotes"""
    return text.replace('⌊', open_quote).replace('⌋', close_quote)


def text_to_braille(text: str) -> list:
    """Returns braille codes for text"""
    text = quote(text)
    state = ''

    # In multilingual strings we need to
    # mark language of first letter
    first_letter = None
    used_russian = False
    used_latin = False

    braille = list()

    for letter in text:
        if letter in SEPARATORS:
            if state == 'number':
                state = ''

            braille.append(SEPARATORS[letter])

        elif letter in NUMBERS:
            if state != 'number':
                braille.append(CONTROLS['NEXT_NUMBER'])

            braille.append(NUMBERS[letter])
            state = 'number'

        elif letter in PUNCTUATION:
            braille.append(PUNCTUATION[letter])

        elif letter.lower() in LATIN and letter.isupper():
            braille.append(CONTROLS['NEXT_CAPITAL_LATIN'])
            braille.append(LATIN[letter.lower()])
            first_letter = first_letter or len(braille)
            state = 'latin' 
            used_latin = True

        elif letter in LATIN:
            if state != 'latin' and state != '':
                braille.append(CONTROLS['NEXT_SMALL_LATIN'])
                first_letter = first_letter or len(braille)

            braille.append(LATIN[letter])
            first_letter = first_letter or len(braille)
            state = 'latin'
            used_latin = True

        elif letter.lower() in RUSSIAN and letter.isupper():
            braille.append(CONTROLS['NEXT_CAPITAL_RUSSIAN'])

            braille.append(RUSSIAN[letter.lower()])
            first_letter = first_letter or len(braille)
            state = 'russian'
            used_russian = True

        elif letter in RUSSIAN:
            if state != 'russian' and state != '':
                braille.append(CONTROLS['NEXT_SMALL_RUSSIAN'])
                first_letter = first_letter or len(braille)

            braille.append(RUSSIAN[letter])
            first_letter = first_letter or len(braille)
            state = 'russian'
            used_russian = True

        else:
            print(f'Letter `{letter}` is not supported, replacing on `?`')
            braille.append(PUNCTUATION['?'])

    if first_letter is not None and used_latin and used_russian:
        first_letter -= 1
        letter = braille[first_letter]

        if letter in LATIN:
            braille.insert(first_letter, CONTROLS['NEXT_SMALL_LATIN'])
        elif letter in RUSSIAN:
            braille.insert(first_letter, CONTROLS['NEXT_SMALL_RUSSIAN'])

    return braille


def text_to_image(text: str) -> Image.Image:
    """Returns text from image with braille codes"""
    braille = text_to_braille(text)
    return braille_to_image(braille)


def braille_to_image(braille: list) -> Image.Image:
    """Returns image from braille codes"""
    w, h = 1, 1

    # Calculate image sizes in characters
    current_w = 0
    for letter in braille:
        if letter == 'NEWLINE':
            h += 1
            w = max(w, current_w)
            current_w = 0
        current_w += 1

    w = max(w, current_w)

    tile_w, tile_h = 2, 3
    image = Image.new(
        '1',
        (w * tile_w, h * tile_h),
        color=(255)
    )

    # Generate image
    x, y = 0, 0
    for letter in braille:
        if letter == 'NEWLINE':
            x = 0
            y += tile_h
            continue

        tile = TILES[letter]
        image.paste(tile, (x, y))
        x += tile_w

    image = image.convert('1')
    return image


def braille_to_text(braille):
    """Returns text from braille codes"""
    text = ''
    state = ''

    is_capital = False

    for letter in braille:
        if letter == 'NEXT_NUMBER':
            state = 'number'

        elif letter == 'NEXT_CAPITAL_LATIN':
            is_capital = True
            state = 'latin'

        elif letter == 'NEXT_SMALL_LATIN':
            state = 'latin'

        elif letter == 'NEXT_CAPITAL_RUSSIAN':
            is_capital = True
            state = 'russian'

        elif letter == 'NEXT_SMALL_RUSSIAN':
            state = 'russian'

        elif letter in SEPARATORS.values():
            text += key_for(SEPARATORS, letter)

            if state == 'number':
                state = ''

        elif state == 'number' and letter in NUMBERS.values():
            text += key_for(NUMBERS, letter)

        elif letter in PUNCTUATION.values():
            key = key_for(PUNCTUATION, letter)
            text += key

        elif letter in LATIN.values():
            key = key_for(LATIN, letter)
            if is_capital:
                key = key.capitalize()
                is_capital = False

            text += key

        elif letter in RUSSIAN.values():
            key = key_for(RUSSIAN, letter)
            if is_capital:
                key = key.capitalize()
                is_capital = False

            text += key

    return unquote(text)


def image_to_braille(image: Image.Image, language: Language = 'latin') -> str:
    """Returns braille codes for image"""
    braille = list()

    tile_w, tile_h = 2, 3
    img_w, img_h = image.size

    last_language = language
    state = language

    full_tiles_h = img_h // tile_h
    full_tiles_w = img_w // tile_w

    for y in range(0, full_tiles_h * tile_h, tile_h):
        for x in range(0, full_tiles_w * tile_w, tile_w):
            tile = image.crop((x, y, x + tile_w, y + tile_h)). get_flattened_data()

            # Get available representation
            letters = [
                letter for letter in TILES
                if TILES[letter].get_flattened_data() == tile
            ]

            if len(letters) == 1:
                if letters[0] == 'NEXT_NUMBER':
                    state = 'number'

                elif letters[0] == 'NEXT_CAPITAL_LATIN':
                    last_language = 'latin'
                    state = 'latin'

                elif letters[0] == 'NEXT_SMALL_LATIN':
                    last_language = 'latin'
                    state = 'latin'

                elif letters[0] == 'NEXT_CAPITAL_RUSSIAN':
                    last_language = 'russian'
                    state = 'russian'

                elif letters[0] == 'NEXT_SMALL_RUSSIAN':
                    last_language = 'russian'
                    state = 'russian'

                elif letters[0] in SEPARATORS.values():
                    if state == 'number':
                        state = last_language

                braille.append(letters[0])

            elif len(letters) > 1:
                if state == 'latin':
                    # Remove all russian suggestions
                    letters = [l for l in letters if l not in RUSSIAN]

                elif state == 'russian':
                    # Remove all latin suggestions
                    letters = [l for l in letters if l not in LATIN]

                elif state == 'number':
                    # Numbers ara written witn latin letters
                    letters = [l for l in letters if l in LATIN]

                    if letters[0] not in NUMBERS.values():
                        state = last_language

                braille.append(letters[0])

        braille.append('NEWLINE')

    # Remove last NEWLINE
    braille.pop(-1)

    return braille


def image_to_text(image: Image.Image, language: Language = 'latin') -> str:
    """Converts image to human readable text"""
    braille = image_to_braille(image=image, language=language)
    text = braille_to_text(braille)

    return text
