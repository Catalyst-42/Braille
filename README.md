# Braille
Simple generated scripts to convert text into braille image and braille image back to text. Make on Python with numpy and Pillow. To use, install dependencies first:

> [!Warning]
This code is clean, but highly AI generated, don't use it to learning purposes

```
pip3 install -r requirements.txt
```

## Converting to Braille
To encode image use `to_braille` script. It will demand an input text and will output converted image. Image will be located at script folder and will be named `output.png`. Braille glyphs used to create image are stored in `parts` folder. The list of available glyphs is:

| ` abcdefghijklmnopqrstuvwxyzAN.,?;!''()-` |
|-|
| ![Example of tiles](img/tiles_example.png) |

You also can use capital letters and digits from zero to nine, but they will be encoded by Braille 1 rules. In output you will get an image, created with glyphs of tileset.

## Converting from Braille
To convert image from braille you need to initially get clear image, which intains characted, mapped on tileset. All glyphs must be located in one line. Internally Braille uses codes to describe special charactes. There's two types of them: capital letters and numericals.

Rules for capital letters:
- Each capital letter should be prepended with capital letter sign "A".

Examples:
```
Hello -> Ahello
WIP   -> AwAiAp
mIxEd -> mAixAed
```

Rules for numbers:
- Numbers are encoded with letters (a.e. 112 is aab)
- Number sequence must be prepended with number sequence sign "N".
- Number sequence breaks on space or on alpha symbol (a.e 1a2b is N)

Examples:
```
100 cats -> Najj cats
1ac      -> Na;c
500,000  -> Nejj,jjj
4C       -> Nd;Ac
```

> [!NOTE]  
> when creating text you dont need to pass special signs to describe sequences of capital letters and numericals. When you converting braille image back to text you need to read text according to rules, described above.
