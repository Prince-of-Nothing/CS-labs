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
CAP = "/tmp/opencode/captures"
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

    U.heading(doc, "1. Task")
    U.para(doc, "Task 1.1. Implement the Caesar cipher for the Romanian "
                "alphabet (n = 31 letters, encoding of Table 2 of the handout) "
                "in a programming language of choice. The program must encrypt "
                "and decrypt a text given interactively, using the numeric key "
                "k (1\u201330), and must reject invalid input with a clear message.")
    U.para(doc, "Task 1.2. Implement the Caesar cipher with two keys over the "
                "same alphabet, keeping all conditions of Task 1.1. Key 1 is the "
                "numeric shift; Key 2 is a keyword of at least 7 Romanian letters "
                "(including \u0102, \u00c2, \u00ce, \u0218, \u021a) that is converted to "
                "uppercase and is used to build a permuted alphabet, which the "
                "program must display so the result can be checked by hand.")

    U.heading(doc, "2. Theoretical contents")
    U.para(doc, "The Caesar cipher is the simplest monoalphabetic substitution "
                "cipher: every letter is replaced by the letter situated k "
                "positions later in the alphabet, cyclically. Over an alphabet "
                "A of n letters each letter is identified with its code "
                "code(x) \u2208 {0, \u2026, n\u22121}; encryption and decryption are")
    U.code_block(doc, [
        "    c = (m + k) mod n        encryption,   m, c \u2208 {0, \u2026, n\u22121}",
        "    m = (c \u2212 k + n) mod n    decryption",
    ])
    U.para(doc, "For the Romanian alphabet n = 31 (Table 2 of the handout), so "
                "the key space contains only 30 possible keys; an attacker can "
                "recover the plaintext by trying all 30 shifts (brute force) or "
                "by comparing the letter frequencies of the ciphertext with the "
                "reference frequencies of the language.")
    U.para(doc, "In the two-key version (Task 1.2) the second key, a keyword, "
                "produces a key-dependent permutation of the alphabet: the "
                "keyword letters are written first (duplicates removed) and the "
                "remaining alphabet letters follow in their natural order. "
                "Encryption again uses a cyclic shift, but now in the permuted "
                "alphabet. The key space grows to 30 \u00d7 (number of admissible "
                "keywords), yet the cipher remains monoalphabetic and is still "
                "broken by frequency analysis.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "Both tasks were implemented in Go (files task1_1.go and "
                "task1_2.go). The alphabet and the letter-to-code map are built "
                "once; encryption and decryption differ only in the sign of the "
                "shift. The core of Task 1.1 is:")
    U.code_block(doc, read(os.path.join(REPO, "Lab1", "task1_1.go")).splitlines())
    U.para(doc, "For Task 1.2 the permuted alphabet is constructed by writing "
                "the keyword first and then every Romanian letter not yet used:")
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
    U.para(doc, "All inputs are validated interactively: the numeric key must "
                "be an integer from 1 to 30, the keyword at least 7 Romanian "
                "letters, and the message must contain only Romanian letters and "
                "spaces (which are removed). Every violation prints a message "
                "stating the allowed values and re-prompts the user.")

    U.heading(doc, "4. Results of the work")
    lab1 = read(os.path.join(CAP, "lab1.txt"))
    p = shot_excerpt("lab1_1.png", lab1, start="$ ./caesar",
                     end="Plaintext: CRIPTOGRAFIAESTEOSTIINTAFRUMOASA",
                     title="caesar \u2014 Task 1.1 (encrypt / decrypt, k = 7)")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Task 1.1 \u2014 encryption with k = 7 "
                                        "and the decryption round trip.")
    p = shot_excerpt("lab1_2.png", lab1, start="verificarea validarilor",
                     end="Ciphertext: \u00ceWOUZ\u02baMWFLOFKXZK\u02baXZOOTZFLW\u0102\u0218\u02baFXF",
                     title="caesar \u2014 input validation")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Task 1.1 \u2014 invalid key (0, 31) and "
                                        "invalid character ('2') are rejected.")
    p = shot_excerpt("lab1_3.png", lab1, start="Sarcina 1.2: cifrul cu cuvant-cheie",
                     end="Plaintext: CRIPTOGRAFIAPEINTELESULTUTUROR",
                     title="caesar \u2014 Task 1.2 (keyword ROMANIA, k = 3)")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Task 1.2 \u2014 permuted alphabet built "
                                        "from the keyword ROMANIA, encryption and decryption.")
    U.para(doc, "Together the three runs verify the specification end to end: "
                "Fig. 1 shows that encryption and decryption are exact inverses "
                "over the 31-letter alphabet; Fig. 2 confirms that the input "
                "constraints (key in 1\u201330, only Romanian letters and spaces) are "
                "enforced with explicit, re-prompting messages instead of "
                "crashing; and Fig. 3 demonstrates the two-key construction, "
                "printing the keyword-derived permuted alphabet "
                "\u201cR O M A N I \u0102 \u00c2 B C \u2026\u201d so that the mapping can be "
                "checked by hand against the ciphertext.")

    U.heading(doc, "5. Conclusions")
    U.para(doc, "Both ciphers were implemented and validated. The classical "
                "Caesar cipher has a key space of only 30 keys, so it offers no "
                "real security: a ciphertext is recovered instantly by brute "
                "force. Moving the shift into a keyword-permuted alphabet "
                "enlarges the key space and hides the simple shift pattern, but "
                "the cipher stays monoalphabetic \u2014 each plain letter always maps "
                "to the same cipher letter \u2014 so it is still defeated by letter "
                "frequency analysis and by the recognisable patterns of frequent "
                "words. This is exactly the weakness exploited in Laboratory "
                "Work No. 2.")

    U.references(doc, [
        "Laboratory Work No. 1 \u2014 Caesar Cipher. UTM, FCIM \u2014 handout (resources/).",
        "Table 2. Letter encoding of the Romanian alphabet (n = 31) \u2014 handout.",
        "W. Stallings. Cryptography and Network Security: Principles and Practice. "
        "Classical encryption systems.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab1", "Report_Lab1_Caesar_Dinu_Plesu.docx")
    doc.save(out)
    return out


# --------------------------------------------------------------------------
# Lab 2
# --------------------------------------------------------------------------
def build_lab2():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 2, "Cryptanalysis of monoalphabetic ciphers \u2014 "
                         "frequency analysis attack (variant V20)")

    U.heading(doc, "1. Task")
    U.para(doc, "A message intercepted from an enemy channel is known to have "
                "been encrypted with a monoalphabetic substitution cipher over "
                "a natural language. The variant assigned to the student "
                "(k = 20) is the ciphertext V20. The task is to recover the "
                "plaintext without knowing the key, using the statistical "
                "attack described in the handout: build the letter-frequency "
                "table, apply the mechanical (most-frequent \u2192 most-frequent) "
                "substitution, then refine the substitution interactively by "
                "examining word patterns, short words and frequent digraphs "
                "until the text becomes readable.")

    U.heading(doc, "2. Theoretical contents")
    U.para(doc, "In a monoalphabetic substitution cipher each letter of the "
                "alphabet is replaced by a fixed, unique substitute; the cipher "
                "is therefore a permutation of the alphabet. Although the key "
                "space is huge (26! \u2248 4\u00d710\u00b2\u2076 for English), the "
                "frequency of each cipher letter is exactly the frequency of the "
                "corresponding plain letter. Every language has a characteristic "
                "frequency profile (Tables 2.1 and 2.2 of the handout for "
                "Romanian and English).")
    U.para(doc, "The attack proceeds iteratively. First the observed cipher "
                "frequencies are ranked and matched against the most frequent "
                "letters of the language \u2014 a mechanical mapping that usually "
                "produces a partially readable text. The result is then refined "
                "by a human analyst: two- and three-letter words, recurring "
                "digraphs and the shapes of frequent words reveal further "
                "letter correspondences, which are applied and the text is "
                "re-examined. The quality of a candidate substitution can be "
                "measured with the chi-square statistic:")
    U.code_block(doc, [
        "    \u03c7\u00b2 = \u03a3\u1d62 (O\u1d62 \u2212 E\u1d62)\u00b2 / E\u1d62   (sum over all letters i)",
        "    O\u1d62 = observed count of the i-th plain letter,",
        "    E\u1d62 = expected count from the language frequency profile.",
    ])
    U.para(doc, "A substitution that approaches the true key drives \u03c7\u00b2 "
                "down sharply and turns the masked word list (unknown letters "
                "shown as \u201c*\u201d) into recognisable words.")
    U.para(doc, "Nothing in the attack inherently requires a computer: it is a "
                "manual, human-driven procedure that can be carried out on paper "
                "from the frequency tables of the handout, or with any online "
                "frequency-analysis tool. A program only automates the "
                "bookkeeping \u2014 counting letters, ranking them and keeping the "
                "candidate substitution consistent \u2014 while every actual letter "
                "correspondence is still chosen by the analyst from the "
                "linguistic evidence.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "For reproducibility the attack was run with a small local "
                "tool, lab2 (Go, file freq.go) \u2014 the same manual procedure, "
                "with the arithmetic automated. The result is equally achievable "
                "by hand or with an online frequency-analysis website; the "
                "program was preferred only because it recomputes the frequency "
                "table and \u03c7\u00b2 after every correspondence, keeps the substitution "
                "a bijection, and makes the whole attack repeatable from the "
                "repository. Option 2 asks for the language profile, prints the "
                "ranked frequency table of the ciphertext, applies the automatic "
                "frequency mapping, and enters an interactive loop with the "
                "commands <CIFRATA>=<CLARA> (assign a correspondence), del, tab "
                "(frequency table), text (current decryption) and gata (finish) "
                "\u2014 the analyst, not the program, decides each mapping. Key "
                "fragments:")
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
    U.para(doc, "Because the intercepted text V20 is written in English, the "
                "English profile (Table 2.2) was selected for the analysis; with "
                "the automatic mapping in place, 13 manual corrections were "
                "enough to complete the substitution.")

    U.heading(doc, "4. Results of the work")
    lab2 = read(os.path.join(CAP, "lab2.txt"))
    attack = read(os.path.join(REPO, "Lab2", "lab2_attack_full.txt"))
    p = shot_excerpt("lab2_1.png", lab2, start="$ ./lab2",
                     end="\u00ceBOUSOADUNOMASYBXQA\u00cePSO", title="lab2 \u2014 Caesar demo")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Option 1 \u2014 a Caesar cryptogram produced "
                                        "with k = 11 (warm-up example).")
    p = shot_excerpt("lab2_2.png", attack, start="Lungimea textului",
                     end="Chi-square al substitutiei automate: 47.8",
                     max_lines=42, title="lab2 \u2014 frequency table + automatic mapping")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Ranked frequency table of V20 and the "
                                        "mechanical (automatic) substitution; "
                                        "\u03c7\u00b2 of the automatic mapping = 47.8.")
    p = shot_excerpt("lab2_3.png", attack, start="> G=N", end="> I=R",
                     max_lines=26, title="lab2 \u2014 interactive refinement")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Interactive step: the correction G=N "
                                        "(the letter N is freed from its old mapping) and "
                                        "the partial decryption that follows it.")
    p = shot_excerpt("lab2_4.png", attack, start="> text", end="> gata",
                     max_lines=20, title="lab2 \u2014 recovered plaintext (fragment)")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. The fully recovered plaintext (fragment): "
                                        "the Black Chamber and the Washington Naval Conference. "
                                        "The complete text (618 words) is saved to "
                                        "Lab2/v20_plain.txt.")
    U.para(doc, "The recovered message is an excerpt from J. Kahn's \u201cThe "
                "Codebreakers\u201d describing the Black Chamber, Yardley and the "
                "Washington Naval Conference; the complete text (618 words) was "
                "saved to Lab2/v20_plain.txt and is reused as the signed message "
                "in Laboratory Work No. 6.")
    U.para(doc, "Read together, the four figures trace the full attack: Fig. 2 "
                "establishes the mechanical starting point \u2014 the ranked cipher "
                "frequencies matched to English, with \u03c7\u00b2 = 47.8 for the pure "
                "most-frequent \u2192 most-frequent guess; Fig. 3 shows a single "
                "linguistic correction (G=N) and the partial text it immediately "
                "unlocks; and Fig. 4 is the end state, a coherent plaintext. The "
                "13 corrections between Fig. 2 and Fig. 4 are the analyst's "
                "reasoning, not the program's.")

    U.heading(doc, "5. Conclusions")
    U.para(doc, "The monoalphabetic substitution cipher was fully broken without "
                "any knowledge of the key. Letter-frequency ranking plus word "
                "pattern analysis recovered the entire plaintext of variant V20 "
                "with 13 manual corrections on top of the automatic mapping. "
                "This confirms that monoalphabetic ciphers, whatever their key "
                "space, are insecure against a statistically grounded "
                "cryptanalytic attack \u2014 the classical frequency analysis known "
                "since Al-Kindi. The attack is fundamentally interactive and "
                "linguistic: the analyst reads the text, recognises word shapes "
                "and steers each correspondence, while \u03c7\u00b2 merely measures how "
                "close the candidate already is \u2014 the software, whether a local "
                "script or an online tool, is only the workbench.")

    U.references(doc, [
        "Lucrare de laborator nr. 2 \u2014 Criptanaliza cifrurilor monoalfabetice. "
        "UTM, FCIM \u2014 handout (resources/).",
        "Tables 2.1\u20132.4 \u2014 reference letter frequencies for Romanian and English.",
        "J. Kahn. The Codebreakers \u2014 the story of secret writing (source of the V20 text).",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab2", "Report_Lab2_Criptanaliza_Dinu_Plesu.docx")
    doc.save(out)
    return out


# --------------------------------------------------------------------------
# Lab 3
# --------------------------------------------------------------------------
def build_lab3():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 3, "Polyalphabetic ciphers \u2014 the Vigen\u00e8re cipher over "
                         "the Romanian alphabet (task 3.2)")

    U.heading(doc, "1. Task")
    U.para(doc, "The students with an even number in the group register solve "
                "task 3.2: implement the Vigen\u00e8re cipher over the Romanian "
                "alphabet (n = 31, codes 0\u202630 from Table 2). The program must "
                "encrypt and decrypt a text given interactively with a keyword "
                "key k\u2082 of at least 7 Romanian letters, display the key codes "
                "\u201ck\u1d62\u201d and apply the formulas c\u1d62 = (m\u1d62 + "
                "k\u1d62) mod 31 and m\u1d62 = (c\u1d62 \u2212 k\u1d62) mod 31. "
                "Invalid keys and invalid characters must be reported clearly.")

    U.heading(doc, "2. Theoretical contents")
    U.para(doc, "The Vigen\u00e8re cipher is polyalphabetic: instead of a single "
                "substitution it applies a sequence of Caesar shifts, cycling "
                "through a keyword. Each letter of the keyword supplies its own "
                "shift, taken from the alphabet encoding table. For an alphabet "
                "of n letters and a keyword K = k\u2081k\u2082\u2026k\u2113 of length "
                "\u2113 (with codes k\u1d62), the i-th plaintext letter m\u1d62 is encrypted as")
    U.code_block(doc, [
        "    c\u1d62 = (m\u1d62 + k\u1d62) mod n       with k\u1d62 = code(K[i mod \u2113])",
        "    m\u1d62 = (c\u1d62 \u2212 k\u1d62 + n) mod n",
    ])
    U.para(doc, "For Romanian n = 31. Because the same plain letter encrypts to "
                "different cipher letters depending on its position, the flat "
                "frequency profile of a monoalphabetic cipher disappears; the "
                "ciphertext frequency roughly flattens towards the language "
                "average, which defeats simple frequency analysis. The cipher "
                "is nevertheless not unconditionally secure: the key length \u2113 "
                "can be discovered with the Kasiski examination or the index of "
                "coincidence, after which the text decomposes into \u2113 "
                "interleaved monoalphabetic Caesar ciphers that are each broken "
                "by frequency.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "Task 3.2 was implemented in Go (file task_vigenere.go). The "
                "keyword is validated (at least 7 Romanian letters), converted "
                "to codes over Table 2, and encryption/decryption loop over the "
                "repeating key:")
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
    U.para(doc, "The program prints the normalized text, the processed keyword, "
                "the key codes k\u1d62, the formula used and the resulting "
                "ciphertext or plaintext, so every step can be checked by hand.")

    U.heading(doc, "4. Results of the work")
    lab3 = read(os.path.join(CAP, "lab3.txt"))
    p = shot_excerpt("lab3_1.png", lab3, start="=== Sarcina 3.2",
                     end="Criptograma: \u02baEUPGWGHO\u0218INNSJT\u0102SGRIDHMFDCMEODAERICC\u0102RGINJO",
                     title="lab3 \u2014 Vigen\u00e8re encryption (k\u2082 = ROMANIA)")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Task 3.2 \u2014 encryption with the keyword "
                                        "ROMANIA; key codes [20 17 15 0 16 10 0] and c\u1d62 = "
                                        "(m\u1d62+k\u1d62) mod 31.")
    p = shot_excerpt("lab3_2.png", lab3, start="Introduceti criptograma",
                     end="Mesajul decriptat: CRIPTOGRAFIAESTEOSTIINTAFRUMOASASIIMPORTANTA",
                     title="lab3 \u2014 Vigen\u00e8re decryption (round trip)")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Task 3.2 \u2014 decryption of the same "
                                        "ciphertext returns the original message.")
    p = shot_excerpt("lab3_3.png", lab3, start="verificarea validarilor",
                     end="Caracter invalid: '1'.", title="lab3 \u2014 keyword validation")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Validation \u2014 a keyword shorter than 7 "
                                        "letters and a keyword containing digits are rejected.")
    U.para(doc, "The three runs confirm both correctness and usability: Fig. 1 "
                "prints the processed keyword and its key codes "
                "[20 17 15 0 16 10 0] so that the shift applied at every "
                "position is transparent and hand-checkable, Fig. 2 proves the "
                "round trip is lossless, and Fig. 3 shows the validation rules "
                "rejecting a short keyword and a keyword containing digits, "
                "each with an explicit message.")

    U.heading(doc, "5. Conclusions")
    U.para(doc, "The Vigen\u00e8re cipher over the Romanian alphabet was implemented "
                "and verified: encryption and decryption are exact inverses and "
                "all input constraints (keyword length, admissible characters) "
                "are enforced with explicit messages. Compared with the "
                "monoalphabetic ciphers of Labs 1\u20132, the polyalphabetic "
                "structure hides the letter frequencies \u2014 the ciphertext "
                "frequency profile flattens \u2014 so a plain frequency attack no "
                "longer works directly. However the cipher is breakable once the "
                "key period is found (Kasiski / index of coincidence), which "
                "motivates the one-time pad and modern stream ciphers.")

    U.references(doc, [
        "Lucrare de laborator nr. 3 \u2014 Cifruri polialfabetice. UTM, FCIM \u2014 handout "
        "(resources/).",
        "Table 2 \u2014 letter encoding of the Romanian alphabet (n = 31).",
        "W. Stallings. Cryptography and Network Security \u2014 Vigen\u00e8re cipher and "
        "cryptanalysis.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab3", "Report_Lab3_Vigenere_Dinu_Plesu.docx")
    doc.save(out)
    return out


# --------------------------------------------------------------------------
# Lab 4  (DES, task 2.9)
# --------------------------------------------------------------------------
def build_lab4():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 4, "Block ciphers \u2014 the DES algorithm "
                         "(task 2.9: determining S_j(B_j))")

    U.heading(doc, "1. Task")
    U.para(doc, "The task number is nr_sarcina = k mod 11 = 20 mod 11 = 9. "
                "Task 2.9: in round i one obtains the 48-bit value "
                "K\u1d62 \u2295 E(R\u1d62\u208b\u2081); for a given box index j "
                "(1\u20138) determine the 4-bit output S\u2c7c(B\u2c7c) of the "
                "j-th S-box, showing all intermediate steps. In addition, the "
                "whole DES algorithm (key schedule, the 16 Feistel rounds, the "
                "final permutation) was implemented so the value used in the "
                "task is a genuine round value and can be checked against the "
                "FIPS test vector.")

    U.heading(doc, "2. Theoretical contents")
    U.para(doc, "DES processes 64-bit blocks with a 56-bit key. A block is "
                "first permuted with IP, then run through 16 identical Feistel "
                "rounds that split the block into (L\u1d62\u208b\u2081, "
                "R\u1d62\u208b\u2081):")
    U.code_block(doc, [
        "    L\u1d62 = R\u1d62\u208b\u2081 ,   R\u1d62 = L\u1d62\u208b\u2081 \u2295 f(R\u1d62\u208b\u2081, K\u1d62)",
        "    f(R, K) = P( S\u2081(B\u2081) \u2026 S\u2088(B\u2088) ),  where B\u2081\u2026B\u2088 are the",
        "    eight 6-bit blocks of  K \u2295 E(R)  (E expands R from 32 to 48 bits).",
    ])
    U.para(doc, "Each S-box maps 6 bits to 4 bits. The outer bits b\u2081b\u2086 "
                "select one of the four rows and the inner bits "
                "b\u2082b\u2083b\u2084b\u2085 select one of the sixteen columns; "
                "the value at that position, written in binary, is the 4-bit "
                "output. Concatenating the eight outputs gives 32 bits, which "
                "the permutation P scatters. This S-box step is the only "
                "non-linear component of DES and the heart of its "
                "cryptographic strength. Task 2.9 asks exactly for one such "
                "lookup.")
    U.para(doc, "The key schedule expands the 64-bit key to 56 bits with PC-1, "
                "splits it into C\u2080/D\u2080, left-shifts each half by 1 or 2 "
                "positions per round (the SHIFTS table), and compresses the "
                "result to 48 bits with PC-2 to produce the round subkeys "
                "K\u2081\u2026K\u2081\u2086.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "DES was implemented from scratch in Python (file des_lab.py). "
                "The S-box selection of Task 2.9 is:")
    U.code_block(doc, [
        "bits = bits_of(value48, 48)          # cei 48 de biti sub forma de \u20180\u2019/\u20181\u2019",
        "blocks = grouped(bits, 6)            # B1..B8, cate 6 biti",
        "bj = blocks[j - 1]                   # blocul cutiei cerute",
        "row = int(bj[0] + bj[5], 2)          # b1 b6  -> linia",
        "col = int(bj[1:5], 2)                # b2 b3 b4 b5 -> coloana",
        "value = SBOX[j - 1][row][col]        # iesirea pe 4 biti a cutiei-S",
    ])
    U.para(doc, "The program prints every intermediate step \u2014 the eight 6-bit "
                "blocks, the chosen row/column, the printed S-box table with "
                "the selected cell marked, the 4-bit result, and (for context) "
                "all eight S-box outputs followed by the P permutation, i.e. "
                "the complete f function of the round. A self-test against the "
                "FIPS-81 known-answer vector verifies the whole "
                "implementation.")

    U.heading(doc, "4. Results of the work")
    lab4 = read(os.path.join(CAP, "lab4.txt"))
    p = shot_excerpt("lab4_1.png", lab4, start="meniul 5: test",
                     end="REZULTAT: CORECT", title="des_lab \u2014 FIPS self-test")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Self-test against the FIPS known-answer "
                                        "vector: key 133457799BBCDFF1, plaintext "
                                        "0123456789ABCDEF \u2192 ciphertext 85E813540F0AB405.")
    p = shot_excerpt("lab4_2.png", lab4, start="Dupa PC-1 (56 biti)",
                     end="K16 (PC-2, 48 biti)", max_lines=44,
                     title="des_lab \u2014 key schedule (PC-1, shifts, PC-2)")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Key schedule \u2014 PC-1, the C\u2080/D\u2080 "
                                        "halves, the per-round left shifts and the 16 "
                                        "subkeys K\u2081\u2026K\u2081\u2086.")
    p = shot_excerpt("lab4_3.png", lab4, start="meniul 4: criptarea completa",
                     end="Blocul criptat (hex)", max_lines=44,
                     title="des_lab \u2014 full 16-round encryption")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Full encryption of a block \u2014 each round "
                                        "shows E(R\u1d62\u208b\u2081), K\u1d62 \u2295 E(R\u1d62\u208b\u2081), the S-box "
                                        "outputs and the new (L, R); the final ciphertext "
                                        "matches the FIPS vector.")
    p = shot_excerpt("lab4_4.png", lab4, start="meniul 1: sarcina 2.9",
                     end="dupa permutarea P", max_lines=44,
                     title="des_lab \u2014 task 2.9 (i = 5, j = 3)")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. Task 2.9 \u2014 given "
                                        "K\u2085 \u2295 E(R\u2084) = 0xC60503EB51A2, the block "
                                        "B\u2083 = 010100 gives r = 0, c = 10, so "
                                        "S\u2083(B\u2083) = S\u2083[0][10] = 12 = 1100\u2082 (binar).")
    U.para(doc, "The evidence forms a closed, reproducible loop: Fig. 1 anchors "
                "the whole implementation to the published FIPS-81 vector "
                "(133457799BBCDFF1 / 0123456789ABCDEF \u2192 85E813540F0AB405), "
                "Fig. 2 and Fig. 3 expose the internal state \u2014 all sixteen "
                "subkeys and a fully traced round \u2014 that a reviewer can "
                "recompute by hand, and Fig. 4 isolates the single S-box lookup "
                "required by Task 2.9, reducing K\u2085 \u2295 E(R\u2084) = 0xC60503EB51A2 "
                "to the cell S\u2083[0][10] = 12 = 1100\u2082.")

    U.heading(doc, "5. Conclusions")
    U.para(doc, "Task 2.9 was solved and cross-checked: the 48-bit value is "
                "split into eight 6-bit blocks, the outer bits select the row "
                "and the inner bits the column, and the S-box entry is the "
                "4-bit output \u2014 here S\u2083(B\u2083) = 1100\u2082 (binar). Implementing "
                "the entire DES algorithm (not only the isolated lookup) was "
                "necessary to obtain a genuine K\u1d62 \u2295 E(R\u1d62\u208b\u2081) value "
                "and to confirm the result inside the real f function; the FIPS "
                "known-answer test validates the complete implementation. The "
                "work makes clear why the S-boxes are the core of DES: they are "
                "the sole non-linear step, and without them the cipher would "
                "collapse into a system of linear equations over GF(2).")

    U.references(doc, [
        "Lucrare de laborator nr. 4 \u2014 Cifruri bloc. Algoritmul DES. UTM, FCIM \u2014 "
        "handout (resources/).",
        "FIPS PUB 46-3 \u2014 Data Encryption Standard (DES) and the FIPS test vectors.",
        "W. Stallings. Cryptography and Network Security \u2014 chapter on DES.",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab4", "Report_Lab4_DES_Dinu_Plesu.docx")
    doc.save(out)
    return out


# --------------------------------------------------------------------------
# Lab 5  (RSA, ElGamal, Diffie-Hellman + AES)
# --------------------------------------------------------------------------
def build_lab5():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 5, "Public-key cryptography \u2014 RSA, ElGamal and "
                         "Diffie-Hellman with an AES-256 session key")

    U.heading(doc, "1. Task")
    U.para(doc, "Using Wolfram Alpha (or Wolfram Mathematica) reproduce the "
                "public-key computations of the handout for the student number "
                "k = 20. Sarcina 2.1 \u2014 RSA: generate two 1024-bit primes, "
                "form N = P\u00b7Q (\u2265 2048 bits), \u03d5(N), the public "
                "exponent e = 65537 and the private exponent d, then encrypt "
                "and decrypt the message. Sarcina 2.2 \u2014 ElGamal over the "
                "given 2048-bit safe prime p with generator g = 2: build the "
                "keys and the ciphertext (c\u2081, c\u2082) and decrypt. "
                "Sarcina 3 \u2014 Diffie-Hellman: Alice and Bob agree on a "
                "shared secret over the same p, g, derive an AES-256 key as "
                "SHA-256 of the shared secret and encrypt the message block "
                "with it. The message is the student's name, "
                "\u201cDinu Plesu\u201d.")

    U.heading(doc, "2. Theoretical contents")
    U.para(doc, "RSA rests on the hardness of factoring N = P\u00b7Q. Key "
                "generation picks large primes P and Q, sets N = P\u00b7Q and "
                "\u03d5(N) = (P\u22121)(Q\u22121), chooses e with gcd(e, "
                "\u03d5(N)) = 1 and computes d = e\u207b\u00b9 mod \u03d5(N). "
                "Encryption and decryption are")
    U.code_block(doc, [
        "    c = m^e mod N        encryption (public key (e, N))",
        "    m = c^d mod N        decryption (private key (d, N))",
        "    because c^d = (m^e)^d = m^(e*d) = m^1 (mod N) = m,",
        "    since e*d = 1 (mod phi(N)) and m^phi(N) = 1 (mod N).",
    ])
    U.para(doc, "ElGamal over a safe prime p = 2q + 1 with generator g uses a "
                "secret x, the public key y = g^x mod p, and encrypts m with "
                "a fresh random k as (c\u2081, c\u2082) = (g^k mod p, "
                "m\u00b7y^k mod p); decryption is "
                "m = c\u2082\u00b7(c\u2081^x)\u207b\u00b9 mod p.")
    U.para(doc, "Diffie-Hellman lets two parties derive a common secret over an "
                "insecure channel: Alice sends A = g^a mod p, Bob sends "
                "B = g^b mod p, and both compute K = B^a = A^b = "
                "g^(a*b) mod p. The shared secret is fed to a KDF "
                "(SHA-256) to obtain an AES-256 key that encrypts the message "
                "block with AES in ECB mode.")

    U.heading(doc, "3. Implementation")
    U.para(doc, "The handout suggests wolframalpha.com or Wolfram Mathematica. "
                "The free Wolfram Alpha interface cannot be scripted and is "
                "impractical at these sizes \u2014 it must generate 1024-bit primes "
                "and reduce 2048-bit moduli interactively \u2014 so the identical "
                "computations were reproduced in Python (file main.py) with "
                "arbitrary-precision integers. Python's built-in "
                "pow(base, exp, mod) is exactly Wolfram's PowerMod and "
                "pow(e, -1, \u03d5) is ModInverse, so the same three primitives "
                "(prime generation, modular exponentiation, modular inverse) "
                "underlie both; the AES layer is in verify_dh_aes.py. The "
                "essential steps:")
    U.code_block(doc, [
        "p = gen_prime(1024);  q = gen_prime(1024);  n = p*q      # RSA modulus",
        "while n.bit_length() < 2048: q = gen_prime(1024); n = p*q # exact 2048 bits",
        "phi = (p-1)*(q-1);  e = 65537;  d = pow(e, -1, phi)      # keys",
        "c = pow(m, e, n);   m2 = pow(c, d, n)                    # encrypt/decrypt",
        "",
        "# Diffie-Hellman + AES-256",
        "A = pow(G, a, P);   B = pow(G, b, P);   K = pow(B, a, P)",
        "key = hashlib.sha256(K.to_bytes(256, 'big')).digest()    # AES-256 key",
    ])
    U.para(doc, "The message is converted to an integer as required by the "
                "handout (ASCII \u2192 hex string \u2192 decimal). The message "
                "conversion, the primality tests, the modular inverses and the "
                "AES-256 encryption of the padded block are all verified by "
                "assertions in the scripts.")

    U.heading(doc, "4. Results of the work")
    lab5 = read(os.path.join(CAP, "lab5.txt"))
    p = shot_excerpt("lab5_1.png", lab5, start="== Sarcina 2.1 RSA",
                     end="Verificare: (e*d) mod phi = 1", max_lines=12,
                     title="main.py \u2014 RSA (2048-bit modulus)")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Sarcina 2.1 \u2014 RSA: P, Q are 1024-bit "
                                        "primes, N is 2048 bits; encryption/decryption round "
                                        "trip is OK and e\u00b7d \u2261 1 (mod \u03d5).")
    p = shot_excerpt("lab5_2.png", lab5, start="== Sarcina 2.2 ElGamal",
                     end="-> OK", max_lines=14, title="main.py \u2014 ElGamal (p 2048-bit)")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Sarcina 2.2 \u2014 ElGamal over the given "
                                        "safe prime p (g = 2): keys, ciphertext (c\u2081, c\u2082) "
                                        "and successful decryption.")
    p = shot_excerpt("lab5_3.png", lab5, start="== Sarcina 3 Diffie-Hellman",
                     end="Cheie AES-256 = SHA-256(K)", max_lines=12,
                     title="main.py \u2014 Diffie-Hellman + AES-256 KDF")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Sarcina 3 \u2014 Alice and Bob compute "
                                        "identical shared secrets; SHA-256(K) yields the "
                                        "AES-256 key.")
    p = shot_excerpt("lab5_4.png", lab5, start="KAT AES-256",
                     end="ciphertext:", title="verify_dh_aes.py \u2014 AES-256 encryption")
    U.add_image(doc, p); U.caption(doc, "Fig. 4. verify_dh_aes.py \u2014 the FIPS-197 AES "
                                        "known-answer test passes and the block "
                                        "\u201cDinu Plesu\u201d is encrypted with the derived "
                                        "AES-256 key.")
    U.para(doc, "Each figure documents a required value, not merely a "
                "screenshot: Fig. 1 proves the RSA modulus is a full 2048 bits "
                "and that the round trip and the key relation e\u00b7d \u2261 1 (mod \u03d5) "
                "hold; Fig. 2 shows ElGamal decryption recovering m over the "
                "given 2048-bit safe prime; Fig. 3 confirms both parties reach "
                "the same Diffie-Hellman secret from which SHA-256(K) derives "
                "the AES-256 key; and Fig. 4 grounds that session key in a "
                "passing FIPS-197 known-answer test before encrypting the block "
                "\u201cDinu Plesu\u201d.")

    U.heading(doc, "5. Conclusions")
    U.para(doc, "All three public-key tasks were reproduced and verified. RSA "
                "encryption/decryption round-trips correctly and the key "
                "relation e\u00b7d \u2261 1 (mod \u03d5(N)) holds; the modulus is a "
                "full 2048-bit number, which requires care because the product "
                "of two 1024-bit primes can occasionally be only 2047 bits. "
                "ElGamal decryption returns the original message and "
                "Diffie-Hellman yields an identical shared secret for both "
                "parties, from which a valid AES-256 key is derived and the "
                "message block is encrypted. The work demonstrates the "
                "practical difference between symmetric and asymmetric "
                "cryptography and how the two are combined in real protocols "
                "(a public-key exchange to derive a symmetric session key).")

    U.references(doc, [
        "Lucrare de laborator nr. 5 \u2014 Criptografia cu chei publice. UTM, FCIM \u2014 "
        "handout (resources/).",
        "R. Rivest, A. Shamir, L. Adleman \u2014 RSA (1978); W. Diffie, M. Hellman "
        "\u2014 New Directions in Cryptography (1976).",
        "FIPS PUB 197 \u2014 Advanced Encryption Standard (AES).",
    ])
    U.source_code(doc, URL)
    out = os.path.join(OUT, "Lab5", "Report_Lab5_CheiePublica_Dinu_Plesu.docx")
    doc.save(out)
    return out


