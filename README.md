# Cryptography and Security — Laboratory Works

**Dinu Plesu**, group **FAF-241** · Technical University of Moldova,
Faculty of Computers, Informatics and Microelectronics,
Department of Computer Science and Information Technologies
Supervisor: **Maia Zaica**

Source code and Word reports for laboratory works 1–6 of the discipline
*Cryptography and Security*, plus the Laboratory 5.2 PKI addendum.

---

## Verified

Status of every laboratory work. The table is generated from
[`reportgen/status.json`](reportgen/status.json) — see
[Updating this table](#updating-this-table).

<!-- status:begin -->

| Lab | Task | Language | Report | Verified | Presented |
|:--|:--|:--|:--|:--:|:--:|
| 1 | Caesar cipher and Caesar cipher with a keyword over the Romanian alphabet | Go | [`Report_Lab1_Caesar_Dinu_Plesu.docx`](Lab1/Report_Lab1_Caesar_Dinu_Plesu.docx) | ✅ | — |
| 2 | Cryptanalysis of monoalphabetic ciphers — frequency analysis attack (variant V20) | Go | [`Report_Lab2_Criptanaliza_Dinu_Plesu.docx`](Lab2/Report_Lab2_Criptanaliza_Dinu_Plesu.docx) | ✅ | — |
| 3 | Polyalphabetic ciphers — the Vigenère cipher over the Romanian alphabet (task 3.2) | Go | [`Report_Lab3_Vigenere_Dinu_Plesu.docx`](Lab3/Report_Lab3_Vigenere_Dinu_Plesu.docx) | ✅ | — |
| 4 | Block ciphers — the DES algorithm (task 2.9: determining S_j(B_j)) | Python | [`Report_Lab4_DES_Dinu_Plesu.docx`](Lab4/Report_Lab4_DES_Dinu_Plesu.docx) | ✅ | — |
| 5 | Public-key cryptography — RSA, ElGamal and Diffie-Hellman with an AES-256 session key | Python | [`Report_Lab5_CheiePublica_Dinu_Plesu.docx`](Lab5/Report_Lab5_CheiePublica_Dinu_Plesu.docx) | ✅ | — |
| 6 | Hash functions and digital signatures — RSA/NTLM and ElGamal/Whirlpool | Python | [`Report_Lab6_Hash_Semnaturi_Dinu_Plesu.docx`](Lab6/Report_Lab6_Hash_Semnaturi_Dinu_Plesu.docx) | ✅ | — |
| 5.2 | Addendum to Laboratory 5 — PKI with OpenSSL and digital signatures | Bash / OpenSSL | [`REPORT.md`](Lab5.2/REPORT.md) | ✅ | — |

<!-- status:end -->

**Legend**

- **Verified ✅** — the work was re-run end to end and every check passed.
  The evidence is reproducible: `python3 reportgen/verify.py` rebuilds the Go
  binaries from the committed sources and asserts the results quoted in the
  reports (the classic DES known-answer vector `85E813540F0AB405`, task 2.9's
  `S3[0][10] = 1100`, the RFC 1320 MD4 vectors, the three Whirlpool ISO
  vectors, both digital signatures, and each report's own ciphertexts).
  At the last full run: **32 checks passed, 0 failed, 0 skipped**.
- **Presented —** the work has not been defended yet. After a defence, flip
  `"presented": true` for that lab and regenerate the table.

### Updating this table

Do not edit the table inside `README.md`; it would be overwritten. Change the
flag in `reportgen/status.json` and regenerate:

```bash
python3 reportgen/build_readme.py
```

Only the block between `<!-- status:begin -->` and `<!-- status:end -->` is
rewritten, so everything else in this file stays as you wrote it — updating
one lab never means re-authoring the README.

---

## Variant 20 (student number 20)

Only some handouts use variants; the table records what number 20 selects.
The code prints the same choice at start-up.

| Lab | Selection rule | Assigned work |
|:--|:--|:--|
| 1 | no variants | Tasks 1.1 (Caesar) and 1.2 (Caesar + keyword) |
| 2 | variant V20 is the assigned ciphertext | Frequency-analysis attack on V20 |
| 3 | even student number → task 3.2 | Vigenère over the 31-letter alphabet; Playfair 3.1 is a bonus |
| 4 | 20 mod 11 = 9 | Task 2.9: determine S_j(B_j) for a chosen j |
| 5 | no variants | RSA 2.1, ElGamal 2.2, Diffie–Hellman + AES-256 (task 3) |
| 6 | i = (20 mod 24) + 1 = 21 | RSA signature with NTLM; ElGamal signature with Whirlpool |
| 5.2 | no variants | Internal PKI with OpenSSL: CA, issue, sign, verify, revoke |

---

## Working on one lab without redoing the others

The reports are generated from `build_reports.py`, then finalized in WordCraft.
The committed Lab 1, 3, 4, 5 and 6 `.docx` files also contain hand edits that
are not in the generator, so rebuilding one of those produces the earlier
layout. Lab 2 is the generated version with the online-service figures.

```bash
python3 reportgen/build_reports.py 3   # rebuild Laboratory 3's report only
python3 reportgen/build_reports.py     # rebuild all six (default)

python3 reportgen/verify.py 3          # re-check Laboratory 3 only
python3 reportgen/verify.py            # re-check everything

python3 reportgen/build_readme.py      # refresh the status table only
```

Rebuilds are deterministic: two consecutive runs produce byte-identical
`.docx` files, so rebuilding a report that did not change leaves git clean and
only genuine edits show up as modified.

---

## Repository layout

| Path | Contents |
|:--|:--|
| `Lab1/` … `Lab6/` | One directory per laboratory work: sources and the generated `.docx` report |
| `Lab5.2/` | PKI addendum (OpenSSL): `pki.sh`, `pki/` certificates and the `REPORT.md` report |
| `run.bat` | Windows menu runner for every lab, verification and report rebuild |
| `pdf/` | Final PDF exports of the six reports, with the TOC page numbers filled in |
| `reportgen/` | Everything that produces the reports |
| `reportgen/build_reports.py` | Builds the six `.docx` reports (all, or selected labs) |
| `reportgen/verify.py` | Functional verification of every laboratory work |
| `reportgen/build_readme.py` | Regenerates the status table in this README |
| `reportgen/status.json` | **Source of truth for the status table** |
| `reportgen/captures/` | Tracked terminal transcripts the reports quote, plus the `.sh` drivers that produced them |
| `reportgen/img/` | Rendered figures (`*.png` are regenerated, the UTM logo is tracked) |
| `resources/` | Handouts and the reference report used for the template |

Languages follow the handouts: **Go** for Labs 1–3, **Python** for Labs 4–6,
**Bash/OpenSSL** for Lab 5.2. Source languages are deliberately left
untouched.

---

## Running the works

### Windows: one-click runner

Double-click **`run.bat`** (or run it from `cmd`). It opens a menu for Labs
1–6 and 5.2, runs the interactive programs, and offers to install the only
missing Python package (`whirlpool`) or the report dependencies on demand.
Options 8 and 9 run `reportgen/verify.py` and rebuild the Word reports, so no
command syntax is required.

| Lab | Command |
|:--|:--|
| 1 | `cd Lab1 && go build -o caesar . && ./caesar` |
| 2 | `cd Lab2 && go build -o lab2 . && ./lab2` |
| 3 | `cd Lab3 && go build -o lab3 . && ./lab3` |
| 4 | `cd Lab4 && python3 des_lab.py --seed` |
| 5 | `cd Lab5 && python3 main.py all && python3 verify_dh_aes.py` |
| 6 | `cd Lab6 && python3 main.py --hash-test && python3 main.py` |
| 5.2 | `cd Lab5.2 && ./pki.sh status` |

On Windows, replace `python3` with `python` (or use `run.bat`).

Requirements: Go ≥ 1.22 (Labs 1–3), Python 3 (Labs 4–6), the `whirlpool`
package for Lab 6, and `python-docx` plus `Pillow` only to rebuild the reports.
`pycryptodome` is optional (it cross-checks the in-repo MD4). Lab 5.2 needs
Bash and OpenSSL 3 — Git Bash is enough on Windows.

Two commands write files, and both are safe: `Lab6/main.py` (without
`--hash-test`) rewrites `rsa_params.txt` and `elgamal_sig_params.txt`, but it
is seeded and `verify.py` asserts the result is byte-identical to what is
committed; `Lab5.2/pki.sh init|issue|sign|revoke` regenerate the PKI, so
verification uses only the read-only subcommands (`status`, `crl`, `verify`).

---

## Reports

The six reports are UTM/FCIM template documents (A4, Times New Roman 12 pt,
1.5 line spacing, margins 3/1.5/2/2 cm) built by
`reportgen/build_reports.py`, with a final WordCraft pass for document
properties, TOC fields, alt text and PDFs. Lab 2 also includes screenshots
from the online frequency-analysis service suggested in the handout.

**Note:** the committed Lab 1, 3, 4, 5 and 6 reports contain final hand edits
(step tables, equation numbers and expanded references) that are not in
`build_reports.py`. Rebuilding those five gives the earlier layout. Keep the
committed `.docx`/PDF versions as the submitted copies, or port the hand edits
back into the generator first.

```bash
wordcraft-cli convert Lab4/Report_Lab4_DES_Dinu_Plesu.docx \
    Lab4/Report_Lab4_DES_Dinu_Plesu.docx --update-fields
wordcraft-cli convert Lab4/Report_Lab4_DES_Dinu_Plesu.docx \
    pdf/Report_Lab4_DES_Dinu_Plesu.pdf --update-fields
```

The same command works for any report. The PDFs in `pdf/` are the exported
versions. If you rebuild a report with `build_reports.py`, run the WordCraft
step again; otherwise Word can also refresh the field with `F9`. The global
OpenCode `wordcraft` skill and MCP server expose the same workflow: open,
inspect, update the TOC, set document properties, save and export.

Reports are in English (the Lab 5.2 addendum is in Romanian); `resources/`
holds the original handouts.

Repository: <https://github.com/Prince-of-Nothing/CS-labs.git>
