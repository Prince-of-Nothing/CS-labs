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
  reports (the FIPS-197 DES vector `85E813540F0AB405`, task 2.9's
  `S3[0][10] = 1100`, the RFC 1320 MD4 vectors, the three Whirlpool ISO
  vectors, both digital signatures, and each report's own ciphertexts).
  At the last full run: **30 checks passed, 0 failed, 0 skipped**.
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

## Working on one lab without redoing the others

The reports are generated, not hand-edited, so a single lab can be rebuilt,
re-checked or re-presented in isolation:

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

| Lab | Command |
|:--|:--|
| 1 | `cd Lab1 && go build -o caesar . && ./caesar` |
| 2 | `cd Lab2 && go build -o lab2 . && ./lab2` |
| 3 | `cd Lab3 && go build -o lab3 . && ./lab3` |
| 4 | `cd Lab4 && python3 des_lab.py --seed` |
| 5 | `cd Lab5 && python3 main.py all && python3 verify_dh_aes.py` |
| 6 | `cd Lab6 && python3 main.py --hash-test` |
| 5.2 | `cd Lab5.2 && ./pki.sh status` |

Requirements: Go ≥ 1.22 (Labs 1–3), Python 3 with `python-docx` and `Pillow`
(report generation). Lab 5 uses `pycryptodome` for the AES known-answer test;
Lab 6 needs the `whirlpool` package and `pycryptodome`; Lab 5.2 needs
OpenSSL 3.

Two commands write files, and both are safe: `Lab6/main.py` (without
`--hash-test`) rewrites `rsa_params.txt` and `elgamal_sig_params.txt`, but it
is seeded and `verify.py` asserts the result is byte-identical to what is
committed; `Lab5.2/pki.sh init|issue|sign|revoke` regenerate the PKI, so
verification uses only the read-only subcommands (`status`, `crl`, `verify`).

---

## Reports

The six reports are UTM/FCIM template documents (A4, Times New Roman 12 pt,
1.5 line spacing, margins 3/1.5/2/2 cm) built by
`reportgen/build_reports.py`. Each carries a title page with the UTM logo,
a *Table of Contents* whose page numbers are filled by Word when the file is
opened (the field is marked dirty and the document sets `updateFields`),
and the terminal sessions quoted in *Results of the work* as figures.

Reports are in English; `resources/` holds the original handouts.

Repository: <https://github.com/Prince-of-Nothing/CS-labs.git>
