# A new strategy to split the words first and then run the converter
# more efficient and less error prone maybe. lets find out
from pprint import pprint

# letter+a = ra = ރަ
# letter+e = re = ރެ
# letter+i = ri = ރި
# letter+o = ro = ރޮ
# letter+u = ru = ރު
# letter+aa = raa = ރާ
# letter+ee = ree = ރީ
# letter+ey = rey = ރޭ
# letter+oo = roo = ރޫ
# letter+oa = roa = ރޯ

vowels = [
    "a", "aa", "i", "ee", "u", "oo", "e", "ey", "o", "oa"
]

sukuns = [
    "s", "n", "h", "y"  # alif and shaviyani takes the same "h" sound
]

consonants = [
    "h", "sh", "n", "r", "b", "lh", "k", "v", "m", "f", "dh", "th", "l", "g", "y", "s", "d", "z"
]

# combinations that can happen
# 1. consonant + vowel
# 2. consonant + sukun can never happen
# 3. consonant + vowel + sukun

all_parts = vowels + sukuns + consonants

combinations = []
for consonant in consonants:
    for vowel in vowels:
        combinations.append(consonant + vowel)

        for sukun in sukuns:
            combinations.append(consonant + vowel + sukun)

all_parts += combinations


# pprint(all_parts)
def split_word(word):
    # split the word into the relevant parts (consonant, vowel, sukun)
    length = len(word)
    parts = set()
    for i in range(length):
        word = word[i:]
        # split the word to portions
        for part in combinations:
            if part in word:
                parts.add(part)
                word = word.replace(part, "")
                print(f"Adding: {part}")
                print(f"Remaining: {word}")



    # only vowels can be alone
    # {'a', 'k', 'u', 'ku', 'ru', 'r'}
    # if a vowel is alone, it must be the letter "a"
    # remove the rest of the vowels that are alone as they would be
    # present in a joint way for example: k and u would be ku
    # {'a', 'ku', 'ru'}
    removal = parts.copy()
    for part in parts:
        if part in vowels or len(part) == 1:
            if part != "a":
                removal.remove(part)
                print(f"Removing: {part}")

    print(removal)


if __name__ == "__main__":
    split_word("harudhanaa")
