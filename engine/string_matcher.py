import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import lib.tesaurus as tesaurus
import sys
import json

factory = StemmerFactory()
stemmer = factory.create_stemmer()

pertanyaan_asli = []
pertanyaan = []
jawaban = []
q_list = []

#Baca file
def readFile(filename):
    f = open("database/" + filename, "r")
    if(f.mode == 'r'):
        content = f.readlines()
    for i in range(len(content)):
        pisah = re.split("[?]", content[i])
        pertanyaan_asli.append(pisah[0].lstrip('0123456789.- '))
        pertanyaan.append(stemmer.stem(pisah[0].lstrip('0123456789.- ').lower()))
        jawaban.append(pisah[1].lstrip(' ').replace('\n', ' '))
    f.close()

#Baca kasus uji asisten
readFile("pertanyaan.txt")

#Baca kasus uji sendiri
readFile("qa.txt")

def buildLast(pattern):
    dict = {}
    for letter in pattern:
        dict[letter] = pattern.rfind(letter)
    return dict

def bmMatch(pattern, text):
    dict = buildLast(pattern)
    n = len(text)
    m = len(pattern)
    i = m - 1
    if(i > n - 1):
        return -1
    j = m - 1
    while True:
        if(pattern[j] == text[i]):
            if(j == 0):
                return i
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
    return -1

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

def kmpMatch(pattern, text):
    n = len(text)
    m = len(pattern)
    fail = computeFail(pattern)
    i = 0
    j = 0
    while(i < n):
        if(pattern[j] == text[i]):
            if(j == m - 1):
                return (i - m + 1)
            i += 1
            j += 1
        elif(j > 0):
            j = fail[j-1]
        else:
            i += 1
    return -1

#TEMPORARY DATABASE FOR WORDS THAT ARE INCLUDED IN THE QUESTIONS DATABASE
# listBaseWords = ['apa','tengah','nama', 'ada','di']
#
# def extractKata(text):
#     # create stemmer for sastrawi
#     factory = StemmerFactory()
#     stemmer = factory.create_stemmer()
#     splitText = text.split()
#     #print(splitText)
#     for i in range(0,len(splitText)):
#         j = 0
#         found = False
#         while (not(found)) and (j < len(listBaseWords)):
#             #print(splitText[i],listBaseWords[j])
#             if splitText[i] in tesaurus.getSinonim(listBaseWords[j]):
#                 splitText[i] = listBaseWords[j]
#                 found = True
#             else:
#                 j += 1
#     #print(splitText)
#     combinedText = ' '.join(splitText)
#     stemmedCombinedText = stemmer.stem(combinedText)
#     #print(stemmedCombinedText)
#     return stemmedCombinedText

def find_fuzzy_match(match_string, text):
    # use an iterator so that we can skip to the end of a match.
    # text_iter = enumerate(text)
    # for index, char in text_iter:
    #     try:
    #         match_start = match_string.index(char)
    #     except ValueError:
    #         continue
    #     match_count = 0
    #     zip_char = zip(match_string[match_start:], text[index:])
    #     for match_index, (match_char, text_char) in enumerate(zip_char):
    #         if match_char == text_char:
    #             match_count += 1
    #             last_match = match_index
    #     if match_count >= len(match_string) * 0.9:
    #         #yield index, index + last_match
    #         yield True
    #         # Advance the iterator past the match
    #         for x in range(last_match):
    #             next(text_iter)
    count = 0
    n = len(match_string)
    m = len(text)
    limit = 0
    if(n > m):
        limit = m
    else:
        limit = n
    for i in range(limit):
        if(match_string[i] == text[i]):
            count += 1
        else:
            break
    return (count / n >= 0.9)


def build_multiple():
    temp = "Apakah yang Anda maksud:<BR>"
    for i in range(len(q_list)):
        if(i > 2):
            break;
        temp += str(i+1) + ". " + q_list[i] + "?<BR>"
    return temp

