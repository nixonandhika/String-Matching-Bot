import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import lib.tesaurus as tesaurus
import sys
import json
import itertools
from copy import copy

stopwords = [" ini", " itu", "kah", " kok",
             " lagian", "lah", "nah", "nya",
             " pun", " saja", " yang",
             "siapa ", " berapa", "berapa ",
             " apa", "apa ", "bagaimana ",
             "dimana ", " kali"]
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
        temp = pisah[0].lstrip('0123456789.- ')
        for word in stopwords:
            temp = copy(temp).lower().replace(word, "")
        pertanyaan_asli.append(pisah[0].lstrip('0123456789.- '))
        pertanyaan.append(stemmer.stem(temp).lower())
        jawaban.append(pisah[1].lstrip(' ').replace('\n', ' '))
    f.close()

#Baca kasus uji asisten
readFile("pertanyaan.txt")

#Baca kasus uji sendiri
readFile("qa.txt")

print(pertanyaan)

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

def find_fuzzy_match(match_string, text):
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
    return (count / n >= 0.9)


def build_multiple():
    temp = "Apakah yang Anda maksud:<BR>"
    for i in range(len(q_list)):
        if(i > 2):
            break;
        temp += "- " + q_list[i] + "?<BR>"
    return temp

def search_in_db(pattern):
    strip_pattern = re.sub(r"^\W+", "", pattern)
    strip_pattern = strip_pattern.lstrip('0123456789 ')
    if(len(strip_pattern) == 0):
        return json.dumps("Pertanyaan tidak valid, silahkan masukkan pertanyaan yang benar")

    if(pattern == "q_list"):
        temp = ""
        for question in pertanyaan_asli:
            temp += question + "?" + "<BR>";
        return json.dumps(temp)

    q_list.clear()

    temp = strip_pattern
    for word in stopwords:
        temp = copy(temp).lower().replace(word, "")
    strip_pattern = temp

    stemmedPattern = stemmer.stem(strip_pattern.lower().replace('?', ''))

    print(1)
    print(stemmedPattern)
    #Mencari yang exact match
    for question in pertanyaan:
        if(bmMatch(stemmedPattern, question) > -1):
            print(question)
            q_list.append(pertanyaan_asli[pertanyaan.index(question)])
    if(len(q_list) > 1):
        #return json.dumps(build_multiple())
        return build_multiple()
    elif(len(q_list) == 1):
        strip_pattern = q_list[0]
        temp = strip_pattern
        for word in stopwords:
            temp = copy(temp).lower().replace(word, "")
        strip_pattern = temp
        stemmedPattern = stemmer.stem(strip_pattern.lower().replace('?', ''))
        #return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])
        return jawaban[pertanyaan.index(stemmedPattern)]

    print(2)
    #Mencari yang mirip > 90%
    for question in pertanyaan:
        if(find_fuzzy_match(stemmedPattern, question)):
            q_list.append(pertanyaan_asli[pertanyaan.index(question)])
    if(len(q_list) > 1):
        #return json.dumps(build_multiple())
        return build_multiple()
    elif(len(q_list) == 1):
        strip_pattern = q_list[0]
        temp = strip_pattern
        for word in stopwords:
            temp = copy(temp).lower().replace(word, "")
        strip_pattern = temp
        stemmedPattern = stemmer.stem(strip_pattern.lower().replace('?', ''))
        #return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])
        return jawaban[pertanyaan.index(stemmedPattern)]

    print(3)
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
        # return json.dumps(build_multiple())
        return build_multiple()
    elif(len(q_list) == 1):
        strip_pattern = q_list[0]
        temp = strip_pattern
        for word in stopwords:
            temp = copy(temp).lower().replace(word, "")
        strip_pattern = temp
        stemmedPattern = stemmer.stem(strip_pattern.lower().replace('?', ''))
        # return json.dumps(jawaban[pertanyaan.index(stemmedPattern)])
        return jawaban[pertanyaan.index(stemmedPattern)]

    #Jika tidak ada yang ketemu
    # return json.dumps("Maaf, aku tidak mengerti pertanyaan Anda")
    return None

def main():
    pattern = sys.argv[1].replace('?', '')
    if(len(pattern.split()) == 1):
        print("Pertanyaan tidak valid, silahkan masukkan pertanyaan yang benar")
    else:
        splitTestString = pattern.split()
        for i in range(len(splitTestString)):
            tempList = [splitTestString[i]]
            for item in tesaurus.getSinonim(splitTestString[i]):
                tempList.append(item)
            splitTestString[i] = tempList
        splitPermutationTestString = list(itertools.product(*splitTestString))
        combinedTestString = []
        for i in range(len(splitPermutationTestString)):
            combinedTestString.append(' '.join(splitPermutationTestString[i]))
        for i in range(len(combinedTestString)):
            res = search_in_db(combinedTestString[i])
            if res is not None:
                print(res)
                break
            else:
                q_list.clear()

if __name__ == "__main__":
    main()
    #print(search_in_db(sys.argv[1]))
