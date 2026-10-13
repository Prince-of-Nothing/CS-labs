package main

const romanianAlphabet = "AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ"

func caesarCipher(message []rune, key int, encrypt bool) string {
	alphabet := []rune(romanianAlphabet)
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
