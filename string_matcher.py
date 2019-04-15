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

def main():
    compare_count = 0
    text = input("Input text: ")
    pattern = input("Pattern to search: ")

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

if __name__ == "__main__":
    main()
