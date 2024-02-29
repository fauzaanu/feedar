# taken from dh2en from a js library that doesnt actually work
# todo: make it work

vowels = {
    "ަ": "a",
    "ާ": "aa",
    "ި": "i",
    "ީ": "ee",
    "ު": "u",
    "ޫ": "oo",
    "ެ": "e",
    "ޭ": "ey",
    "ޮ": "o",
    "ޯ": "oa",
    "ް": ""
}

sukun_words = {
    "ް": "h"
}

alif_compounds = {
    "އަ": "a",
    "އާ": "aa",
    "އި": "i",
    "އީ": "ee",
    "އު": "u",
    "އޫ": "oo",
    "އެ": "e",
    "އޭ": "ey",
    "އޮ": "o",
    "އޯ": "oa"
}

consonants = {
    "ހ": "h",
    "ށ": "sh",
    "ނ": "n",
    "ރ": "r",
    "ބ": "b",
    "ޅ": "lh",
    "ކ": "k",
    "އ": "",
    "ވ": "v",
    "މ": "m",
    "ފ": "f",
    "ދ": "dh",
    "ތ": "th",
    "ލ": "l",
    "ގ": "g",
    "ޏ": "y",
    "ސ": "s",
    "ޑ": "d",
    "ޒ": "z",
    "ޓ": "t",
    "ޔ": "y",
    "ޕ": "p",
    "ޖ": "j",
    "ޗ": "ch",
    "ޙ": "h",
    "ޚ": "kh",
    "ޛ": "z",
    "ޜ": "z",
    "ޝ": "sh"
}

punctuations = {
    "]": "[",
    "[": "]",
    "\\": "\\",
    "\'": "\'",
    "،": ",",
    ".": ".",
    "/": "/",
    "÷": "",
    "}": "{",
    "{": "}",
    "|": "|",
    ":": ":",
    "\"": "\"",
    ">": "<",
    "<": ">",
    "؟": "?",
    ")": ")",
    "(": "("
}

def thaana_to_latin(text):
    for key, value in vowels.items():
        text = text.replace(key, value)
    for key, value in alif_compounds.items():
        text = text.replace(key, value)
    for key, value in consonants.items():
        text = text.replace(key, value)
    for key, value in punctuations.items():
        text = text.replace(key, value)
    for key, value in sukun_words.items():
        text = text.replace(key, value)
    return text


# letting copilot do it first
if __name__ == "__main__":
    print(thaana_to_latin("ކަޅުތުއްކަލާކޮށި"))

