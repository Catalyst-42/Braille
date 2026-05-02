from braille import quote
from braille import text_to_braille
from braille import braille_to_text
from braille import text_to_image
from braille import image_to_text
from braille import Language

# Some reversable aliases
def text_image_text(text, language: Language = 'latin'):
    return image_to_text(text_to_image(text), language)


def text_braille_text(text):
    return braille_to_text(text_to_braille(text))


# Tests
def test_quotes():
    assert quote('"a"') == '⌊a⌋'
    assert quote('"a" \'b\' `c`') == '⌊a⌋ ⌊b⌋ ⌊c⌋'
    assert quote('"\' a \'"') == '⌊⌊ a ⌋⌋'
    assert quote('a\' b "c\' d "e') == 'a⌊ b ⌊c⌋ d ⌋e'
    assert quote('"a" b "c"') == '⌊a⌋ b ⌊c⌋'


def test_simple():
    assert text_to_braille('hello') == ['h', 'e', 'l', 'l', 'o']
    assert text_to_braille('привет') == ['п', 'р', 'и', 'в', 'е', 'т']


def test_controls():
    assert text_to_braille('ZZ zz') == ['NEXT_CAPITAL_LATIN', 'z', 'NEXT_CAPITAL_LATIN', 'z', 'SPACE', 'z', 'z']
    assert text_to_braille('ЯЯ яя') == ['NEXT_CAPITAL_RUSSIAN', 'я', 'NEXT_CAPITAL_RUSSIAN', 'я', 'SPACE', 'я', 'я']
    assert text_to_braille('a? b!') == ['a', 'QUESTION_MARK', 'SPACE', 'b', 'EXCLAMATION_MARK']
    assert text_to_braille('"w"') == ['OPEN_QUOTE', 'w', 'CLOSE_QUOTE']
    assert text_to_braille('"\'b\'"') == ['OPEN_QUOTE', 'OPEN_QUOTE', 'b', 'CLOSE_QUOTE', 'CLOSE_QUOTE']


def test_capitals():
    assert text_to_braille('ALL') == ['NEXT_CAPITAL_LATIN', 'a', 'NEXT_CAPITAL_LATIN', 'l', 'NEXT_CAPITAL_LATIN', 'l']
    assert text_to_braille('ВСЁ') == ['NEXT_CAPITAL_RUSSIAN', 'в', 'NEXT_CAPITAL_RUSSIAN', 'с', 'NEXT_CAPITAL_RUSSIAN', 'ё']


def test_mixed():
    assert text_to_braille('abc абв') == ['NEXT_SMALL_LATIN', 'a', 'b', 'c', 'SPACE', 'NEXT_SMALL_RUSSIAN', 'а', 'б', 'в']
    assert text_to_braille('123 abc') == ['NEXT_NUMBER', 'a', 'b', 'c', 'SPACE', 'a', 'b', 'c']
    assert text_to_braille('abc 123 abc') == ['a', 'b', 'c', 'SPACE', 'NEXT_NUMBER', 'a', 'b', 'c', 'SPACE', 'a', 'b', 'c']
    assert text_to_braille('pri при pri при') == ['NEXT_SMALL_LATIN', 'p', 'r', 'i', 'SPACE', 'NEXT_SMALL_RUSSIAN', 'п', 'р', 'и', 'SPACE', 'NEXT_SMALL_LATIN', 'p', 'r', 'i', 'SPACE', 'NEXT_SMALL_RUSSIAN', 'п', 'р', 'и']
    assert text_to_braille('при pri при') == ['NEXT_SMALL_RUSSIAN', 'п', 'р', 'и', 'SPACE', 'NEXT_SMALL_LATIN', 'p', 'r', 'i', 'SPACE', 'NEXT_SMALL_RUSSIAN', 'п', 'р', 'и']
    assert text_to_braille('Си Wi, и ду') == ['NEXT_CAPITAL_RUSSIAN', 'с', 'и', 'SPACE', 'NEXT_CAPITAL_LATIN', 'w', 'i', 'COMMA', 'SPACE', 'NEXT_SMALL_RUSSIAN', 'и', 'SPACE', 'д', 'у']
    assert text_to_braille('Бы 7, 4 un 5!') == ['NEXT_CAPITAL_RUSSIAN', 'б', 'ы', 'SPACE', 'NEXT_NUMBER', 'g', 'COMMA', 'SPACE', 'NEXT_NUMBER', 'd', 'SPACE', 'NEXT_SMALL_LATIN', 'u', 'n', 'SPACE', 'NEXT_NUMBER', 'e', 'EXCLAMATION_MARK']

