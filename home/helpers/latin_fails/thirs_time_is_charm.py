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
    # "ް": ""
}

double_vowels = {
    "ަަ": "aa",
    "ާާ": "aa",
    "ިި": "ii",
    "ީީ": "ii",
    "ުު": "uu",
    "ޫޫ": "uu",
    "ެެ": "ee",
    "ޭޭ": "ey",
    "ޮޮ": "oo",
    "ޯޯ": "oa",
}

sukun_words = {
    "އް": "h",
    "ސް": "s",
    "ން": "n",
    "ށް": "h",
    "ތް": "iy",
}

alif_remaining = {
    "އ": "އަ",
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

cl = {
    "ހ": "h",
    "ށ": "sh",
    "ނ": "n",
    "ރ": "r",
    "ބ": "b",
    "ޅ": "lh",
    "ކ": "k",
    "ވ": "v",
    "މ": "m",
    "ފ": "f",
    "ދ": "dh",  #
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
    "ޗ": "ch",  #
    "ޙ": "h",
    "ޚ": "kh",
    "ޛ": "z",
    "ޜ": "z",
    "ޝ": "sh"
}

double_consonants = [
    "dh", "th", "lh", "sh", "ch", "kh"
]

sukunables = [
    "އ", "ސ", "ނ", "ށ", "ތ"
]

punctuations = {
    "]": "[",
    "[": "]",
    "\\": "\\",
    "\'": "\'",
    "،": ",",
    ".": ".",
    "/": "/",
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


# ha
# hu
# hi
# ho
# haa
# hee
# hoa
# hoo
# hey
# he

# basically when a letter is a consonant, it can be followed by a vowel

# it can be followed by a sukun only if it is sukunable

def latin_to_thaana(word):
    consonent_pos = []
    parts = []
    double_consonent_pos = []

    # get the positions of the double consonents
    for dc in double_consonants:
        if dc in word:
            double_consonent_pos.append((dc, word.index(dc), word.index(dc) + 1))

    # get the position of the consonents
    for key, value in cl.items():
        if value in word:
            consonent_pos.append((value, word.index(value), word.index(value)))

    next_consonent_pos = double_consonent_pos.copy()
    # for each double consonent, check if it is followed by a double vowel first
    for consonent, start_pos, end_pos in double_consonent_pos:
        cwdv = word[end_pos+1:end_pos + 3]
        actual_word = word[start_pos:end_pos + 3]
        #print(cwdv)

        if cwdv in double_vowels.values():
            parts.append(actual_word)
            # remove the consonent position so that we don't check for it again
            next_consonent_pos.remove((consonent, start_pos, end_pos))

    next_consonent_pos = consonent_pos.copy()
    # for each consonent, check if it is followed by a double vowel first
    for consonent, start_pos, end_pos in consonent_pos:
        cwdv = word[end_pos+1:end_pos + 2]
        actual_word = word[start_pos:end_pos + 2]
        print(actual_word)

        if cwdv in double_vowels.values():
            parts.append(actual_word)
            # remove the consonent position so that we don't check for it again
            next_consonent_pos.remove((consonent, start_pos, end_pos))

    print(parts)
    print(next_consonent_pos)


latin_to_thaana("dhaanaa")
