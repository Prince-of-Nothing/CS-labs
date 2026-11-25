# Cryptography and Security — Laboratory Works

**Dinu Plesu**, group **FAF-241** · Technical University of Moldova,
Faculty of Computers, Informatics and Microelectronics.
Supervisor: **Maia Zaica**.

| Lab | Topic | Language | Folder |
|:--|:--|:--|:--|
| 1 | Caesar cipher and Caesar cipher with a keyword (Romanian alphabet) | Go | [`Lab1/`](Lab1) |
| 2 | Cryptanalysis of a monoalphabetic cipher by frequency analysis (variant V20) | Go | [`Lab2/`](Lab2) |
| 3 | Vigenère cipher, task 3.2 (Playfair 3.1 as a bonus) | Go | [`Lab3/`](Lab3) |
| 4 | DES, task 2.9: determining S<sub>j</sub>(B<sub>j</sub>) | Python | [`Lab4/`](Lab4) |
| 5 | RSA, ElGamal and Diffie-Hellman with an AES-256 key | Python | [`Lab5/`](Lab5) |
| 6 | Hash functions and digital signatures (RSA/NTLM, ElGamal/Whirlpool) | Python | [`Lab6/`](Lab6) |

Each folder holds the source code and the Word report. The reports as PDF are in
[`pdf/`](pdf), and the lab assignments are in [`resources/`](resources).

## Running

Requirements: Go 1.22 or newer (Labs 1–3), Python 3 (Labs 4–6), and the
`whirlpool` package for Lab 6 (`pip install whirlpool`).

| Lab | Command (from the repository root) |
|:--|:--|
| 1 | `cd Lab1 && go build -o caesar . && ./caesar` |
| 2 | `cd Lab2 && go build -o lab2 . && ./lab2` |
| 3 | `cd Lab3 && go build -o lab3 . && ./lab3` |
| 4 | `cd Lab4 && python3 des_lab.py --seed` |
| 5 | `cd Lab5 && python3 main.py all && python3 verify_dh_aes.py` |
| 6 | `cd Lab6 && python3 main.py --hash-test && python3 main.py` |

On Windows, use `python` instead of `python3` and `.\caesar` instead of `./caesar`.

- **Lab 2:** choose option 2 with the `en` profile and paste the text of
  `v20_cipher.txt` as one line. Corrections are typed as `G=N`; `gata` ends the attack.
- **Lab 4:** `--seed` makes random inputs repeatable. The full 16-round trace from the
  report is in `lab4_encrypt_full.txt`.
- **Lab 5:** each run saves the full values to `rsa_params.txt`, `elgamal_params.txt`
  and `dh_params.txt`; `verify_dh_aes.py` encrypts the message with the key from
  `dh_params.txt`.
- **Lab 6:** the signed message is the Lab 2 plaintext (`Lab2/v20_plain.txt`); the full
  values are saved to `rsa_params.txt` and `elgamal_sig_params.txt`.