def test_numbers():
    assert text_to_braille('11 ab') == ['NEXT_NUMBER', 'a', 'a', 'SPACE', 'a', 'b']
    assert text_to_braille('11 вг') == ['NEXT_NUMBER', 'a', 'a', 'SPACE', 'в', 'г']
    assert text_to_braille('1a2b') == ['NEXT_NUMBER', 'a', 'NEXT_SMALL_LATIN', 'a', 'NEXT_NUMBER', 'b', 'NEXT_SMALL_LATIN', 'b']
    assert text_to_braille('12.34') == ['NEXT_NUMBER', 'a', 'b', 'DOT', 'c', 'd']
    assert text_to_braille('12.,.34') == ['NEXT_NUMBER', 'a', 'b', 'DOT', 'COMMA', 'DOT', 'c', 'd']


def test_text():
    assert text_braille_text('hello') == 'hello'
    assert text_braille_text('привет') == 'привет'
    assert text_braille_text('123') == '123'
    assert text_braille_text('123 абв abc .,!') == '123 абв abc .,!'

    assert text_braille_text('133FCA') == '133FCA'
    assert text_braille_text('133АБВ') == '133АБВ'
    assert text_braille_text('123где') == '123где'
    assert text_braille_text('123def') == '123def'

    assert text_braille_text('13аВо3Fd,.;23fва') == '13аВо3Fd,.;23fва'


def test_images():
    assert text_image_text('Hello') == 'Hello'
    assert text_image_text('Привет') == 'Привет'

    assert text_image_text('hello') == 'hello'
    assert text_image_text('привет', 'russian') == 'привет'

    assert text_image_text('123 hour') == '123 hour'
    assert text_image_text('123 часа', 'russian') == '123 часа'
    assert text_image_text('123 часа hours', 'russian') == '123 часа hours'
    assert text_image_text('123 часа hours') == '123 часа hours'

    assert text_image_text('11.23 рубли', 'russian') == '11.23 рубли'
    assert text_image_text('"Иди ка ты" - сказал он мне', 'russian') == '"Иди ка ты" - сказал он мне'
    assert text_image_text('"Иди ка ты" - сказал он мне') == '"Иди ка ты" - сказал он мне'

    assert text_image_text('long story начинается') == 'long story начинается'
    assert text_image_text('long story начинается', 'russian') == 'long story начинается'
    assert text_image_text('long story привет begin начинается', 'russian') == 'long story привет begin начинается'

    assert text_image_text('hello привет hello привет') == 'hello привет hello привет'

    assert text_image_text('long') == 'long'
    assert text_image_text('long', 'russian') == 'лонг'

    assert text_image_text('колбаса tastefull колбаса') == 'колбаса tastefull колбаса'
    assert text_image_text('колбаса tastefull колбаса', 'russian') == 'колбаса tastefull колбаса'
    assert text_image_text('123 123 колбаса tastefull колбаса', 'russian') == '123 123 колбаса tastefull колбаса'
    assert text_image_text('123 123 колбаса tastefull full колбаса') == '123 123 колбаса tastefull full колбаса'

    assert text_image_text('123 wor 123 12.23 war') == '123 wor 123 12.23 war'
    assert text_image_text('123 вор 123 12.23 вар', 'russian') == '123 вор 123 12.23 вар'

    assert text_image_text('˚∆˚') == '???'


def test_punctuation():
    assert text_image_text('Система Windows, и дургие') == 'Система Windows, и дургие'
    assert text_image_text('Было 7, 3, и 4 units 5!') == 'Было 7, 3, и 4 units 5!'
    assert text_image_text('Was 23 ря. ру si 34. ков') == 'Was 23 ря. ру si 34. ков'
    assert text_image_text('Я Z 1 . я z 1 ,') == 'Я Z 1 . я z 1 ,'
    assert text_image_text('ядzombie') == 'ядzombie'
    assert text_image_text('яд-11zombie') == 'яд-11zombie'
    assert text_image_text('34KвЧjмсd2ds') == '34KвЧjмсd2ds'
    assert text_image_text('При. What ur делаешь?') == 'При. What ur делаешь?'


def test_transliteration():
    def text_to_text(text, language: Language = 'latin'):
        return image_to_text(text_to_image(text), language)

    assert text_to_text('hello', 'russian') == 'хелло'
    assert text_to_text('привет') == 'priwet'
    assert text_to_text('hello world', 'russian') == 'хелло ворлд'


def test_full():

    pangramm_ru = '- Эх, йог зряч, съел мёд "Жуть дюн". Щипцы б в шкаф.' 
    pangramm_en = 'Sphinx of black quartz, judge my vow' 
    assert text_image_text(pangramm_ru, 'russian') == pangramm_ru
    assert text_image_text(pangramm_en) == pangramm_en

    assert text_image_text(pangramm_ru + pangramm_en) == pangramm_ru + pangramm_en