def search_in_db(pattern):
    strip_pattern = re.sub(r"^\W+", "", pattern)
    strip_pattern = strip_pattern.lstrip('0123456789 ')
    if(len(strip_pattern) == 0):
        return json.dumps("Pertanyaan tidak valid, silahkan masukkan pertanyaan yang benar")

    #Untuk menerima bagian yang lebih dari satu kemungkinan
    if(pattern == "1"):
        stemmedPattern = stemmer.stem(q_list[0].lower().replace('?', ''))
        return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])
    elif(pattern == "2"):
        stemmedPattern = stemmer.stem(q_list[1].lower().replace('?', ''))
        return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])
    elif(pattern == "3"):
        stemmedPattern = stemmer.stem(q_list[2].lower().replace('?', ''))
        return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])
    else:
        q_list.clear()

    stemmedPattern = stemmer.stem(strip_pattern.lower().replace('?', ''))

    #Mencari yang exact match
    for question in pertanyaan:
        if(bmMatch(stemmedPattern, question) > -1):
            q_list.append(pertanyaan_asli[pertanyaan.index(question)])
    if(len(q_list) > 1):
        return json.dumps(build_multiple())
    elif(len(q_list) == 1):
        stemmedPattern = stemmer.stem(q_list[0].lower().replace('?', ''))
        return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])

    #Mencari yang mirip > 90%
    for question in pertanyaan:
        if(find_fuzzy_match(stemmedPattern, question)):
            q_list.append(pertanyaan_asli[pertanyaan.index(question)])
    if(len(q_list) > 1):
        return json.dumps(build_multiple())
    elif(len(q_list) == 1):
        stemmedPattern = stemmer.stem(q_list[0].lower().replace('?', ''))
        return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])

    #Regex
    get_word = re.findall(r'^\w+|\w+$', stemmedPattern)
    if(len(get_word) > 1):
        src_rx = r'' + re.escape(get_word[0]) + r'(.*?)' + re.escape(get_word[1])
    else:
        src_rx = r'' + re.escape(get_word[0]) + r'(.*?)'
    for question in pertanyaan:
        if(re.search(src_rx, question, re.IGNORECASE)):
            q_list.append(pertanyaan_asli[pertanyaan.index(question)])
    if(len(q_list) > 1):
        return json.dumps(build_multiple())
    elif(len(q_list) == 1):
        stemmedPattern = stemmer.stem(q_list[0].lower().replace('?', ''))
        return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])

    #Jika tidak ada yang ketemu
    return json.dumps("Maaf, saya tidak mengerti pertanyaan Anda")

def main():
    # compare_count = 0
    # text = input("Input text: ").lower()
    pattern = input("Pattern to search: ")
    #
    # print()
    #
    # print("Pattern search with KMP: ")
    # res, compare_count = kmpMatch(text, pattern)
    # print("Total comparison: " + str(compare_count))
    # if(res == -1):
    #     print("Pattern not found")
    # else:
    #     print("Pattern found in idx: " + str(res))
    #
    # print()
    #
    # print("Pattern search with BM: ")
    # res, compare_count = bmMatch(text, pattern)
    # print("Total comparison: " + str(compare_count))
    # if(res == -1):
    #     print("Pattern not found")
    # else:
    #     print("Pattern found in idx: " + str(res))

    # print("Input Text: Apa julukan blackhole yang hadir dalam pusat galaksi bimasakti itu?")
    # print("Testing to find:",stemmer.stem(testPattern))
    # extractedText = extractKata(testText)
    # stemmedPattern = stemmer.stem(pattern)
    # print("Question in Database:",str(stemmedPattern))
    # print("Extracted Text after it is changed:",str(extractedText))
    # x = find_fuzzy_match(str(stemmedPattern),str(extractedText))
    # if True in x:
    #     print("Blackhole M8715")
    res = search_in_db(pattern)
    print(res)
    if(len(q_list) > 1):
        pattern = input("> ")
        res = search_in_db(pattern)
        print(res)

if __name__ == "__main__":
    # main()
    print(search_in_db(sys.argv[1]))