# --------------------------------------------------------------------------
# Lab 6  (hash functions + RSA/NTLM and ElGamal/Whirlpool signatures)
# --------------------------------------------------------------------------
def build_lab6():
    doc = U.new_document()
    U.add_page_numbers(doc)
    U.title_page(doc, 6, "Hash functions and digital signatures \u2014 "
                         "RSA/NTLM and ElGamal/Whirlpool")

    U.heading(doc, "1. Task")
    U.para(doc, "The hash functions are assigned by list index "
                "i = (k mod 24) + 1 = (20 mod 24) + 1 = 21. From list 1 "
                "(RSA signatures) index 21 gives the NTLM hash; from list 2 "
                "(ElGamal signatures) index 21 gives the Whirlpool hash. The "
                "message m to be signed is the plaintext recovered in "
                "Laboratory Work No. 2 (variant V20). Task: generate an RSA "
                "digital signature of H = NTLM(m) and an ElGamal digital "
                "signature of H = Whirlpool(m), validate both signatures, and "
                "verify the hash functions against standard test vectors.")

    U.heading(doc, "2. Theoretical contents")
    U.para(doc, "A cryptographic hash function H maps an arbitrary message to a "
                "fixed-size digest and must be pre-image resistant, "
                "second-pre-image resistant and collision resistant, while "
                "being fast to compute. NTLM is built on MD4: the message is "
                "padded, processed in 64-byte blocks with four rounds of "
                "bitwise logic functions and modular additions, producing a "
                "128-bit digest. MD4 is cryptographically broken \u2014 practical "
                "collision attacks exist \u2014 so NTLM is retained here only as the "
                "assigned legacy hash and must not be used in real systems. "
                "Whirlpool (ISO/IEC 10118-3) is a 512-bit "
                "hash based on an AES-like Miyaguchi-Preneel construction with "
                "a 512-bit block and a 512-bit output.")
    U.para(doc, "A digital signature binds a digest to a signer's private key. "
                "With RSA the signature of a digest H (converted to an integer) "
                "is s = H^d mod n and verification recovers "
                "v = s^e mod n = H; anyone holding the public key (e, n) "
                "checks v = H. With ElGamal over a safe prime p with generator "
                "g and secret key x, signing a digest H chooses a random k with "
                "gcd(k, p\u22121) = 1 and produces")
    U.code_block(doc, [
        "    s\u2081 = g^k mod p",
        "    s\u2082 = k\u207b\u00b9 \u00b7 (H \u2212 x\u00b7s\u2081) mod (p\u22121)",
        "    verification:  g^H  =  y^s\u2081 \u00b7 s\u2081^s\u2082  (mod p)",
        "    where y = g^x mod p is the public key.",
    ])

    U.heading(doc, "3. Implementation")
    U.para(doc, "The lab was implemented in Python (main.py, md4.py, whirlpool "
                "module). NTLM is computed as MD4 over the UTF-16LE encoding of "
                "the message; a dedicated MD4 implementation was written and "
                "validated against all seven RFC 1320 test vectors. The ElGamal "
                "signature uses the safe prime p of the handout. Core steps:")
    U.code_block(doc, [
        "# RSA signature over NTLM",
        "H = int.from_bytes(ntlm(m), 'big')          # digest -> integer",
        "s = pow(H, d, n)                            # sign with private key",
        "v = pow(s, e, n);  assert v == H            # validate",
        "",
        "# ElGamal signature over Whirlpool",
        "H = int.from_bytes(whirlpool(m).digest(), 'big')",
        "s1 = pow(G, kA, p)",
        "s2 = (pow(kA, -1, p-1) * (H - x*s1)) % (p-1)",
        "v1 = pow(G, H, p);  v2 = pow(y, s1, p) * pow(s1, s2, p) % p",
        "assert v1 == v2",
    ])
    U.para(doc, "An anti-corruption check additionally verifies that tampering "
                "with the digest (H + 1) makes the ElGamal verification fail. "
                "The Whirlpool implementation was cross-checked against three "
                "ISO/IEC 10118-3 known-answer vectors, and the MD4 "
                "implementation against the RFC 1320 vectors.")

    U.heading(doc, "4. Results of the work")
    hashtest = read(os.path.join(CAP, "lab6_hashtest.txt"))
    full = read(os.path.join(CAP, "lab6_full.txt"))
    p = shot_excerpt("lab6_1.png", hashtest, start="Verificarea Whirlpool",
                     end="Toate cele 3 vectori", title="main.py --hash-test \u2014 Whirlpool KAT")
    U.add_image(doc, p); U.caption(doc, "Fig. 1. Whirlpool verified against the three "
                                        "ISO/IEC 10118-3 known-answer vectors (empty string, "
                                        "\u201cabc\u201d, the quick-brown-fox sentence).")
    p = shot_excerpt("lab6_2.png", full, start="SARCINA 2 - SEMNATURA RSA",
                     end="SEMNATURA VALIDA", max_lines=30,
                     title="main.py \u2014 RSA signature, hash = NTLM")
    U.add_image(doc, p); U.caption(doc, "Fig. 2. Sarcina 2 \u2014 RSA signature of H = NTLM(m) "
                                        "with a 3072-bit modulus: validation v = s^e mod n "
                                        "returns H (signature valid).")
    p = shot_excerpt("lab6_3.png", full, start="SARCINA 3 - SEMNATURA ELGAMAL",
                     end="control anticoruptie", max_lines=32,
                     title="main.py \u2014 ElGamal signature, hash = Whirlpool")
    U.add_image(doc, p); U.caption(doc, "Fig. 3. Sarcina 3 \u2014 ElGamal signature of "
                                        "H = Whirlpool(m): g^H = y^s\u2081\u00b7s\u2081^s\u2082 "
                                        "(mod p) and the anti-corruption check both hold.")
    U.para(doc, "The three runs move from component to system: Fig. 1 validates "
                "the Whirlpool primitive against the published ISO vectors, "
                "Fig. 2 shows the RSA signature of H = NTLM(m) verifying "
                "(v = s^e mod n returns H), and Fig. 3 shows the ElGamal "
                "signature satisfying g^H = y^s\u2081\u00b7s\u2081^s\u2082 (mod p) \u2014 together "
                "with the anti-corruption check, which confirms that altering "
                "the digest (H + 1) invalidates the signature.")

    U.heading(doc, "5. Conclusions")
    U.para(doc, "Both signatures were generated and validated. The RSA "
                "signature of the NTLM digest verifies because "
                "s^e = (H^d)^e = H^(e\u00b7d) = H mod n; "
                "the ElGamal signature satisfies g^H = "
                "y^s\u2081\u00b7s\u2081^s\u2082 (mod p), and the "
                "anti-corruption check confirms that any change to the digest "
                "breaks verification. Implementing MD4 from scratch and fixing "
                "a subtle round-constant bug against the RFC 1320 vectors, and "
                "validating Whirlpool against the ISO vectors, underscored the "
                "importance of testing hash functions against published "
                "known-answer vectors \u2014 a signature scheme is only as strong "
                "as the hash underneath it. The recovered Lab 2 message served "
                "as the signed message, linking the whole practical sequence "
                "together.")

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
    doc.save(out)
    return out


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    for fn in (build_lab1, build_lab2, build_lab3, build_lab4, build_lab5,
               build_lab6):
        print("wrote", fn())
