#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lucrarea de laborator nr. 4 - Cifruri bloc. Algoritmul DES.

Sarcina aleasa (nr_sarcina = k mod 11, k = 20  ->  20 mod 11 = 9):

    Sarcina 2.9. In runda i a algoritmului DES am obtinut
                 K_i XOR E(R_{i-1}) = ... (48 biti).
                 Sa se determine S_j(B_j) pentru un j dat.

Programul:
  * afiseaza tabelele utilizate (cutiile-S, permutarile IP/FP/E/P/PC-1/PC-2);
  * afiseaza toti pasii intermediari ai sarcinii 2.9 ( impartirea celor 48
    de biti in B1..B8, bitii de rand/coloana, intrarea in cutia-S aleasa);
  * permite introducerea datelor de intrare de la utilizator SAU generarea
    lor aleatorii (conform cerintei din enunt);
  * contine implementarea completa a algoritmului DES (programul de chei,
    toate cele 16 runde, permutarile finale), pentru ca intregul algoritm
    sa poata fi prezentat si verificat (testul clasic DES).

Verificare cu vectorul de test cunoscut:
    key = 133457799BBCDFF1, plaintext = 0123456789ABCDEF
    -> ciphertext = 85E813540F0AB405
"""

import random
import sys

# ---------------------------------------------------------------------------
# 1. Tabelele algoritmului DES
# ---------------------------------------------------------------------------

# Permutarea initiala (IP) si permutarea finala (FP = IP^-1)
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]
FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
]

# Expandarea E: 32 biti -> 48 biti (cu replicarea unor biti)
E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1,
]

# Permutarea P de iesire din functia f
P = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25,
]

# Permutarile cheii: PC-1 (64 -> 56), PC-2 (56 -> 48)
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4,
]
PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]

# Numarul de deplasari la stanga pentru fiecare runda
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Cele 8 cutii-S (4 linii x 16 coloane; intrarea de 6 biti -> iesirea de 4 biti)
SBOX = [
    # S1
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    # S2
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    # S3
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    # S4
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    # S5
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    # S6
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    # S7
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    # S8
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]],
]


# ---------------------------------------------------------------------------
# 2. Functii ajutatoare
# ---------------------------------------------------------------------------

def permute(block: str, table: list) -> str:
    """Aplica o permutare (tabel de indici 1-based) peste sirul de biti."""
    return ''.join(block[i - 1] for i in table)


def xor(a: str, b: str) -> str:
    return ''.join('0' if x == y else '1' for x, y in zip(a, b))


def to_hex(bits: str) -> str:
    return ''.join(f'{int(bits[i:i + 4], 2):X}' for i in range(0, len(bits), 4))


def bits_of(data: str, nbits: int) -> str:
    """Hex (0x.../fara prefix) sau biti direct -> sir de exact nbits biti."""
    s = data.strip().replace(' ', '').replace('_', '')
    if all(c in '01' for c in s) and len(s) == nbits:
        return s
    s = s.replace('0x', '').replace('0X', '')
    if not all(c in '0123456789abcdefABCDEF' for c in s):
        raise ValueError('datele trebuie sa fie biti sau hexazecimal')
    if len(s) * 4 > nbits:
        raise ValueError(f'prea multe cifre hexazecomale pentru {nbits} biti')
    return format(int(s, 16), f'0{nbits}b')


def grouped(bits: str, size: int) -> list:
    return [bits[i:i + size] for i in range(0, len(bits), size)]


def read_line(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        print()
        sys.exit(0)


def read_choice(prompt: str, valid: list) -> str:
    while True:
        v = read_line(prompt).strip()
        if v in valid:
            return v
        print(f'  Valoare invalida. Alegeti una dintre: {", ".join(valid)}')


# ---------------------------------------------------------------------------
# 3. Sarcina 2.9 - determinarea lui S_j(B_j)
# ---------------------------------------------------------------------------

def print_sbox(j: int, highlight=None) -> None:
    """Afiseaza cutia-S cu numarul j (1..8), eventual cu celula evidentiata."""
    box = SBOX[j - 1]
    print(f'    Tabelul cutiei-S S{j} (liniile = bitii b1b6, coloanele = b2b3b4b5):')
    print('         ' + ' '.join(f'{c:>3}' for c in range(16)))
    for r in range(4):
        row = ' '.join(f'{box[r][c]:>3}' for c in range(16))
        mark = '   <- linia aleasa' if highlight and highlight[0] == r else ''
        print(f'     r{r}:  {row}{mark}')
    if highlight:
        r, c = highlight
        print(f'    Selectie: linia {r}, coloana {c} -> S{j}[{r}][{c}] = '
              f'{box[r][c]} = {box[r][c]:04b}b')


def task_2_9(value48: str, j: int, round_no: int, show_all: bool = True) -> str:
    """
    Sarcina 2.9: primind cei 48 de biti K_i XOR E(R_{i-1}), determinam
    S_j(B_j) pentru un j dat. Afiseaza totii pasii intermediari.
    """
    bits = bits_of(value48, 48)
    blocks = grouped(bits, 6)

    print('\n  Pasul 1. Sirul primit (48 biti), impartit in 8 blocuri de 6 biti:')
    print('    ' + ' '.join(f'B{n+1}' for n in range(8)))
    print('    ' + ' '.join(b for b in blocks))
    if show_all:
        print(f'    (hexazecimal: 0x{to_hex(bits)})')

    print(f'\n  Pasul 2. Se lucreaza cu B{j} = {blocks[j-1]} (6 biti).')
    bj = blocks[j - 1]
    row = int(bj[0] + bj[5], 2)          # bitii de sus/jos: b1 b6
    col = int(bj[1:5], 2)                # bitii din mijloc: b2 b3 b4 b5
    print(f'      b1 b6 (bitii de rand)       = {bj[0]}{bj[5]}  -> r = {row}')
    print(f'      b2 b3 b4 b5 (bitii de coloana) = {bj[1:5]}  -> c = {col}')

    print(f'\n  Pasul 3. Cautarea in cutia-S:')
    print_sbox(j, highlight=(row, col))
    value = SBOX[j - 1][row][col]

    print(f'\n  Pasul 4. Rezultatul: S{j}(B{j}) = {value} = {value:04b} (4 biti)')
    if show_all:
        print('\n  Pasul 5 (contextul complet in functia f): toate cele 8 cutii-S:')
        outs = []
        for n in range(8):
            b = blocks[n]
            r = int(b[0] + b[5], 2)
            c = int(b[1:5], 2)
            v = SBOX[n][r][c]
            outs.append(f'{v:04b}')
            print(f'      S{n+1}(B{n+1}) = S{n+1}(b1b6={b[0]}{b[5]}, '
                  f'b2b3b4b5={b[1:5]}) = S{n+1}[{r}][{c}] = {v:04b}  '
                  f'({b} -> {v:04b})')
        f_out = ''.join(outs)
        print(f'      S1(B1)S2(B2)...S8(B8) = {f_out}  (32 biti)')
        print(f'      dupa permutarea P      = {permute(f_out, P)}')
        print(f'      R_i = L_(i-1) XOR P(...)   [vezi sarcina 2.8/2.10]')
    return f'{value:04b}'


# ---------------------------------------------------------------------------
# 4. Implementarea completa a algoritmului DES (pentru intregul algoritm)
# ---------------------------------------------------------------------------

def key_schedule(key: str, verbose: bool = False):
    """Cheile de runda K1..K16 (48 biti); daca verbose, afiseaza toti pasii."""
    key64 = bits_of(key, 64)
    if verbose:
        print(f'  Cheia (64 biti): {to_hex(key64)}  {key64}')
        print(f'  Bitii de paritate (8,16,...,64) se elimina prin PC-1.')
    k56 = permute(key64, PC1)
    c, d = k56[:28], k56[28:]
    if verbose:
        print(f'  Dupa PC-1 (56 biti): {k56}')
        print(f'  C0 = {c}   D0 = {d}')
    round_keys = []
    for i in range(16):
        c = c[SHIFTS[i]:] + c[:SHIFTS[i]]
        d = d[SHIFTS[i]:] + d[:SHIFTS[i]]
        ki = permute(c + d, PC2)
        round_keys.append(ki)
        if verbose:
            print(f'  Runda {i+1:2}: deplasare la stanga {SHIFTS[i]}  '
                  f'C{i+1} = {c}  D{i+1} = {d}')
            print(f'            K{i+1} (PC-2, 48 biti) = {ki}  '
                  f'= 0x{to_hex(ki)}')
    return round_keys


def des_encrypt_block(pt: str, key: str, verbose: bool = False) -> str:
    """Criptarea unui bloc de 64 biti; daca verbose, afiseaza pasii."""
    block = permute(bits_of(pt, 64), IP)
    if verbose:
        print(f'  Textul clar (64 biti) : {to_hex(bits_of(pt, 64))}')
        print(f'  Dupa IP               : {block}')
        print(f'    L0 = {block[:32]}')
        print(f'    R0 = {block[32:]}')
    rkeys = key_schedule(key, verbose=False)
    if verbose:
        print('\n  Programul de chei (vezi meniul 3 pentru detalii):')
        for i, k in enumerate(rkeys, 1):
            print(f'    K{i:2} = 0x{to_hex(k)}')
    l, r = block[:32], block[32:]
    for i in range(16):
        expanded = permute(r, E)
        x = xor(expanded, rkeys[i])
        blocks6 = grouped(x, 6)
        s_out = ''
        for n in range(8):
            b = blocks6[n]
            row = int(b[0] + b[5], 2)
            col = int(b[1:5], 2)
            s_out += f'{SBOX[n][row][col]:04b}'
        f_out = permute(s_out, P)
        l, r = r, xor(l, f_out)
        if verbose:
            print(f'\n  Runda {i+1:2}:')
            print(f'    E(R{i})            = {expanded}')
            print(f'    K{i+1} XOR E(R{i})  = {x}  (48 biti)')
            print(f'    B1..B8             = {" ".join(blocks6)}')
            print(f'    S1..S8             = {" ".join(grouped(s_out,4))}')
            print(f'    dupa P (f)         = {f_out}')
            print(f'    L{i+1} = R{i}       = {l}')
            print(f'    R{i+1} = L{i} XOR f = {r}')
    preout = r + l  # schimbul final L16/R16
    ct = permute(preout, FP)
    if verbose:
        print(f'\n  Schimbul final (R16, L16): {preout}')
        print(f'  Dupa permutarea finala FP: {ct}')
        print(f'  Blocul criptat (hex)      : {to_hex(ct)}')
    return to_hex(ct)


def self_test() -> bool:
    """Vector de test DES clasic (FIPS 46 / NBS SP 500-20)."""
    ct = des_encrypt_block('0123456789ABCDEF', '133457799BBCDFF1')
    ok = ct == '85E813540F0AB405'
    print(f'  cheie = 133457799BBCDFF1, text clar = 0123456789ABCDEF')
    print(f'  text cifrat obtinut = {ct}')
    print(f'  text cifrat asteptat = 85E813540F0AB405')
    print(f'  REZULTAT: {"CORECT - test trecut" if ok else "GRESIT"}')
    return ok


# ---------------------------------------------------------------------------
# 5. Meniul interactiv
# ---------------------------------------------------------------------------

def read_48(prompt: str, allow_random: bool = True) -> str:
    while True:
        v = read_line(prompt).strip()
        if allow_random and v.lower() in ('r', 'rand', 'random', 'a', 'aleator'):
            val = random.getrandbits(48)
            print(f'  (valoare generata aleatoriu: 0x{val:012X} = '
                  f'{val:048b})')
            return format(val, '048b')
        try:
            return bits_of(v, 48)
        except ValueError as e:
            print(f'  Date invalide ({e}). Introduceti 48 de biti (0/1) '
                  f'sau 12 cifre hexazecimale, ori "r" pentru generare '
                  f'aleatorie.')


def read_j() -> int:
    while True:
        v = read_line('  Numarul cutiei-S j (1-8) [sau "r" aleator]: ').strip()
        if v.lower() in ('r', 'aleator'):
            j = random.randint(1, 8)
            print(f'  (j generat aleatoriu: j = {j})')
            return j
        if v.isdigit() and 1 <= int(v) <= 8:
            return int(v)
        print('  j trebuie sa fie un intreg intre 1 si 8.')


def read_round() -> int:
    while True:
        v = read_line('  Numarul rundei i (1-16) [sau "r" aleator]: ').strip()
        if v.lower() in ('r', 'aleator'):
            i = random.randint(1, 16)
            print(f'  (i generat aleatoriu: i = {i})')
            return i
        if v.isdigit() and 1 <= int(v) <= 16:
            return int(v)
        print('  i trebuie sa fie un intreg intre 1 si 16.')


def main() -> None:
    random.seed()  # sursa aleatorie reala (poate fi fixata cu --seed)
    if '--seed' in sys.argv:
        random.seed(2026)  # reproducibilitate pentru raport

    print('=' * 78)
    print('LUCRAREA DE LABORATOR NR. 4 - CIFRURI BLOC. ALGORITMUL DES')
    print('Sarcina 2.9 (k = 20 -> nr_sarcina = 20 mod 11 = 9):')
    print('  In runda i am obtinut K_i XOR E(R_i-1) = ... (48 biti);')
    print('  sa se determine S_j(B_j) pentru un j dat.')
    print('=' * 78)

    while True:
        print('\nOptiuni:')
        print('  1 = Sarcina 2.9: determinarea lui S_j(B_j)')
        print('  2 = Afișarea cutiilor-S (tabelele folosite)')
        print('  3 = Programul de chei (PC-1, deplasari, PC-2, K1..K16)')
        print('  4 = Criptarea completa a unui bloc (toate cele 16 runde)')
        print('  5 = Test de verificare (vectorul clasic DES)')
        print('  0 = Iesire')
        c = read_choice('Alegeti optiunea: ', ['0', '1', '2', '3', '4', '5'])

        if c == '0':
            print('La revedere!')
            return
        elif c == '1':
            print('\n--- SARCINA 2.9 ---')
            print('Valorile pot fi introduse de utilizator sau generate aleator.')
            i = read_round()
            v = read_48('  K_i XOR E(R_i-1) (48 biti / 12 cifre hex / "r"): ')
            j = read_j()
            print(f'\n  Runda i = {i}; valoarea de 48 de biti, cutia j = {j}.')
            task_2_9(v, j, i)
        elif c == '2':
            sel = read_line('  Ce cutie afisam (1-8 sau "toate"): ').strip().lower()
            if sel == 'toate':
                for n in range(1, 9):
                    print_sbox(n)
                    print()
            elif sel.isdigit() and 1 <= int(sel) <= 8:
                print_sbox(int(sel))
            else:
                print('  Selectie invalida.')
        elif c == '3':
            key = read_line('  Cheia DES (8 octeti hex, ex. 133457799BBCDFF1): ')
            try:
                key_schedule(key, verbose=True)
            except ValueError as e:
                print(f'  Cheie invalida: {e}')
        elif c == '4':
            pt = read_line('  Blocul de text clar (8 octeti hex): ')
            key = read_line('  Cheia (8 octeti hex): ')
            try:
                des_encrypt_block(pt, key, verbose=True)
            except ValueError as e:
                print(f'  Date invalide: {e}')
        elif c == '5':
            print('\n--- Test de verificare ---')
            self_test()


if __name__ == '__main__':
    main()
