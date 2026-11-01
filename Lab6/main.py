#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lucrarea de laborator nr. 6 - Functii hash si semnaturi digitale

Mesajul m este mesajul obtinut la Lucrarea de laborator nr. 2 - textul clar
recuperat prin atacul cu analiza frecventei (varianta V20), pastrat in
Lab2/v20_plain.txt; aici m este incarcat din acel fisier (cu rezerva
inglobata daca fisierul lipseste).

Sarcina 2: semnatura RSA peste hash, n >= 3072 biti
Sarcina 3: semnatura ElGamal peste hash, p = 2048 biti (din enunt), g = 2

Functia hash se alege dupa formula i = (k mod 24) + 1, unde k este numarul
de ordine al studentului in lista grupei. Pentru k = 20 (grupa FAF-241):
  - lista sarcinii 2: i = (20 mod 24) + 1 = 21 -> NTLM
  - lista sarcinii 3: i = (20 mod 24) + 1 = 21 -> Whirlpool
NTLM se calculeaza cu implementarea MD4 din md4.py. Whirlpool nu este in
stdlib-ul Python: se foloseste pachetul "whirlpool" sau, ca rezerva, OpenSSL
(provider legacy); cele doua surse sunt verificate incrucisat (aceleasi
vectori de test ISO 10118-3).

