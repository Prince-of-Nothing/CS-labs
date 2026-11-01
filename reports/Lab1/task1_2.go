package main

func buildPermutedAlphabet(keyword []rune) []rune {
	result := make([]rune, 0, len([]rune(romanianAlphabet)))
	included := make(map[rune]bool)
	for _, letter := range append(keyword, []rune(romanianAlphabet)...) {
		if isRomanianLetter(letter) && !included[letter] {
			result = append(result, letter)
			included[letter] = true
		}
	}
	return result
}

func keywordCaesarCipher(message, alphabet []rune, key int, encrypt bool) string {
	letterCodes := make(map[rune]int, len(alphabet))
	for code, letter := range alphabet {
		letterCodes[letter] = code
	}

	result := make([]rune, 0, len(message))
	for _, letter := range message {
		code := letterCodes[letter]
		if encrypt {
			code = (code + key) % len(alphabet)
		} else {
			code = (code - key + len(alphabet)) % len(alphabet)
		}
		result = append(result, alphabet[code])
	}
	return string(result)
}
