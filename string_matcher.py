import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import lib.tesaurus as tesaurus

def buildLast(pattern):
    dict = {}
    for letter in pattern:
        dict[letter] = pattern.rfind(letter)
    return dict

def bmMatch(text, pattern):
    count = 0
    dict = buildLast(pattern)
    n = len(text)
    m = len(pattern)
    i = m - 1
    if(i > n - 1):
        return -1
    j = m - 1
    while True:
        count += 1
        if(pattern[j] == text[i]):
            if(j == 0):
                return i, count
            else:
                i -= 1
                j -= 1
        else:
            if(text[i] not in dict):
                lo = -1
            else:
                lo = dict[text[i]]
            i = i + m - min(j, 1+lo)
            j = m - 1
        if(i > n - 1):
            break
    return -1, count

def computeFail(pattern):
    m = len(pattern)
    fail = [0] * m
    j = 0
    i = 1
    while(i < m):
        if(pattern[i] == pattern[j]):
            j += 1
            fail[i] = j
            i += 1
        else:
            if(j == 0):
                fail[i] = 0
                i += 1
            else:
                j = fail[j-1]
    return fail

def kmpMatch(text, pattern):
    count = 0
    n = len(text)
    m = len(pattern)
    fail = computeFail(pattern)
    i = 0
    j = 0
    while(i < n):
        count += 1
        if(pattern[j] == text[i]):
            if(j == m - 1):
                return (i - m + 1), count
            i += 1
            j += 1
        elif(j > 0):
            j = fail[j-1]
        else:
            i += 1
    return -1, count

#TEMPORARY DATABASE FOR WORDS THAT ARE INCLUDED IN THE QUESTIONS DATABASE
listBaseWords = ['apa','tengah','nama', 'ada','di']

def extractKata(text):
    # create stemmer for sastrawi
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    splitText = text.split()
    #print(splitText)
    for i in range(0,len(splitText)):
        j = 0
        found = False
        while (not(found)) and (j < len(listBaseWords)):
            #print(splitText[i],listBaseWords[j])
            if splitText[i] in tesaurus.getSinonim(listBaseWords[j]):
                splitText[i] = listBaseWords[j]
                found = True
            else:
                j += 1
    #print(splitText)
    combinedText = ' '.join(splitText)
    stemmedCombinedText = stemmer.stem(combinedText)
    #print(stemmedCombinedText)
    return stemmedCombinedText

def find_fuzzy_match(match_string, text):
    # use an iterator so that we can skip to the end of a match.
    text_iter = enumerate(text)
    for index, char in text_iter:
        try:
            match_start = match_string.index(char)
        except ValueError:
            continue
        match_count = 0
        zip_char = zip(match_string[match_start:], text[index:])
        for match_index, (match_char, text_char) in enumerate(zip_char):
            if match_char == text_char:
                match_count += 1
                last_match = match_index
        if match_count >= len(match_string) * 0.9:
            #yield index, index + last_match
            yield True
            # Advance the iterator past the match
            for x in range(last_match):
                next(text_iter)    

def main():
    #Testing Sastrawi
    testText = "Apa julukan blackhole yang hadir dalam pusat galaksi bimasakti itu?"
    testPattern = "Apa nama blackhole yang berada di tengah galaksi bimasakti?"
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    #End Test
    compare_count = 0
    text = input("Input text: ").lower()
    pattern = input("Pattern to search: ").lower()

    print()

    print("Pattern search with KMP: ")
    res, compare_count = kmpMatch(text, pattern)
    print("Total comparison: " + str(compare_count))
    if(res == -1):
        print("Pattern not found")
    else:
        print("Pattern found in idx: " + str(res))

    print()

    print("Pattern search with BM: ")
    res, compare_count = bmMatch(text, pattern)
    print("Total comparison: " + str(compare_count))
    if(res == -1):
        print("Pattern not found")
    else:
        print("Pattern found in idx: " + str(res))

    print("Input Text: Apa julukan blackhole yang hadir dalam pusat galaksi bimasakti itu?")
    print("Testing to find:",stemmer.stem(testPattern))
    extractedText = extractKata(testText)
    stemmedPattern = stemmer.stem(testPattern)
    print("Question in Database:",str(stemmedPattern))
    print("Extracted Text after it is changed:",str(extractedText))
    x = find_fuzzy_match(str(stemmedPattern),str(extractedText))
    if True in x:
        print("Blackhole M8715")
    

if __name__ == "__main__":
    main()
