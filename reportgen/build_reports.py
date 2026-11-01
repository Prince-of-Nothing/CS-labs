#!/usr/bin/env python3
"""Generate the six UTM laboratory reports (.docx) for Labs 1-6.

Renders terminal-screenshot PNGs from the captured program runs and embeds
them, together with theory, implementation fragments and conclusions, into
Word documents styled after the UTM/FCIM template.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render_terminal, render_excerpt  # noqa: E402
import utm_doc as U  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = os.path.join(REPO, "reportgen", "captures")   # tracked: builds must not
                                                    # depend on /tmp surviving
IMG = os.path.join(REPO, "reportgen", "img")
OUT = REPO
URL = "https://github.com/Prince-of-Nothing/CS-labs.git"


def read(*names):
    parts = []
    for n in names:
        with open(n, encoding="utf-8") as f:
            parts.append(f.read())
    return "\n".join(parts)


def shot(name, lines, **kw):
    path = os.path.join(IMG, name)
    render_terminal(lines, path, **kw)
    return path


def shot_excerpt(name, text, start=None, end=None, **kw):
    path = os.path.join(IMG, name)
    render_excerpt(text, path, start=start, end=end, **kw)
    return path


# --------------------------------------------------------------------------
# Lab 1
# --------------------------------------------------------------------------
def build_lab1():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 1, "Caesar cipher and Caesar cipher with a keyword "
                         "over the Romanian alphabet")

    U.heading(doc, "1. Purpose of the Work")
    U.para(doc, "The purpose of this laboratory work was to implement the "
                "Caesar cipher and its keyword version for the Romanian "
                "alphabet. In Task 1.1 I had to implement the Caesar cipher, "
                "using the 31-letter encoding from Table 2 of the handout. The "
                "program had to encrypt and decrypt a text typed by the user, "
                "ask for the numeric key k (1-30), and reject invalid input "
                "with a clear message.")
    U.para(doc, "Task 1.2 asked for the same cipher with a keyword. Key 1 is "
                "still the numeric shift. Key 2 is a keyword of at least 7 "
                "Romanian letters. The program builds a permuted alphabet from "
                "the keyword and prints it, so the result can be checked by hand.")

    U.heading(doc, "2. Short theory")
    U.para(doc, "The Caesar cipher replaces every letter with the letter k "
                "positions to the right in the alphabet. After the last letter "
                "it continues from the first one. I used the codes from Table 2: "
                "A = 0, \u0102 = 1, ..., Z = 30. With n = 31, encryption and "
                "decryption are")
    U.code_block(doc, [
        "    c = (m + k) mod n        encryption,   m, c \u2208 {0, \u2026, n\u22121}",
        "    m = (c \u2212 k + n) mod n    decryption",
    ])
    U.para(doc, "For example, with k = 3 the text CIFRULCEZAR becomes "
                "FKITXOFH\u00c2BT. The English example from the handout gives a "
                "different result because it uses the 26-letter English alphabet.")
    U.para(doc, "The key space is small. The keys are 1 to 30, so there are "
                "only 30 useful keys; k = 0 would leave the text unchanged. A "
                "program can try all of them in a moment. The cipher also keeps "
                "the letter frequencies of the language, so it can be attacked "
                "without trying all keys.")
    U.para(doc, "In Task 1.2 the keyword is written at the beginning of the "
                "alphabet, with duplicate letters removed, and the rest of the "
                "Romanian alphabet follows in the normal order. The shift is then "
                "applied in this new alphabet. The theoretical number of key "
                "pairs is 31! \u00d7 30: 31! possible alphabet orders and 30 "
                "shifts. Different keys can give the same substitution, so the "
                "number of different substitutions is at most 31!. The keyword "
                "makes the key space much larger, but each plaintext letter "
                "still becomes the same ciphertext letter every time. The "
                "cipher is still monoalphabetic, so frequency analysis still "
                "works.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "I wrote the program in Go. The menu and the input checks are "
                "in main.go, the classic cipher is in task1_1.go, and the keyword "
                "version is in task1_2.go. The alphabet is stored in a string. "
                "The position in that string is the letter code, so the program "
                "does not use ASCII or Unicode code points for the shift. The "
                "core of Task 1.1 is:")
    U.code_block(doc, read(os.path.join(REPO, "Lab1", "task1_1.go")).splitlines())
    U.para(doc, "The function builds a map from each letter to its position, "
                "then adds the key modulo 31 for encryption, or subtracts it and "
                "adds 31 for decryption. The extra 31 keeps the result positive.")
    U.para(doc, "For Task 1.2 I build the permuted alphabet by adding the "
                "keyword letters first, skipping letters that are already in the "
                "result, and then adding the rest of the Romanian alphabet. The "
                "function is:")
    U.code_block(doc, [
        "func buildPermutedAlphabet(keyword []rune) []rune {",
        "    result := make([]rune, 0, len([]rune(romanianAlphabet)))",
        "    included := make(map[rune]bool)",
        "    for _, letter := range append(keyword, []rune(romanianAlphabet)...) {",
        "        if isRomanianLetter(letter) && !included[letter] {",
        "            result = append(result, letter)",
        "            included[letter] = true",
        "        }",
        "    }",
        "    return result",
        "}",
    ])
    U.para(doc, "The function walks through the keyword first and then the "
                "alphabet, and the included map makes sure no letter appears "
                "twice.")
    U.para(doc, "Most of the code is input validation. The key has to be an "
                "integer from 1 to 30. The keyword has to contain at least 7 "
                "Romanian letters. The message may contain only Romanian letters "
                "and spaces, and the program removes the spaces before "
                "encryption. The keyword and the message are converted to "
                "uppercase before use. If a value is wrong, the program prints "
                "what is allowed and asks again. I also accept the cedilla forms "
                "\u015e/\u0162 and change them to \u0218/\u021a, because those are "
                "easy to type by mistake on a Romanian keyboard.")
    U.code_block(doc, [
        "func readShift() int {",
        "    for {",
        "        value := readLine(\"Enter numeric key k (1-30): \")",
        "        shift, err := strconv.Atoi(strings.TrimSpace(value))",
        "        if err == nil && shift >= 1 && shift <= 30 {",
        "            return shift",
        "        }",
        "        fmt.Println(\"Invalid key. The numeric key must be an integer from 1 to 30.\")",
        "    }",
        "}",
    ])
    U.para(doc, "The loop asks again until the key is valid. The keyword "
                "reader works the same way, and it also checks the length and "
                "the allowed letters.")

    U.heading(doc, "4. Results")
    lab1 = read(os.path.join(CAP, "lab1.txt"))
    p = shot_excerpt("lab1_1.png", lab1, start="$ ./caesar",
                     end="Plaintext: CRIPTOGRAFIAESTEOSTIINTAFRUMOASA",
                     title="caesar \u2014 Task 1.1 (encrypt / decrypt, k = 7)")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Task 1.1: encryption with k = 7 "
                                        "and decryption with the same key.")
    p = shot_excerpt("lab1_2.png", lab1, start="verificarea validarilor",
                     end="Ciphertext: \u00ceWOUZ\u021aMWFLOFKXZK\u021aXZOOTZFLW\u0102\u0218\u021aFXF",
                     title="caesar \u2014 input validation")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Invalid input: keys 0 and 31 and "
                                        "the character '2' are rejected.")
    p = shot_excerpt("lab1_3.png", lab1, start="verificarea cuvantului-cheie",
                     end="Ciphertext: VH\u021aV", title="caesar \u2014 keyword validation")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Invalid keyword: a keyword shorter "
                                        "than 7 letters and a keyword containing '!' are rejected.")
    p = shot_excerpt("lab1_4.png", lab1, start="Sarcina 1.2: cifrul cu cuvant-cheie",
                     end="Plaintext: CRIPTOGRAFIAPEINTELESULTUTUROR",
                     title="caesar \u2014 Task 1.2 (keyword ROMANIA, k = 3)")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. Task 1.2: the permuted alphabet "
                                        "for ROMANIA and the encryption/decryption run.")
    U.heading(doc, "4.1. Observations", level=2)
    U.para(doc, "1. Task 1.1 with k = 7: the program encrypted "
                "\u201ccriptografia este o stiinta frumoasa\u201d and then "
                "decrypted the ciphertext with the same key. The decrypted "
                "text is the input in uppercase without spaces, so the round "
                "trip works (Fig. 1).", first_indent=0)
    U.para(doc, "2. The invalid keys 0 and 31 were rejected. The message "
                "containing the character '2' was also rejected, and the "
                "program asked for a new value each time. It printed the "
                "allowed range instead of crashing (Fig. 2).", first_indent=0)
    U.para(doc, "3. Task 1.2 with the keyword ROMANIA and k = 3: the permuted "
                "alphabet starts with R O M A N I, followed by the rest of the "
                "Romanian alphabet. The ciphertext was "
                "FAB\u0218VNJA\u0102\u00ceB\u0102\u0218HB\u00c2VHSH\u021aXSVXVXANA, and decryption "
                "returned the original text (Fig. 4).", first_indent=0)
    U.para(doc, "4. The keyword \u201cabece\u201d was rejected because it is "
                "shorter than 7 letters. The keyword \u201cchei!\u201d was "
                "rejected because of '!'. Both messages name the problem, and "
                "the program asks for the keyword again (Fig. 3).",
          first_indent=0)

    U.heading(doc, "5. Conclusions")
    U.para(doc, "With only 30 keys, the classic Caesar cipher is easy to "
                "brute-force, and the letter frequencies do not change. The "
                "keyword version hides the simple shift, but it is still a "
                "monoalphabetic substitution, so the frequency attack from "
                "Laboratory 2 still works. Most of the code went into input "
                "checks, especially the cedilla forms and the negative modulo in "
                "Go. The cipher functions themselves are short.")

    U.references(doc, [
        "Laboratory Work No. 1 \u2014 Caesar Cipher. UTM, FCIM \u2014 handout (resources/).",
        "Table 2. Letter encoding of the Romanian alphabet (n = 31) \u2014 handout.",
        "W. Stallings. Cryptography and Network Security: Principles and Practice. "
        "Classical encryption systems.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab1", "Report_Lab1_Caesar_Dinu_Plesu.docx")
    U.insert_toc(doc)
    U.save(doc, out)
    return out


# --------------------------------------------------------------------------
# Lab 2
# --------------------------------------------------------------------------
def build_lab2():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 2, "Cryptanalysis of monoalphabetic ciphers \u2014 "
                         "frequency analysis attack (variant V20)")

    U.heading(doc, "1. Purpose of the Work")
    U.para(doc, "The purpose of this laboratory work was to break a "
                "monoalphabetic cipher without the key. My variant was V20, a "
                "text written in English. I had to follow the frequency-analysis "
                "attack from the handout: count the letters, match the most "
                "frequent ciphertext letters to the most frequent English "
                "letters, then correct the result by looking at words and letter "
                "patterns. The report had to describe the whole process, not "
                "only give the final plaintext.")
    U.para(doc, "The handout also says that only the letters were encrypted; "
                "spaces and punctuation stayed in place. I used the word lengths "
                "from the original ciphertext when I read the partial result. "
                "The program itself strips everything except letters for the "
                "frequency table.")

    U.heading(doc, "2. Short theory")
    U.para(doc, "In a monoalphabetic substitution cipher each plaintext letter "
                "is always replaced by the same ciphertext letter, so the cipher "
                "is just a permutation of the alphabet. The key space is large "
                "(26! \u2248 4\u00d710\u00b2\u2076 for English), but the letter "
                "frequencies do not change. For English, the most common letters "
                "are E, T, A, O, I and N, and the handout gives the full "
                "frequency tables for English and Romanian.")
    U.para(doc, "I started by ranking the ciphertext letters by frequency and "
                "matching them to the English ranking. That gave a partially "
                "readable text. Then I read the text and corrected the mapping "
                "using short words, common endings and repeated patterns. The "
                "chi-square statistic shows how close the current mapping is to "
                "English:")
    U.code_block(doc, [
        "    \u03c7\u00b2 = \u03a3\u1d62 (O\u1d62 \u2212 E\u1d62)\u00b2 / E\u1d62   (sum over all letters i)",
        "    O\u1d62 = observed count of the i-th plain letter,",
        "    E\u1d62 = expected count from the language frequency profile.",
    ])
    U.para(doc, "A lower chi-square means a better match, but it is only a "
                "number. The final decision comes from reading the text and "
                "recognising words. The program prints \u03c7\u00b2 after every "
                "change so I could see whether a correction helped.")
    U.para(doc, "The attack does not need a computer. I could have done the "
                "counting on paper with the tables from the handout. I used the "
                "suggested online service for the frequency table and the final "
                "substitutions, and I wrote a small Go program to test the "
                "automatic mapping and keep the corrections consistent.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "I used the service suggested in the handout: "
                "https://crypto.interactive-maths.com/frequency-analysis-breaking-the-code.html. "
                "I pasted V20 into the Intercept box and clicked Find "
                "Frequencies. The site produced the table in Fig. 2. After the "
                "manual analysis I entered the final substitution for each "
                "ciphertext letter in the site's row and clicked Make "
                "Substitutions. The service returned the plaintext shown in "
                "Fig. 4.")
    U.para(doc, "I also wrote a small Go program, freq.go, to test the "
                "automatic mapping and keep the 13 corrections consistent. "
                "Option 2 asks for the language profile, reads the ciphertext, "
                "counts the letters, prints the frequency table and applies the "
                "automatic mapping. After that it enters a loop with these "
                "commands: <CIFRATA>=<CLARA> assigns a correspondence, del "
                "removes one, tab prints the table again, text prints the "
                "current decryption, and gata ends the loop.")
    U.para(doc, "The program keeps the mapping bijective. If I assign a "
                "plaintext letter that is already used for another ciphertext "
                "letter, the old assignment is removed. The important part is:")
    U.code_block(doc, [
        "// Automatic mapping: rank cipher letters by frequency and match them",
        "// to the most frequent letters of the language profile.",
        "for idx, l := range observed {",
        "    assign[l] = profile.letters[idx]",
        "}",
        "",
        "// Interactive refinement (bijective): assigning a plain letter frees it",
        "// from any previous cipher letter, keeping the substitution a permutation.",
        "for oc, om := range assign {",
        "    if om == m && oc != c { delete(assign, oc) }",
        "}",
        "assign[c] = m",
    ])
    U.para(doc, "The first loop is the mechanical step: it sorts the cipher "
                "letters by frequency and assigns the most frequent English "
                "letters. The second loop runs when I type a correction and "
                "removes any old assignment of the plaintext letter. Everything "
                "else in the attack is reading the text and deciding the next "
                "correspondence.")
    U.para(doc, "The V20 text is English, so I used the English profile. The "
                "automatic mapping gave a rough text, and 13 manual corrections "
                "were enough to finish it.")

    U.heading(doc, "4. Results")
    lab2 = read(os.path.join(CAP, "lab2.txt"))
    attack = read(os.path.join(REPO, "Lab2", "lab2_attack_full.txt"))
    p = shot_excerpt("lab2_1.png", lab2, start="$ ./lab2",
                     end="\u00ceBOUSOADUNOMASYBXQA\u00cePSO", title="lab2 \u2014 Caesar demo")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. A short Caesar example with k = 11. "
                                        "I used it to check the frequency table before V20.")
    p = os.path.join(REPO, "Lab2", "figures", "lab2_online_freq.jpg")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Frequency table from the suggested "
                                        "Crypto Corner service after pasting V20. "
                                        "The letters are ranked by frequency, with "
                                        "their counts and percentages.")
    p = shot_excerpt("lab2_3.png", attack, start="> G=N", end="> I=R",
                     max_lines=26, title="lab2 \u2014 interactive refinement")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. One manual correction, G=N, and the "
                                        "partial text that follows it. I used the "
                                        "local program for this step.")
    p = os.path.join(REPO, "Lab2", "figures", "lab2_online_text.jpg")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. The suggested service after the final "
                                        "substitutions. The site returns the recovered "
                                        "plaintext; the complete text has 618 words and "
                                        "is saved in Lab2/v20_plain.txt.")
    U.heading(doc, "4.1. Observations", level=2)
    U.para(doc, "1. The small Caesar example with k = 11 worked and produced "
                "the expected ciphertext. I used it to check that the frequency "
                "table and the program were working before I started on V20 "
                "(Fig. 1).", first_indent=0)
    U.para(doc, "2. I pasted V20 into the suggested service. The site counted "
                "2,979 letters; V, W and T were the most frequent, with 363, "
                "310 and 300 occurrences (12.2%, 10.4%, 10.1%). The English "
                "ranking starts with E, T and A, so the mechanical mapping was "
                "V\u2192E, W\u2192T, T\u2192A (Fig. 2). The local tool gave "
                "chi-square 47.8 for that automatic mapping.", first_indent=0)
    U.para(doc, "3. I made 13 corrections on top of the automatic mapping: "
                "G=N, N=O, I=R, P=S, Q=H, C=F, D=U, J=G, Z=M, A=B, R=W, B=Q, "
                "Y=X. After the last one the text was clear. The final "
                "cipher-to-plain mapping is:", first_indent=0)
    U.code_block(doc, [
        "Cipher: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z",
        "Plain:  B Q F U J Y N C R G V K Z O D S H W L A P E T I X M",
    ])
    U.para(doc, "4. I entered this mapping in the service and clicked Make "
                "Substitutions. The site returned the 2,979-letter plaintext "
                "(Fig. 4), and it matches Lab2/v20_plain.txt. The recovered "
                "message is an excerpt from J. Kahn's \u201cThe Codebreakers\u201d "
                "about the Black Chamber, Yardley and the Washington Naval "
                "Conference. It has 618 words and is reused as the signed "
                "message in Laboratory 6.", first_indent=0)
    U.para(doc, "The 13 corrections are the part I did by reading. The local "
                "program counted the letters and kept the mapping consistent; "
                "the online service produced the final plaintext in Fig. 4.",
          first_indent=0)

    U.heading(doc, "5. Conclusions")
    U.para(doc, "The attack worked. The 2,979 letters were enough for the "
                "automatic mapping to get close, and 13 manual corrections "
                "finished the text. The key space of 26! did not matter because "
                "the frequencies and the word patterns gave the answer. I used "
                "the suggested online service for the frequency table and the "
                "final substitutions; it returned the same plaintext as the "
                "local check. The local program counted the letters and kept the "
                "mapping bijective, but the corrections came from reading the "
                "text.")

    U.references(doc, [
        "Lucrare de laborator nr. 2 \u2014 Criptanaliza cifrurilor monoalfabetice. "
        "UTM, FCIM \u2014 handout (resources/).",
        "Tables 2.1\u20132.4 \u2014 reference letter frequencies for Romanian and English.",
        "Crypto Corner \u2014 Frequency Analysis: Breaking the Code. "
        "https://crypto.interactive-maths.com/frequency-analysis-breaking-the-code.html",
        "J. Kahn. The Codebreakers \u2014 the story of secret writing (source of the V20 text).",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab2", "Report_Lab2_Criptanaliza_Dinu_Plesu.docx")
    U.insert_toc(doc)
    U.save(doc, out)
    return out


# --------------------------------------------------------------------------
# Lab 3
# --------------------------------------------------------------------------
def build_lab3():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 3, "Polyalphabetic ciphers \u2014 the Vigen\u00e8re cipher over "
                         "the Romanian alphabet (task 3.2)")

    U.heading(doc, "1. Purpose of the Work")
    U.para(doc, "The purpose of this laboratory work was to implement the "
                "Vigen\u00e8re cipher over the Romanian alphabet for task 3.2. My "
                "number in the group register is 20, which is even, so task 3.2 "
                "is the one assigned to me. The alphabet has 31 letters and the "
                "codes from Table 2 (0 to 30). The key is a word of at least 7 "
                "Romanian letters. The program has to encrypt and decrypt a "
                "text, show the key codes k\u1d62, and apply the formulas "
                "c\u1d62 = (m\u1d62 + k\u1d62) mod 31 and "
                "m\u1d62 = (c\u1d62 \u2212 k\u1d62) mod 31. Invalid keys and "
                "invalid characters have to be reported clearly.")
    U.para(doc, "I also implemented task 3.1, Playfair, as a bonus. The assigned "
                "task is still 3.2.")

    U.heading(doc, "2. Short theory")
    U.para(doc, "The Vigen\u00e8re cipher is a Caesar cipher with a different "
                "shift for every position. The keyword is repeated over the "
                "text, and each keyword letter gives one shift. If the keyword "
                "is K = k\u2081k\u2082\u2026k\u2113, the i-th plaintext letter "
                "m\u1d62 is encrypted with the shift k\u1d62:")
    U.code_block(doc, [
        "    c\u1d62 = (m\u1d62 + k\u1d62) mod n       with k\u1d62 = code(K[i mod \u2113])",
        "    m\u1d62 = (c\u1d62 \u2212 k\u1d62 + n) mod n",
    ])
    U.para(doc, "For Romanian n = 31. Because the shift changes, the same "
                "plaintext letter does not always become the same ciphertext "
                "letter. The letter frequencies are flatter than in a "
                "monoalphabetic cipher, so the simple frequency attack from "
                "Laboratory 2 does not work directly. The cipher is still "
                "breakable: the key length \u2113 can be found with the Kasiski "
                "examination or the index of coincidence, and then the text "
                "splits into \u2113 Caesar ciphers, one for each key position.")
    U.para(doc, "The keyword must have at least 7 letters. The key codes are the "
                "positions of the keyword letters in Table 2, so the program can "
                "print them and the shift at every position can be checked by "
                "hand.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "I wrote the program in Go. common.go contains the alphabet and "
                "the validation helpers, task_vigenere.go contains the "
                "Vigen\u00e8re cipher, task_playfair.go contains the bonus, and "
                "main.go contains the menu. The alphabet is stored in a string, "
                "and letterCode returns the position of a letter in that string. "
                "validateRomanianText converts the text to uppercase, removes "
                "spaces, accepts the cedilla forms and rejects any other "
                "character. The Vigen\u00e8re loop is:")
    U.code_block(doc, [
        "// key codes: each keyword letter -> its code in Table 2 (n = 31)",
        "codes, ok, msg = vigenereKeyCodes(kw)",
        "",
        "// encryption: ci = (mi + ki) mod 31 ; decryption: mi = (ci - ki) mod 31",
        "for i, letter := range text {",
        "    k := codes[i%len(codes)]",
        "    if operation == opEncrypt {",
        "        out[i] = alphabet[(letterCodes[letter]+k)%31]",
        "    } else {",
        "        out[i] = alphabet[(letterCodes[letter]-k+31)%31]",
        "    }",
        "}",
    ])
    U.para(doc, "The loop takes the key code with i % len(codes), so the "
                "keyword repeats until the end of the text. Encryption adds the "
                "key and decryption subtracts it; the extra 31 keeps the result "
                "positive. The program prints the normalized text, the keyword, "
                "the key codes, the formula and the result, so I could check the "
                "shift at every position by hand.")
    U.para(doc, "For the bonus task 3.1 I used a 6\u00d76 matrix because 31 "
                "letters do not fit a 5\u00d75 grid. The 31 letters are followed by "
                "the digits 0\u20134, which fill the last five cells. I did not fold "
                "J into I because the Romanian alphabet has its own J. The text "
                "is split into digraphs, X is inserted between two equal letters "
                "and at the end if the length is odd, and the rectangle, same-row "
                "and same-column rules are applied. The decryption path accepts "
                "the digits 0\u20134 because they can appear in a ciphertext, but "
                "plaintext validation still accepts only Romanian letters.")
    U.para(doc, "The Playfair code is the largest part of the program. The "
                "matrix is stored in a 6\u00d76 array, and a map from each "
                "character to its row and column makes the three rules short.")

    U.heading(doc, "4. Results")
    lab3 = read(os.path.join(CAP, "lab3.txt"))
    p = shot_excerpt("lab3_1.png", lab3, start="=== Sarcina 3.2",
                     end="Criptograma: \u021aEUPGWGHO\u0218INNSJT\u0102SGRIDHMFDCMEODAERICC\u0102RGINJO",
                     title="lab3 \u2014 Vigen\u00e8re encryption (k\u2082 = ROMANIA)")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Vigen\u00e8re encryption with the "
                                        "keyword ROMANIA. The key codes are "
                                        "[20 17 15 0 16 10 0].")
    p = shot_excerpt("lab3_2.png", lab3, start="Introduceti criptograma",
                     end="Mesajul decriptat: CRIPTOGRAFIAESTEOSTIINTAFRUMOASASIIMPORTANTA",
                     title="lab3 \u2014 Vigen\u00e8re decryption (round trip)")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Decryption of the same ciphertext "
                                        "with the same keyword. The result is the "
                                        "original message.")
    p = shot_excerpt("lab3_3.png", lab3, start="verificarea validarilor",
                     end="Caracter invalid: '1'.", title="lab3 \u2014 keyword validation")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Invalid keywords: one shorter than "
                                        "7 letters and one containing the digit '1'.")
    p = shot_excerpt("lab3_4.png", lab3, start="=== Sarcina 3.1",
                     end="CRIPTOGRAFIAESTEOSTIINTAFRUMOASASIIMPORTANTA",
                     title="lab3 \u2014 Playfair (task 3.1, 6\u00d76 matrix) round trip")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. Playfair bonus: the 6\u00d76 matrix "
                                        "and the encryption/decryption round trip.")
    U.heading(doc, "4.1. Observations", level=2)
    U.para(doc, "1. Vigen\u00e8re with the keyword ROMANIA and k\u2082 = 3: the "
                "program printed the key codes [20 17 15 0 16 10 0] and the "
                "ciphertext for \u201ccriptografia este o stiinta frumoasa si "
                "important\u0103\u201d. Decryption with the same keyword returned "
                "the original text (Fig. 1 and Fig. 2).", first_indent=0)
    U.para(doc, "2. The keyword checks work. A keyword shorter than 7 letters "
                "is rejected, and a keyword containing the digit '1' is also "
                "rejected. The program prints the reason and asks again "
                "(Fig. 3).", first_indent=0)
    U.para(doc, "3. The Playfair bonus also works. The 6\u00d76 matrix starts "
                "with the keyword and is filled with the rest of the alphabet "
                "and the digits 0\u20134. The round trip returned the original "
                "letters (Fig. 4). The digits are the part I had to be careful "
                "about, because they can appear in a ciphertext but not in the "
                "plaintext.", first_indent=0)

    U.heading(doc, "5. Conclusions")
    U.para(doc, "Both tasks work. Vigen\u00e8re hides the letter frequencies "
                "much better than Caesar, but the key length can be found and "
                "the text then splits into Caesar ciphers. I did not implement "
                "the Kasiski attack, but I understood why it works. Playfair was "
                "the harder bonus: the 6\u00d76 matrix, the filler X and the "
                "digits 0\u20134 needed more care than Vigen\u00e8re. The input "
                "checks were the same kind as in Laboratory 1.")

    U.references(doc, [
        "Lucrare de laborator nr. 3 \u2014 Cifruri polialfabetice. UTM, FCIM \u2014 handout "
        "(resources/).",
        "Table 2 \u2014 letter encoding of the Romanian alphabet (n = 31).",
        "W. Stallings. Cryptography and Network Security \u2014 Vigen\u00e8re cipher and "
        "cryptanalysis.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab3", "Report_Lab3_Vigenere_Dinu_Plesu.docx")
    U.insert_toc(doc)
    U.save(doc, out)
    return out


# --------------------------------------------------------------------------
# Lab 4  (DES, task 2.9)
# --------------------------------------------------------------------------
def build_lab4():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 4, "Block ciphers \u2014 the DES algorithm "
                         "(task 2.9: determining S\u2c7c(B\u2c7c))")

    U.heading(doc, "1. Purpose of the Work")
    U.para(doc, "The purpose of this laboratory work was to solve task 2.9 of "
                "DES. My student number is 20, so the task number is "
                "nr_sarcina = 20 mod 11 = 9. In round i of DES the 48-bit value "
                "K\u1d62 \u2295 E(R\u1d62\u208b\u2081) is known, and for a chosen "
                "box j (1\u20138) I have to determine the 4-bit output "
                "S\u2c7c(B\u2c7c), showing all intermediate steps.")
    U.para(doc, "I also implemented the whole DES algorithm, not only the "
                "S-box lookup. That way the 48-bit value comes from a real "
                "round, and I could check the implementation with the classic "
                "DES test vector.")

    U.heading(doc, "2. Short theory")
    U.para(doc, "DES encrypts 64-bit blocks with a 64-bit key, but 8 bits are "
                "parity bits, so the effective key is 56 bits. The block goes "
                "through the initial permutation IP, 16 Feistel rounds and the "
                "final permutation. In round i:")
    U.code_block(doc, [
        "    L\u1d62 = R\u1d62\u208b\u2081 ,   R\u1d62 = L\u1d62\u208b\u2081 \u2295 f(R\u1d62\u208b\u2081, K\u1d62)",
        "    f(R, K) = P( S\u2081(B\u2081) \u2026 S\u2088(B\u2088) ),  where B\u2081\u2026B\u2088 are the",
        "    eight 6-bit blocks of  K \u2295 E(R)  (E expands R from 32 to 48 bits).",
    ])
    U.para(doc, "The function f first expands R from 32 to 48 bits with E, then "
                "XORs the result with the round key K\u1d62. The 48 bits are split "
                "into eight blocks of six bits. Each block goes into one S-box, "
                "which returns four bits. The eight outputs form 32 bits, and P "
                "permutes them. The S-boxes are the only non-linear part of "
                "DES; without them the cipher would be linear.")
    U.para(doc, "For one S-box, the outer bits b\u2081b\u2086 give the row and the "
                "middle bits b\u2082b\u2083b\u2084b\u2085 give the column. The entry at "
                "that row and column is the 4-bit output. The key schedule takes "
                "the 64-bit key, removes the parity bits with PC-1, splits the "
                "56 bits into C\u2080 and D\u2080, shifts each half left by one or two "
                "positions per round, and applies PC-2 to get each 48-bit "
                "subkey K\u2081\u2026K\u2081\u2086.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "I wrote the program in Python, in des_lab.py. The menu has "
                "options for task 2.9, the S-box tables, the key schedule, full "
                "encryption, the self-test and exit. The task 2.9 part is:")
    U.code_block(doc, [
        "bits = bits_of(value48, 48)          # cei 48 de biti sub forma de \u20180\u2019/\u20181\u2019",
        "blocks = grouped(bits, 6)            # B1..B8, cate 6 biti",
        "bj = blocks[j - 1]                   # blocul cutiei cerute",
        "row = int(bj[0] + bj[5], 2)          # b1 b6  -> linia",
        "col = int(bj[1:5], 2)                # b2 b3 b4 b5 -> coloana",
        "value = SBOX[j - 1][row][col]        # iesirea pe 4 biti a cutiei-S",
    ])
    U.para(doc, "The code splits the 48-bit value into eight blocks of six "
                "bits, takes B\u2c7c, reads the row from the first and last bit, "
                "the column from the middle four bits, and looks up the value in "
                "SBOX. The function prints the eight blocks, the chosen B\u2c7c, "
                "the row and column, the S-box table with the selected cell "
                "marked, the 4-bit result, and, for context, all eight S-box "
                "outputs followed by P.")
    U.para(doc, "The full DES part is in the same file. It implements the key "
                "schedule, the 16 rounds and the final permutation, so I could "
                "use a real K\u1d62 \u2295 E(R\u1d62\u208b\u2081) in task 2.9. "
                "The program accepts binary or hexadecimal input, and it can "
                "generate the values randomly. The --seed option fixes the "
                "random generator so a run can be repeated exactly for the "
                "report.")

    U.heading(doc, "4. Results")
    lab4 = read(os.path.join(CAP, "lab4.txt"))
    p = shot_excerpt("lab4_1.png", lab4, start="meniul 5: test",
                     end="REZULTAT: CORECT", title="des_lab \u2014 DES self-test")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. DES self-test: key "
                                        "133457799BBCDFF1, plaintext "
                                        "0123456789ABCDEF, ciphertext "
                                        "85E813540F0AB405.")
    p = shot_excerpt("lab4_2.png", lab4, start="Dupa PC-1 (56 biti)",
                     end="K16 (PC-2, 48 biti)", max_lines=44,
                     title="des_lab \u2014 key schedule (PC-1, shifts, PC-2)")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Key schedule: PC-1, the C\u2080/D\u2080 "
                                        "halves, the 16 shifts and the subkeys "
                                        "K\u2081\u2026K\u2081\u2086.")
    full = read(os.path.join(REPO, "Lab4", "lab4_encrypt_full.txt"))
    lines = full.splitlines()

    def line_index(text, start=0):
        return next(i for i in range(start, len(lines)) if text in lines[i])

    i0 = line_index("Textul clar (64 biti)")
    i1 = line_index("Runda  2:", i0)
    i16 = line_index("Runda 16:", i0)
    iend = line_index("Blocul criptat (hex)", i16)
    excerpt = (lines[i0:i1] + ["", "  ... (rounds 2-15 omitted) ...", ""]
               + lines[i16:iend + 1])
    p = shot("lab4_3.png", excerpt,
             title="des_lab \u2014 full encryption (round 1, round 16, final)")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Full encryption excerpt: round 1, "
                                        "round 16 and the final permutation. The final "
                                        "ciphertext is 85E813540F0AB405. The complete "
                                        "transcript is in lab4_encrypt_full.txt.")
    p = shot_excerpt("lab4_4.png", lab4, start="meniul 1: sarcina 2.9",
                     end="dupa permutarea P", max_lines=44,
                     title="des_lab \u2014 task 2.9 (i = 5, j = 3)")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. Task 2.9: given "
                                        "K\u2085 \u2295 E(R\u2084) = 0xC60503EB51A2, "
                                        "B\u2083 = 010100 gives r = 0, c = 10, so "
                                        "S\u2083(B\u2083) = S\u2083[0][10] = 12 = 1100\u2082.")
    U.heading(doc, "4.1. Observations", level=2)
    U.para(doc, "1. The self-test produced the expected ciphertext "
                "85E813540F0AB405 from the key 133457799BBCDFF1 and the "
                "plaintext 0123456789ABCDEF. This checks the key schedule, the "
                "16 rounds and the final permutation together (Fig. 1).",
          first_indent=0)
    U.para(doc, "2. The key schedule printed C\u2080, D\u2080, the left shifts "
                "and all 16 subkeys. I compared K\u2081 = 1B02EFFC7072 with the "
                "value in the DES example, and it matches (Fig. 2).",
          first_indent=0)
    U.para(doc, "3. The full encryption trace shows round 1, round 16 and the "
                "final permutation. The final ciphertext is the same "
                "85E813540F0AB405 as in the self-test. I left out rounds 2\u201315 "
                "so the figure fits; the complete transcript is in "
                "lab4_encrypt_full.txt (Fig. 3).", first_indent=0)
    U.para(doc, "4. For task 2.9 I used i = 5 and j = 3. The program received "
                "K\u2085 \u2295 E(R\u2084) = 0xC60503EB51A2 and split it into "
                "eight 6-bit blocks. B\u2083 = 010100, so b\u2081b\u2086 = 00 "
                "(row 0) and b\u2082b\u2083b\u2084b\u2085 = 1010 (column 10). "
                "The entry S\u2083[0][10] is 12, or 1100 in binary (Fig. 4).",
          first_indent=0)

    U.heading(doc, "5. Conclusions")
    U.para(doc, "Task 2.9 is a small step once the 6-bit split is clear. The "
                "hard part was the full DES: the tables, the key schedule and "
                "the order of the rounds. One wrong table changes the final "
                "ciphertext, so the test vector was the best check. The S-boxes "
                "are the only non-linear part; without them the cipher would be "
                "linear. DES is obsolete because 56 bits is too short for a "
                "brute-force search, but it is a clear Feistel example.")

    U.references(doc, [
        "Lucrare de laborator nr. 4 \u2014 Cifruri bloc. Algoritmul DES. UTM, FCIM \u2014 "
        "handout (resources/).",
        "FIPS PUB 46-3 \u2014 Data Encryption Standard (DES); NBS Special "
        "Publication 500-20 \u2014 DES validation test set.",
        "W. Stallings. Cryptography and Network Security \u2014 chapter on DES.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab4", "Report_Lab4_DES_Dinu_Plesu.docx")
    U.insert_toc(doc)
    U.save(doc, out)
    return out


# --------------------------------------------------------------------------
# Lab 5  (RSA, ElGamal, Diffie-Hellman + AES)
# --------------------------------------------------------------------------
def build_lab5():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 5, "Public-key cryptography \u2014 RSA, ElGamal and "
                         "Diffie-Hellman with an AES-256 session key")

    U.heading(doc, "1. Purpose of the Work")
    U.para(doc, "The purpose of this laboratory work was to implement RSA, "
                "ElGamal and a Diffie-Hellman exchange with an AES-256 session "
                "key. My student number is 20. For task 2.1 I had to generate "
                "RSA keys with n of at least 2048 bits, encrypt the message and "
                "decrypt it. For task 2.2 I had to use the 2048-bit safe prime p "
                "and g = 2 from the handout, build an ElGamal key pair and "
                "encrypt/decrypt the same message. For task 3 I had to do a "
                "Diffie-Hellman exchange between Alice and Bob over the same p "
                "and g, derive a 256-bit AES key from the shared secret, and "
                "encrypt the message block.")
    U.para(doc, "The message is my name, \u201cDinu Plesu\u201d. The handout "
                "asks for the decimal representation of the ASCII/hex form, so "
                "the scripts convert the name to a hexadecimal string and then "
                "to an integer.")

    U.heading(doc, "2. Short theory")
    U.para(doc, "RSA is based on the difficulty of factoring n = p\u00b7q. I "
                "chose two 1024-bit primes p and q, computed n and "
                "\u03d5(n) = (p\u22121)(q\u22121), used e = 65537, and computed "
                "d = e\u207b\u00b9 mod \u03d5(n). Encryption and decryption are")
    U.code_block(doc, [
        "    c = m^e mod n        encryption (public key (e, n))",
        "    m = c^d mod n        decryption (private key (d, n))",
        "    because c^d = (m^e)^d = m^(e*d) = m^1 (mod n) = m,",
        "    since e*d = 1 (mod phi(n)) and m^phi(n) = 1 (mod n)",
        "    for gcd(m, n) = 1 (the message here is much smaller than n).",
    ])
    U.para(doc, "This is raw textbook RSA without OAEP padding. It is the form "
                "used in the exercise; real systems add OAEP for encryption and "
                "PSS for signatures.")
    U.para(doc, "ElGamal uses the safe prime p = 2q + 1 and the generator g = 2. "
                "The secret key is x, the public key is y = g^x mod p, and a "
                "message m is encrypted with a fresh random k as "
                "(c\u2081, c\u2082) = (g^k mod p, m\u00b7y^k mod p). Decryption "
                "is m = c\u2082\u00b7(c\u2081^x)\u207b\u00b9 mod p.")
    U.para(doc, "Diffie-Hellman uses the same p and g. Alice sends A = g^a mod p, "
                "Bob sends B = g^b mod p, and both compute the same "
                "K = B^a = A^b = g^(a\u00b7b) mod p. I hashed K with SHA-256 to "
                "get the 256-bit AES key, then encrypted the padded message "
                "block with AES-256 in ECB mode.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "The handout suggests Wolfram Alpha or Wolfram Mathematica. The "
                "free web interface is not practical for 1024-bit primes and "
                "2048-bit moduli, so I wrote the calculations in Python "
                "(main.py). The operations are the same: Python's "
                "pow(base, exp, mod) is Wolfram's PowerMod, and "
                "pow(e, -1, \u03d5) is ModInverse. The AES part is in "
                "verify_dh_aes.py. The main steps are:")
    U.code_block(doc, [
        "e = 65537",
        "while True:",
        "    p = gen_prime(1024); q = gen_prime(1024); n = p*q",
        "    phi = (p-1)*(q-1)",
        "    if n.bit_length() >= 2048 and gcd(e, phi) == 1: break",
        "d = pow(e, -1, phi)                                      # ModInverse",
        "c = pow(m, e, n);   m2 = pow(c, d, n)                    # encrypt/decrypt",
        "",
        "# Diffie-Hellman + AES-256",
        "A = pow(G, a, P);   B = pow(G, b, P);   K = pow(B, a, P)",
        "key = hashlib.sha256(K.to_bytes(256, 'big')).digest()    # AES-256 key",
    ])
    U.para(doc, "The loop generates p and q until n has at least 2048 bits and "
                "e is invertible modulo \u03d5(n). Then d is the modular "
                "inverse. The ElGamal part uses the given p and g = 2, a random "
                "x and a random k. The Diffie-Hellman part uses the same p and "
                "g, and the shared secret is converted to 256 bytes before "
                "SHA-256, so the key length is exactly 256 bits.")
    U.para(doc, "The message is converted to an integer as the handout asks: "
                "ASCII to a hexadecimal string, then to decimal. The scripts "
                "print the values and check the round trips. "
                "verify_dh_aes.py also runs a FIPS-197 AES known-answer test "
                "before it encrypts the message block.")
    U.para(doc, "The same steps in Wolfram Language would be:")
    U.code_block(doc, [
        "m = FromDigits[ToCharacterCode[\"Dinu Plesu\"], 256];",
        "d = ModInverse[e, phi]; c = PowerMod[m, e, n];",
        "PowerMod[c, d, n] == m",
        "y = PowerMod[2, x, p]; c1 = PowerMod[2, k, p];",
        "c2 = Mod[m*PowerMod[y, k, p], p];",
        "Mod[c2*PowerMod[PowerMod[c1, x, p], p-2, p], p] == m",
        "A = PowerMod[2, a, p]; B = PowerMod[2, b, p];",
        "PowerMod[B, a, p] == PowerMod[A, b, p]",
    ])

    U.heading(doc, "4. Results")
    lab5 = read(os.path.join(CAP, "lab5.txt"))
    p = shot_excerpt("lab5_1.png", lab5, start="== Sarcina 2.1 RSA",
                     end="Verificare: (e*d) mod phi = 1", max_lines=12,
                     title="main.py \u2014 RSA (2048-bit modulus)")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. RSA: p and q are 1024-bit primes, "
                                        "n has 2048 bits, the round trip returns the "
                                        "message, and e\u00b7d \u2261 1 (mod \u03d5).")
    p = shot_excerpt("lab5_2.png", lab5, start="== Sarcina 2.2 ElGamal",
                     end="-> OK", max_lines=14, title="main.py \u2014 ElGamal (p 2048-bit)")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. ElGamal with the given safe prime p "
                                        "and g = 2: the keys, the ciphertext "
                                        "(c\u2081, c\u2082) and the decrypted message.")
    p = shot_excerpt("lab5_3.png", lab5, start="== Sarcina 3 Diffie-Hellman",
                     end="Cheie AES-256 = SHA-256(K)", max_lines=12,
                     title="main.py \u2014 Diffie-Hellman + AES-256 KDF")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Diffie-Hellman: Alice and Bob get "
                                        "the same K, and SHA-256(K) gives the AES-256 key.")
    p = shot_excerpt("lab5_4.png", lab5, start="KAT AES-256",
                     end="ciphertext:", title="verify_dh_aes.py \u2014 AES-256 encryption")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. verify_dh_aes.py: the FIPS-197 AES "
                                        "known-answer test passes, then the block "
                                        "\u201cDinu Plesu\u201d is encrypted with the "
                                        "derived AES-256 key.")
    U.heading(doc, "4.1. Observations", level=2)
    U.para(doc, "1. RSA: p and q are 1024-bit primes, so n has 2048 bits. The "
                "encryption and decryption returned the original message, and "
                "the last line shows e\u00b7d \u2261 1 (mod \u03d5). Some values "
                "are shortened in the screenshot; the full values are in "
                "rsa_params.txt (Fig. 1).", first_indent=0)
    U.para(doc, "2. ElGamal used the given p, g = 2 and a random k. The "
                "script printed x, y, c\u2081, c\u2082 and the decrypted "
                "message. Decryption returned the same m; the full values are "
                "in elgamal_params.txt (Fig. 2).", first_indent=0)
    U.para(doc, "3. Diffie-Hellman: Alice and Bob computed the same K. "
                "SHA-256(K) gave the 256-bit AES key. The full values are in "
                "dh_params.txt (Fig. 3).", first_indent=0)
    U.para(doc, "4. The AES part starts with the FIPS-197 known-answer test, "
                "which passed, then encrypts the padded block \u201cDinu "
                "Plesu\u201d with the derived key (Fig. 4).", first_indent=0)

    U.heading(doc, "5. Conclusions")
    U.para(doc, "All three tasks worked. RSA needed the 2048-bit check and the "
                "gcd check; ElGamal needed a fresh random k for each message; "
                "Diffie-Hellman gave both sides the same K, and SHA-256 turned "
                "it into the AES key. The most interesting part was combining "
                "the public-key exchange with AES. Raw RSA is only for the "
                "exercise; real systems need OAEP padding and PSS signatures.")

    U.references(doc, [
        "Lucrare de laborator nr. 5 \u2014 Criptografia cu chei publice. UTM, FCIM \u2014 "
        "handout (resources/).",
        "R. Rivest, A. Shamir, L. Adleman \u2014 RSA (1978); W. Diffie, M. Hellman "
        "\u2014 New Directions in Cryptography (1976).",
        "FIPS PUB 197 \u2014 Advanced Encryption Standard (AES).",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab5", "Report_Lab5_CheiePublica_Dinu_Plesu.docx")
    U.insert_toc(doc)
    U.save(doc, out)
    return out


# --------------------------------------------------------------------------
# Lab 6  (hash functions + RSA/NTLM and ElGamal/Whirlpool signatures)
# --------------------------------------------------------------------------
def build_lab6():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 6, "Hash functions and digital signatures \u2014 "
                         "RSA/NTLM and ElGamal/Whirlpool")

    U.heading(doc, "1. Purpose of the Work")
    U.para(doc, "The purpose of this laboratory work was to generate and "
                "verify two digital signatures. My number in the group is 20, "
                "so the hash index is i = (20 mod 24) + 1 = 21. In the first "
                "list (RSA signatures) index 21 is NTLM. In the second list "
                "(ElGamal signatures) index 21 is Whirlpool. The message m is "
                "the plaintext I recovered in Laboratory 2 from variant V20.")
    U.para(doc, "I had to generate an RSA signature of H = NTLM(m), an ElGamal "
                "signature of H = Whirlpool(m), and validate both signatures. I "
                "also had to check the two hash functions against published test "
                "vectors.")

    U.heading(doc, "2. Short theory")
    U.para(doc, "A hash function takes a message of any length and returns a "
                "fixed-size digest. It should be hard to find a message with a "
                "given digest, hard to find a second message with the same "
                "digest, and hard to find any two messages with the same digest. "
                "NTLM is MD4 over the UTF-16LE form of the text. MD4 processes "
                "the message in 64-byte blocks with three rounds and returns a "
                "128-bit digest. MD4 is broken; practical collisions exist, so "
                "NTLM is only used here because the list assigns it.")
    U.para(doc, "Whirlpool is a 512-bit hash from ISO/IEC 10118-3. It uses an "
                "AES-like block cipher and the Miyaguchi-Preneel construction, "
                "with a 512-bit block and a 512-bit digest.")
    U.para(doc, "A digital signature uses the signer's private key. For RSA, the "
                "signature of H is s = H^d mod n, and the public check is "
                "v = s^e mod n = H. For ElGamal, the signer picks a random k "
                "with gcd(k, p\u22121) = 1 and computes")
    U.code_block(doc, [
        "    s\u2081 = g^k mod p",
        "    s\u2082 = k\u207b\u00b9 \u00b7 (H \u2212 x\u00b7s\u2081) mod (p\u22121)",
        "    verification:  g^H  =  y^s\u2081 \u00b7 s\u2081^s\u2082  (mod p)",
        "    where y = g^x mod p is the public key.",
    ])
    U.para(doc, "The ElGamal verification checks the digest without recovering "
                "it. Both schemes need a hash function, because signing the "
                "whole message would be slow and the digest is enough to detect "
                "changes.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "The handout suggests Wolfram Alpha or Wolfram Mathematica. I "
                "used Python (main.py, md4.py and the external whirlpool "
                "package) because it is easier to rerun and check every value. "
                "The modular operations are the same as PowerMod and ModInverse. "
                "NTLM is MD4 over the UTF-16LE bytes of the message; I wrote the "
                "MD4 code and tested it with all seven RFC 1320 vectors. "
                "Whirlpool comes from the external package and I tested it with "
                "three ISO vectors. The RSA modulus has 3072 bits (two 1536-bit "
                "primes), and ElGamal uses the 2048-bit p from the handout. The "
                "core steps are:")
    U.code_block(doc, [
        "# RSA signature over NTLM",
        "h_hex, H = compute_hash(\"NTLM\", m)         # digest -> integer",
        "s = pow(H, d, n)                            # sign with private key",
        "v = pow(s, e, n);  assert v == H            # validate",
        "",
        "# ElGamal signature over Whirlpool",
        "h_hex, H = compute_hash(\"Whirlpool\", m)",
        "s1 = pow(G, kA, p)",
        "s2 = (pow(kA, -1, p-1) * (H - x*s1)) % (p-1)",
        "v1 = pow(G, H, p);  v2 = pow(y, s1, p) * pow(s1, s2, p) % p",
        "assert v1 == v2",
    ])
    U.para(doc, "The first block signs H = NTLM(m) with RSA and checks that "
                "v = H. The second computes s\u2081 and s\u2082 for "
                "H = Whirlpool(m) and checks g^H = "
                "y^s\u2081\u00b7s\u2081^s\u2082 mod p. The RSA signature is raw "
                "textbook RSA; real systems add PSS or PKCS#1 v1.5 padding. The "
                "extra check with H + 1 shows that changing the digest breaks "
                "the ElGamal verification.")
    U.para(doc, "The Whirlpool implementation was cross-checked against three "
                "ISO/IEC 10118-3 known-answer vectors, and the MD4 "
                "implementation against the seven RFC 1320 vectors. The test "
                "vectors were important because a signature is only as good as "
                "the hash underneath it.")

    U.heading(doc, "4. Results")
    hashtest = read(os.path.join(CAP, "lab6_hashtest.txt"))
    full = read(os.path.join(CAP, "lab6_full.txt"))
    p = shot_excerpt("lab6_1.png", hashtest, start="Verificarea Whirlpool",
                     end="Toate cele 3 vectori", title="main.py --hash-test \u2014 Whirlpool KAT")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Whirlpool checked against the three "
                                        "ISO/IEC 10118-3 vectors: empty string, "
                                        "\u201cabc\u201d and the quick-brown-fox sentence.")
    p = shot_excerpt("lab6_2.png", full, start="SARCINA 2 - SEMNATURA RSA",
                     end="SEMNATURA VALIDA", max_lines=30,
                     title="main.py \u2014 RSA signature, hash = NTLM")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. RSA signature of H = NTLM(m) with a "
                                        "3072-bit modulus. The check v = s^e mod n "
                                        "returns H.")
    p = shot_excerpt("lab6_3.png", full, start="SARCINA 3 - SEMNATURA ELGAMAL",
                     end="control anticoruptie", max_lines=32,
                     title="main.py \u2014 ElGamal signature, hash = Whirlpool")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. ElGamal signature of "
                                        "H = Whirlpool(m): g^H = "
                                        "y^s\u2081\u00b7s\u2081^s\u2082 (mod p), and "
                                        "the H + 1 check fails.")
    U.heading(doc, "4.1. Observations", level=2)
    U.para(doc, "1. Whirlpool produced the expected digests for the empty "
                "string, \u201cabc\u201d and the quick-brown-fox sentence. All "
                "three match the ISO vectors (Fig. 1).", first_indent=0)
    U.para(doc, "2. RSA: the script generated two 1536-bit primes, so n has "
                "3072 bits, then signed H = NTLM(m). The validation line shows "
                "v == H, so the signature is valid (Fig. 2).", first_indent=0)
    U.para(doc, "3. ElGamal: the script hashed the same message with Whirlpool, "
                "chose kA with gcd(kA, p\u22121) = 1, and computed s\u2081 and "
                "s\u2082. The check g^H = y^s\u2081\u00b7s\u2081^s\u2082 mod p "
                "passed. The H + 1 line failed, so a changed digest is rejected "
                "(Fig. 3).", first_indent=0)

    U.heading(doc, "5. Conclusions")
    U.para(doc, "Both signatures verified. RSA works because s^e = H, and "
                "ElGamal because g^H = y^s\u2081\u00b7s\u2081^s\u2082; changing "
                "H to H + 1 breaks the check. MD4 is broken, so NTLM is only "
                "here because the list assigns it. Whirlpool passed the ISO "
                "vectors. The message from Laboratory 2 connects the two labs: "
                "the text I recovered there is what I signed here.")

    U.references(doc, [
        "Lucrare de laborator nr. 6 \u2014 Func\u021bii hash \u0219i semn\u0103turi "
        "digitale. UTM, FCIM \u2014 handout (resources/).",
        "RFC 1320 \u2014 The MD4 Message-Digest Algorithm; NTLM (MD4-based).",
        "ISO/IEC 10118-3 \u2014 Whirlpool hash function; J. Daemen, M. Knudsen.",
        "R. Rivest \u2014 MD4/MD5; A. Menezes, P. van Oorschot, S. Vanstone \u2014 "
        "Handbook of Applied Cryptography.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab6", "Report_Lab6_Hash_Semnaturi_Dinu_Plesu.docx")
    U.insert_toc(doc)
    U.save(doc, out)
    return out


BUILDERS = {1: build_lab1, 2: build_lab2, 3: build_lab3,
            4: build_lab4, 5: build_lab5, 6: build_lab6}


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print("usage: build_reports.py [lab ...]     default: every lab")
        print("example: build_reports.py 3           rebuild Laboratory 3 only")
        raise SystemExit(0)
    bad = [a for a in args if not a.isdigit() or int(a) not in BUILDERS]
    if bad:
        raise SystemExit("unknown lab(s): %s — choose from %s"
                         % (" ".join(bad), " ".join(map(str, sorted(BUILDERS)))))
    chosen = sorted({int(a) for a in args}) if args else sorted(BUILDERS)
    for n in chosen:
        print("wrote", BUILDERS[n]())
