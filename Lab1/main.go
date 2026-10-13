package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

var input = bufio.NewScanner(os.Stdin)

func main() {
	fmt.Println("Romanian Caesar Ciphers")
	fmt.Println("1. Caesar cipher")
	fmt.Println("2. Caesar cipher with keyword permutation")

	cipherType := readChoice("Choose cipher (1-2): ", 1, 2)
	fmt.Println("1. Encrypt")
	fmt.Println("2. Decrypt")
	operation := readChoice("Choose operation (1-2): ", 1, 2)
	shift := readShift()

	var keyword []rune
	if cipherType == 2 {
		keyword = readKeyword()
		alphabet := buildPermutedAlphabet(keyword)
		fmt.Printf("Permuted alphabet: %s\n", joinRunes(alphabet, " "))
	}

	message := readMessage()
	var result string
	if cipherType == 1 {
		result = caesarCipher(message, shift, operation == 1)
	} else {
		result = keywordCaesarCipher(message, buildPermutedAlphabet(keyword), shift, operation == 1)
	}
	if operation == 1 {
		fmt.Printf("Ciphertext: %s\n", result)
	} else {
		fmt.Printf("Plaintext: %s\n", result)
	}
}

func readLine(prompt string) string {
	fmt.Print(prompt)
	if !input.Scan() {
		os.Exit(0)
	}
	return input.Text()
}

func readChoice(prompt string, minimum, maximum int) int {
	for {
		value := readLine(prompt)
		choice, err := strconv.Atoi(strings.TrimSpace(value))
		if err == nil && choice >= minimum && choice <= maximum {
			return choice
		}
		fmt.Printf("Invalid choice. Enter an integer from %d to %d.\n", minimum, maximum)
	}
}

func readShift() int {
	for {
		value := readLine("Enter numeric key k (1-30): ")
		shift, err := strconv.Atoi(strings.TrimSpace(value))
		if err == nil && shift >= 1 && shift <= 30 {
			return shift
		}
		fmt.Println("Invalid key. The numeric key must be an integer from 1 to 30.")
	}
}

func readKeyword() []rune {
	for {
		keyword := normalize(readLine("Enter keyword (at least 7 Romanian letters): "))
		if invalid, ok := firstInvalid(keyword, false); ok {
			fmt.Printf("Invalid keyword character '%c'. Use only Romanian alphabet letters.\n", invalid)
			continue
		}
		if len([]rune(keyword)) < 7 {
			fmt.Println("Invalid keyword. It must contain at least 7 Romanian alphabet letters.")
			continue
		}
		return []rune(keyword)
	}
}

func readMessage() []rune {
	for {
		message := strings.ReplaceAll(normalize(readLine("Enter message (spaces are removed): ")), " ", "")
		if len(message) == 0 {
			fmt.Println("Invalid text. Enter at least one Romanian alphabet letter.")
			continue
		}
		if invalid, ok := firstInvalid(message, false); ok {
			fmt.Printf("Invalid character '%c'. Use only Romanian alphabet letters and spaces.\n", invalid)
			continue
		}
		return []rune(message)
	}
}

func normalize(value string) string {
	value = strings.ToUpper(value)
	value = strings.ReplaceAll(value, "Ş", "Ș")
	value = strings.ReplaceAll(value, "Ţ", "Ț")
	return value
}

func firstInvalid(value string, allowSpaces bool) (rune, bool) {
	for _, character := range value {
		if (allowSpaces && character == ' ') || isRomanianLetter(character) {
			continue
		}
		return character, true
	}
	return 0, false
}

func isRomanianLetter(character rune) bool {
	return strings.ContainsRune(romanianAlphabet, character)
}

func joinRunes(values []rune, separator string) string {
	parts := make([]string, len(values))
	for index, value := range values {
		parts[index] = string(value)
	}
	return strings.Join(parts, separator)
}