Toate valorile hash sunt convertite in intregi zecimali, conform notei din
enunt (hex -> decimal). Echivalentele Wolfram Alpha sunt comentate la pas.
"""

import hashlib
import os
import random
import subprocess
import sys
from math import gcd

# Hash NTLM/MD4 prin implementare proprie MD4 (md4.py).
from md4 import md4

try:
    from Cryptodome.Hash import MD4 as _MD4lib
except ImportError:
    try:
        from Crypto.Hash import MD4 as _MD4lib
    except ImportError:
        _MD4lib = None

HERE = os.path.dirname(os.path.abspath(__file__))   # folderul Lab6/
LAB2_PLAIN = os.path.join(HERE, os.pardir, "Lab2", "v20_plain.txt")

STUDENT_NO = 20         # <<< numarul de ordine in lista grupei (FAF-241)
random.seed(20261013)   # reproductibilitate


# ------------------------------------------------------------- functii utile
def egcd(a, b):
    """Euclid extins (iterativ - recursivitatea depaseste limita Python la
    numere de 2048 biti). Wolfram: ExtendedGCD[a, b]"""
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


def modinv(a, m):
    """Invers modular. Wolfram: PowerMod[a, -1, m]"""
    g, x, _ = egcd(a % m, m)
    assert g == 1, "inversul modular nu exista"
    return x % m


def is_probable_prime(n, rounds=40):
    """Miller-Rabin. Wolfram: PrimeQ[n]"""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits):
    """Prim pseudoaleator cu exact `bits` biti.
    Wolfram: RandomPrime[{2^(bits-1), 2^bits - 1}]"""
    while True:
        c = random.randrange(1 << (bits - 1), 1 << bits) | 1
        if is_probable_prime(c):
            return c


def short(v, width=60):
    """Afiseaza un intreg mare trunchiat, cu numarul de cifre."""
    s = str(v)
    if len(s) <= width:
        return s
    return f"{s[:width]}...({len(s)} cifre)"


# -------------------------------------------------------------- alegerea hash
HASH_NAMES = ["", "MD4", "MD5", "MD2", "MD6-128", "MD6-256", "MD6-512",
              "SHA-1", "SHA-224", "SHA-256", "SHA-384", "SHA-512",
              "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512",
              "RipeMD-128", "RipeMD-160", "RipeMD-256", "RipeMD-320",
              "Whirlpool", "NTLM", "Haval192,3", "Haval224,4", "Haval256,4"]
# Lista sarcinii 3 (ElGamal): 1 NTLM, 2 MD4, ..., 20 RipeMD-320,
# 21 Whirlpool, 22 Haval192,3, 23 Haval224,4, 24 Haval256,4.
HASH_NAMES_S3 = ["", "NTLM", "MD4", "MD5", "MD2", "MD6-128", "MD6-256",
                 "MD6-512", "SHA-1", "SHA-224", "SHA-256", "SHA-384",
                 "SHA-512", "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512",
                 "RipeMD-128", "RipeMD-160", "RipeMD-256", "RipeMD-320",
                 "Whirlpool", "Haval192,3", "Haval224,4", "Haval256,4"]

i2 = (STUDENT_NO % 24) + 1
i3 = (STUDENT_NO % 24) + 1
name2, name3 = HASH_NAMES[i2], HASH_NAMES_S3[i3]


def _whirlpool_hex(data: bytes) -> str:
    """Whirlpool (ISO 10118-3) - 512 biti. Surse, in ordine:
      1. pachetul "whirlpool" (implementare pura/C, instalat cu pip);
      2. OpenSSL, daca suporta digest-ul (whirlpool);
      3. OpenSSL cu provider-ul "legacy".
    Daca doua surse sunt disponibile, rezultatele se verifica intre ele.
    Vectori de test ISO cunoscuti (verificati ruland --hash-test):
      W("")  = 19fa61d75522a4669b44e39c1d2e1726...
      W("abc") = 4e2448a4c6f486bb16b6562c73b4020b...
    """
    results = []
    try:
        import whirlpool
        results.append(("whirlpool", whirlpool.new(data).hexdigest()))
    except ImportError:
        pass
    for args in (["-whirlpool"], ["-provider", "default", "-provider",
                                  "legacy", "-whirlpool"]):
        try:
            p = subprocess.run(["openssl", "dgst"] + args,
                               input=data, capture_output=True, timeout=30)
            if p.returncode == 0 and b"=" in p.stdout:
                hx = p.stdout.split(b"=")[-1].strip().decode()
                results.append(("openssl", hx))
                break
        except (OSError, subprocess.TimeoutExpired):
            continue
    if not results:
        raise SystemExit(
            "Whirlpool indisponibil: instalati pachetul 'whirlpool' "
            "(pip install whirlpool) sau OpenSSL cu provider-ul legacy.")
    ref = results[0][1]
    for name, hx in results[1:]:
        assert hx == ref, f"Whirlpool: dezechilibru intre surse ({name})!"
    return ref


# Verificarea implementarii Whirlpool cu vectorii ISO 10118-3:
#   python3 main.py --hash-test
WHIRLPOOL_VECTORS = [
    (b"", "19fa61d75522a4669b44e39c1d2e1726c530232130d407f89afee0964997f7a7"
          "3e83be698b288febcf88e3e03c4f0757ea8964e59b63d93708b138cc42a66eb3"),
    (b"abc", "4e2448a4c6f486bb16b6562c73b4020bf3043e3a731bce721ae1b303d97e6d4"
             "c7181eebdb6c57e277d0e34957114cbd6c797fc9d95d8b582d225292076d4eef5"),
    (b"The quick brown fox jumps over the lazy dog",
     "b97de512e91e3828b40d2b0fdce9ceb3c4a71f9bea8d88e75c4fa854df36725fd2b5"
     "2eb6544edcacd6f8beddfea403cb55ae31f03ad62a5ef54e42ee82c3fb35"),
]


def hash_test() -> None:
    """Ruleaza vectorii de test ISO pentru Whirlpool (verificare)."""
    print("Verificarea Whirlpool cu vectorii ISO 10118-3:")
    for data, expected in WHIRLPOOL_VECTORS:
        got = _whirlpool_hex(data)
        label = data[:40] if data else b'(sir gol)'
        status = "OK" if got == expected else "GRESIT"
        print(f"  W({label!r}) = {got[:48]}... -> {status}")
        assert got == expected, "Vector de test ISO nerespectat!"
    print("Toate cele 3 vectori de test sunt corecte.")


if "--hash-test" in sys.argv:
    hash_test()
    raise SystemExit(0)


def compute_hash(name, text):
    """Returneaza (hex, intreg_zecimal) pentru functia hash aleasa.
    Wolfram: Hash[string, "SHA384"] etc., apoi conversia hexazecimal->zecimal."""
    data = text.encode("utf-8")
    if name.startswith("SHA3-"):
        h = hashlib.new(name.lower().replace("-", ""), data).hexdigest()
    elif name.startswith("SHA"):
        h = hashlib.new(name.lower(), data).hexdigest()
    elif name == "MD5":
        h = hashlib.md5(data).hexdigest()
    elif name == "MD4":
        h = md4(data).hex()
    elif name == "NTLM":
        h = md4(text.encode("utf-16-le")).hex()
        if _MD4lib is not None:  # verificare incrucisata cu Pycryptodome
            ref = _MD4lib.new()
            ref.update(text.encode("utf-16-le"))
            assert ref.hexdigest() == h, "Mismatch MD4 vs Pycryptodomex!"
    elif name == "Whirlpool":
        h = _whirlpool_hex(data)
    else:
        raise SystemExit(f"Functia {name} nu este disponibila in stdlib; "
                         "folositi alta optiune din lista sau Wolfram Alpha.")
    return h, int(h, 16)


# ------------------------------------------------------------------ mesajul m
# Mesajul obtinut la lucrarea nr. 2 (textul clar recuperat prin analiza
# frecventei, varianta V20). Daca fisierul Lab2/v20_plain.txt lipseste,
# se foloseste rezerva inglobata mai jos (acelasi text).
FALLBACK_LAB2 = (
    "A few months before the November opening of the disarmament conference "
    "in Washington, daily courier service was set up between the Black "
    "Chamber and the State Department."
)


def load_lab2_message() -> str:
    try:
        with open(LAB2_PLAIN, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return FALLBACK_LAB2


M = load_lab2_message()

print("=" * 78)
print("LUCRAREA DE LABORATOR NR. 6 - FUNCTII HASH SI SEMNATURI DIGITALE")
print(f"Numar student (lista grupei): k = {STUDENT_NO}")
print("\nMesajul m = mesajul obtinut la Lucrarea de laborator nr. 2")
print("(textul clar recuperat prin analiza frecventei, varianta V20):")
print(M if len(M) <= 400 else M[:400] + " ...")
print(f"(lungime: {len(M)} caractere)")

# ============================================================== SARCINA 2
print("\n" + "=" * 78)
print(f"SARCINA 2 - SEMNATURA RSA, hash = {name2}  [i = ({STUDENT_NO} mod 24)+1 = {i2}]")

# Pasul 1 - exponent public
e = 65537
print("\nPasul 1: exponentul public e = 65537 (ales astfel incat gcd(e, phi)=1)")

# Pasul 2 - cheile: p,q primi de 1536 biti => n = p*q are 3072 biti
print("Pasul 2: se genereaza p si q primi de 1536 biti (Wolfram: RandomPrime)...")
p2 = random_prime(1536)
q2 = random_prime(1536)
n2 = p2 * q2
phi2 = (p2 - 1) * (q2 - 1)
# p*q of two 1536-bit primes can be 3071 bits; e must also be invertible.
while q2 == p2 or n2.bit_length() < 3072 or gcd(e, phi2) != 1:
    q2 = random_prime(1536)
    n2 = p2 * q2
    phi2 = (p2 - 1) * (q2 - 1)
assert n2.bit_length() >= 3072, "n trebuie sa aiba cel putin 3072 biti"
assert gcd(e, phi2) == 1
d2 = modinv(e, phi2)
print(f"  p = {short(p2)}")
print(f"  q = {short(q2)}")
print(f"  n = p*q  ({n2.bit_length()} biti) = {short(n2)}")
print(f"  phi(n) = (p-1)(q-1) = {short(phi2)}")
print(f"  d = e^-1 mod phi(n)  (Wolfram: PowerMod[e,-1,phi]) = {short(d2)}")
print(f"  Cheie publica (e, n); cheie secreta (d, n)")

# Pasul 3 - hash-ul lui m
h2_hex, H2 = compute_hash(name2, M)
print(f"\nPasul 3: H = {name2}(m)")
print(f"  hex: {h2_hex}")
print(f"  zecimal (conform notei): {short(H2)}")
assert H2 < n2, "H trebuie sa fie < n (informatie redundanta la RSA real)"

# Pasul 4 - semnarea
s2 = pow(H2, d2, n2)  # Wolfram: PowerMod[H, d, n]
print(f"\nPasul 4: semnatura s = H^d mod n (PowerMod[H,d,n]):")
print(f"  s = {short(s2)}")

# Pasul 5 - validarea
v2 = pow(s2, e, n2)  # Wolfram: PowerMod[s, e, n]
print(f"\nPasul 5: validarea v = s^e mod n:")
print(f"  v == H ? {v2 == H2}  -> SEMNATURA VALIDA")
with open(os.path.join(HERE, "rsa_params.txt"), "w") as f:
    f.write(f"hash={name2}\ne={e}\np={p2}\nq={q2}\nn={n2}\nphi={phi2}\n"
            f"d={d2}\nH_dec={H2}\ns={s2}\n")
print("  (parametrii completi: Lab6/rsa_params.txt)")

# ============================================================== SARCINA 3
print("\n" + "=" * 78)
print(f"SARCINA 3 - SEMNATURA ELGAMAL, hash = {name3}  [i = ({STUDENT_NO} mod 24)+1 = {i3}]")

P = 32317006071311007300153513477825163362488057133489075174588434139269806834136210002792056362640164685458556357935330816928829023080573472625273554742461245741026202527916572972862706300325263428213145766931414223654220941111348629991657478268034230553086349050635557712219187890332729569696129743856241741236237225197346402691855797767976823014625397933058015226858730761197532436467475855460715043896844940366130497697812854295958659597567051283852132784468522925504568272879113720098931873959143374175837826000278034973198552060607533234122603254684088120031105907484281003994966956119696956248629032338072839127039
G = 2
print("\nPasul 1: verificarea parametrilor din enunt (p, g)")
print(f"  p are {P.bit_length()} biti; g = {G}; q_ord = (p-1)/2")
# (PrimeQ[p] in Wolfram confirma primalitatea lui p; p este safe prime)

# Pasul 2 - cheia secreta x, cheia publica y = g^x mod p
x3 = random.randrange(2, P - 2)     # Wolfram: RandomInteger[{2, p-2}]
y3 = pow(G, x3, P)                  # Wolfram: PowerMod[g, x, p]
print(f"Pasul 2: cheia secreta x = {short(x3)}")
print(f"Pasul 3: cheia publica y = g^x mod p = {short(y3)}")

# Pasul 4 - hash-ul
h3_hex, H3 = compute_hash(name3, M)
print(f"\nPasul 4: H = {name3}(m)")
print(f"  hex: {h3_hex}")
print(f"  zecimal: {short(H3)}")

# Pasul 5 - semnarea (s1, s2): se alege k_A cu gcd(k_A, p-1) = 1
kA = random.randrange(2, (P - 1) // 2)
while gcd(kA, P - 1) != 1:
    kA = random.randrange(2, (P - 1) // 2)
s1 = pow(G, kA, P)                       # Wolfram: PowerMod[g,kA,p]
kinv = modinv(kA, P - 1)                 # Wolfram: PowerMod[kA,-1,p-1]
s2v = (kinv * (H3 - x3 * s1)) % (P - 1)  # Wolfram: Mod[kA^-1*(H-x*s1), p-1]
print(f"\nPasul 5: semnarea")
print(f"  kA (secret, gcd(kA,p-1)=1) = {short(kA)}")
print(f"  s1 = g^kA mod p                    = {short(s1)}")
print(f"  s2 = kA^-1 * (H - x*s1) mod (p-1)  = {short(s2v)}")

# Pasul 6 - validarea: g^H =? y^s1 * s1^s2 (mod p)
lhs = pow(G, H3, P)
rhs = (pow(y3, s1, P) * pow(s1, s2v, P)) % P
print(f"\nPasul 6: validarea")
print(f"  v1 = g^H mod p                = {short(lhs)}")
print(f"  v2 = y^s1 * s1^s2 mod p       = {short(rhs)}")
print(f"  v1 == v2 ? {lhs == rhs}  -> SEMNATURA VALIDA")

# demonstratie: semnatura invalida daca mesajul e alterat
H3t = H3 + 1
print(f"  control anticoruptie: pentru H' = H+1, g^H' mod p != v2 -> "
      f"{pow(G, H3t, P) != rhs}")

with open(os.path.join(HERE, "elgamal_sig_params.txt"), "w") as f:
    f.write(f"hash={name3}\nx={x3}\ny={y3}\nkA={kA}\nH_dec={H3}\ns1={s1}\ns2={s2v}\n")
print("  (parametrii completi: Lab6/elgamal_sig_params.txt)")

print("\nGATA: ambele semnaturi au fost generate si validate.")
