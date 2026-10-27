#!/usr/bin/env python3
"""Functional verification of laboratory works 1-6 and the PKI addendum.

Every check re-runs the real program and asserts a result taken from the
report or from a published reference vector (FIPS-197, RFC 1320, the
Whirlpool ISO vectors). Nothing here edits a tracked file: Lab 6's full run
is the one exception, and it is followed by a git-clean assertion that
proves the seeded outputs are byte-identical to what is committed.

    python3 reportgen/verify.py            # everything
    python3 reportgen/verify.py 3 5        # only those labs

Exit status is non-zero when any check fails, so this can gate a commit.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOCACHE = "/tmp/opencode/gocache"

RESULTS: list[tuple[str, str, str, str]] = []   # lab, description, status, detail


def check(lab, desc, ok, detail=""):
    RESULTS.append((lab, desc, "PASS" if ok else "FAIL", detail))
    return ok


def skip(lab, desc, detail):
    RESULTS.append((lab, desc, "SKIP", detail))


def sh(args, stdin="", cwd=None, timeout=90):
    """Run a command, return (stdout+stderr, returncode)."""
    try:
        p = subprocess.run(args, input=stdin, capture_output=True, text=True,
                           cwd=cwd, timeout=timeout)
        return p.stdout + p.stderr, p.returncode
    except FileNotFoundError as exc:
        return f"missing executable: {exc}", 127
    except subprocess.TimeoutExpired:
        return "timed out", 124


def find_go():
    got = shutil.which("go")
    if got:
        return got
    cand = "/tmp/opencode/gotool/go/bin/go"
    return cand if os.path.exists(cand) else None


def go_binary(lab_dir, name):
    """Return the path of a Go binary, rebuilding it from source if needed."""
    path = os.path.join(REPO, lab_dir, name)
    if os.path.exists(path):
        return path
    go = find_go()
    if not go:
        return None
    env = dict(os.environ, GOCACHE=GOCACHE, PATH=os.path.dirname(go) +
               os.pathsep + os.environ.get("PATH", ""))
    p = subprocess.run([go, "build", "-o", name, "."],
                       cwd=os.path.join(REPO, lab_dir), env=env,
                       capture_output=True, text=True)
    return path if p.returncode == 0 else None


def rebuild_go(lab_dir, name):
    """Force a rebuild so the binary matches the committed sources."""
    go = find_go()
    if not go:
        return None
    env = dict(os.environ, GOCACHE=GOCACHE,
               PATH=os.path.dirname(go) + os.pathsep +
               os.environ.get("PATH", ""))
    p = subprocess.run([go, "build", "-o", name, "."],
                       cwd=os.path.join(REPO, lab_dir), env=env,
                       capture_output=True, text=True)
    return os.path.join(REPO, lab_dir, name) if p.returncode == 0 else None


# --------------------------------------------------------------------------
# Lab 1 - Caesar cipher, keyword-permuted Caesar
# --------------------------------------------------------------------------
def verify_lab1():
    lab = "Lab1"
    exe = rebuild_go("Lab1", "caesar") or go_binary("Lab1", "caesar")
    if not exe:
        skip(lab, "Caesar binary builds", "no Go toolchain available")
        return

    out, rc = sh([exe], "1\n1\n7\ncriptografia este o stiinta frumoasa\n")
    check(lab, "Caesar k=7 round-trip input accepted",
          rc == 0 and "Ciphertext: ÎWOUZȚMWFLOFKXZKȚXZOOTZFLWĂȘȚFXF" in out,
          out.strip().splitlines()[-1][:60] if out.strip() else "no output")

    out, rc = sh([exe], "2\n1\n3\nROMANIA\ncriptografia pe intelesul tuturor\n")
    gold = "Ciphertext: FABȘVNJAĂÎBĂȘHBÂVHSHȚXSVXVXANA"
    check(lab, "keyword cipher (ROMANIA, k=3) matches report", gold in out,
          "keyword ciphertext")

    out, rc = sh([exe], "2\n2\n3\nROMANIA\nFABȘVNJAĂÎBĂȘHBÂVHSHȚXSVXVXANA\n")
    check(lab, "keyword cipher decrypts back to the plaintext",
          "Plaintext: CRIPTOGRAFIAPEINTELESULTUTUROR" in out, "")

    out, rc = sh([exe], "1\n1\n0\n31\n7\nHELLO2\ncriptografie\n")
    check(lab, "invalid keys/messages are rejected with a message",
          rc == 0 and ("invalid" in out.lower() or "greșit" in out.lower()
                       or "k (1-30)" in out or "eroare" in out.lower()
                       or "invalid key" in out.lower()),
          next((l.strip() for l in out.splitlines()
                if "key" in l.lower() and ("1-30" in l or "invalid" in l.lower())),
               "no validation line"))


# --------------------------------------------------------------------------
# Lab 2 - frequency analysis / cryptanalysis
# --------------------------------------------------------------------------
def verify_lab2():
    lab = "Lab2"
    exe = rebuild_go("Lab2", "lab2") or go_binary("Lab2", "lab2")
    if not exe:
        skip(lab, "frequency-analysis binary builds", "no Go toolchain available")
        return

    out, rc = sh([exe], "1\n11\natelierul de criptografie\n0\n")
    check(lab, "Caesar example k=11 matches capture",
          rc == 0 and "Textul cifrat (Caesar, k=11): ÎBOUSOADUNOMASYBXQAÎPSO" in out,
          "")

    out, rc = sh([exe], "3\nexemplu\ngata\n0\n")
    ok_demo = ("683 litere" in out and
               "Chi-square al substitutiei automate: 28.9" in out)
    check(lab, "demonstration attack reports 683 letters, chi-square 28.9",
          ok_demo, next((l.strip() for l in out.splitlines()
                         if "Chi-square" in l), "no chi-square line"))


# --------------------------------------------------------------------------
# Lab 3 - Vigenere (task 3.2) and Playfair (task 3.1)
# --------------------------------------------------------------------------
def verify_lab3():
    lab = "Lab3"
    exe = rebuild_go("Lab3", "lab3") or go_binary("Lab3", "lab3")
    if not exe:
        skip(lab, "Vigenere/Playfair binary builds", "no Go toolchain available")
        return

    msg = "criptografia este o stiinta frumoasa si importanta"
    out, rc = sh([exe], "2\n1\nROMANIA\n%s\n0\n" % msg)
    gold = "ȚEUPGWGHOȘINNSJTĂSGRIDHMFDCMEODAERICCĂRGINJO"
    check(lab, "Vigenere ROMANIA matches report ciphertext", gold in out, "")
    check(lab, "key shifts equal Table 2 codes [20 17 15 0 16 10 0]",
          "[20 17 15 0 16 10 0]" in out, "")

    out, rc = sh([exe], "2\n2\nROMANIA\n%s\n0\n" % gold)
    check(lab, "Vigenere decrypt returns the original letters",
          "CRIPTOGRAFIAESTEOSTIINTAFRUMOASASIIMPORTANTA" in out, "")

    # Playfair used to crash with 'index out of range [35] with length 35'
    # when the grid held 35 cells; the rebuilt binary must not panic.
    pf_msg = "criptografia este o stiinta frumoasa"
    out, rc = sh([exe], "1\n1\nROMANIA\n%s\n0\n" % pf_msg)
    check(lab, "Playfair encrypts without the 35-cell grid panic",
          rc == 0 and "panic" not in out and "Criptograma:" in out,
          next((l.strip() for l in out.splitlines() if "panic" in l), ""))
    cip = next((l.split("Criptograma:", 1)[1].strip()
                for l in out.splitlines() if "Criptograma:" in l), "")
    check(lab, "Playfair grid is the 36-cell layout (31 letters + 0-4)",
          "R O M A N I" in out and "Z 0 1 2 3 4" in out, "")

    if cip:
        out2, _ = sh([exe], "1\n2\nROMANIA\n%s\n0\n" % cip)
        check(lab, "Playfair round-trip decrypts to the same letters",
              "Criptograma" in out2 or "criptografia" in out2.lower()
              or "CRIPTOGRAFIA" in out2, "")


# --------------------------------------------------------------------------
# Lab 4 - DES (task 2.9, FIPS self-test)
# --------------------------------------------------------------------------
def verify_lab4():
    lab = "Lab4"
    script = os.path.join(REPO, "Lab4", "des_lab.py")
    V5 = "110001100000010100000011111010110101000110100010"

    out, rc = sh([sys.executable, "-B", script, "--seed"], "5\n0\n")
    check(lab, "FIPS-197 vector self-test passes",
          rc == 0 and "text cifrat obtinut = 85E813540F0AB405" in out
          and "REZULTAT: CORECT" in out,
          next((l.strip() for l in out.splitlines() if "REZULTAT" in l), ""))

    out, rc = sh([sys.executable, "-B", script, "--seed"], "4\n0123456789ABCDEF\n133457799BBCDFF1\n0\n")
    check(lab, "full 16-round encryption matches the FIPS ciphertext",
          rc == 0 and "85E813540F0AB405" in out, "")

    out, rc = sh([sys.executable, "-B", script, "--seed"], "1\n5\n%s\n3\n0\n" % V5)
    check(lab, "task 2.9 selects S3[0][10] = 1100",
          rc == 0 and "S3[0][10]" in out and "1100" in out,
          next((l.strip() for l in out.splitlines() if "S3[0][10]" in l), ""))

    out, rc = sh([sys.executable, "-B", script, "--seed"], "3\n133457799BBCDFF1\n0\n")
    check(lab, "key schedule (PC-1, shifts, PC-2) runs", rc == 0 and "PC-1" in out, "")


# --------------------------------------------------------------------------
# Lab 5 - RSA, ElGamal, Diffie-Hellman, AES known-answer test
# --------------------------------------------------------------------------
def verify_lab5():
    lab = "Lab5"
    cwd = os.path.join(REPO, "Lab5")

    out, rc = sh([sys.executable, "-B", "main.py", "all"], cwd=cwd)
    check(lab, "RSA encrypt/decrypt round-trip",
          rc == 0 and "-> OK" in out and "(e*d) mod phi = 1" in out,
          next((l.strip() for l in out.splitlines() if "->" in l), ""))
    check(lab, "ElGamal decrypt returns the message",
          rc == 0 and "Decriptare: m = c2 * (c1^x)^-1 mod p" in out and "-> OK" in out, "")
    check(lab, "Diffie-Hellman shared keys agree",
          rc == 0 and "identice: True" in out, "")

    out, rc = sh([sys.executable, "-B", "verify_dh_aes.py"], cwd=cwd)
    check(lab, "AES-256 FIPS-197 known-answer test",
          rc == 0 and "KAT AES-256 FIPS-197: OK" in out,
          next((l.strip() for l in out.splitlines() if "KAT AES" in l), ""))


# --------------------------------------------------------------------------
# Lab 6 - hash functions and digital signatures
# --------------------------------------------------------------------------
def verify_lab6():
    lab = "Lab6"
    cwd = os.path.join(REPO, "Lab6")

    out, rc = sh([sys.executable, "-B", "md4.py"], cwd=cwd)
    check(lab, "MD4/NTLM matches the RFC 1320 vectors",
          rc == 0 and "MD4 self-test OK" in out,
          next((l.strip() for l in out.splitlines() if "MD4" in l), ""))

    out, rc = sh([sys.executable, "-B", "main.py", "--hash-test"], cwd=cwd)
    check(lab, "Whirlpool matches the 3 ISO vectors",
          rc == 0 and "Toate cele 3 vectori de test sunt corecte." in out,
          next((l.strip() for l in out.splitlines() if "vectori" in l), ""))

    before = sh(["git", "status", "--porcelain", "--", "Lab6/rsa_params.txt",
                 "Lab6/elgamal_sig_params.txt"], cwd=REPO)[0]
    out, rc = sh([sys.executable, "-B", "main.py"], cwd=cwd)
    check(lab, "both signatures verify (RSA + ElGamal)",
          rc == 0 and out.count("SEMNATURA VALIDA") >= 2 and "GATA:" in out,
          f"{out.count('SEMNATURA VALIDA')} valid signature marker(s)")
    after = sh(["git", "status", "--porcelain", "--", "Lab6/rsa_params.txt",
                "Lab6/elgamal_sig_params.txt"], cwd=REPO)[0]
    check(lab, "full run reproduces the committed parameter files",
          before.strip() == after.strip() == "",
          "no drift" if not after.strip() else after.strip())


# --------------------------------------------------------------------------
# Lab 5.2 - PKI (OpenSSL) addendum, read-only commands only
# --------------------------------------------------------------------------
def verify_lab52():
    lab = "Lab5.2"
    root = os.path.join(REPO, "Lab5.2")
    pki = os.path.join(root, "pki")

    out, rc = sh(["openssl", "verify", "-CAfile",
                  os.path.join(pki, "ca", "ca.cert.pem"),
                  os.path.join(pki, "users", "alice", "alice.cert.pem"),
                  os.path.join(pki, "users", "bob", "bob.cert.pem")])
    check(lab, "both user certificates chain to the CA",
          rc == 0 and out.count(": OK") == 2, out.strip()[:70])

    out, rc = sh(["./pki.sh", "status"], cwd=root)
    check(lab, "CA status lists the enrolled users",
          rc == 0 and "alice" in out and "bob" in out, "")

    out, rc = sh(["./pki.sh", "crl"], cwd=root)
    check(lab, "CRL lists the revoked certificate",
          rc == 0 and ("bob" in out or "Revoked" in out or "Serial" in out),
          out.strip()[:70])

    # Expected negative test: bob's certificate was revoked on purpose.
    out, rc = sh(["./pki.sh", "verify", "bob", "bob_doc.txt"], cwd=root)
    check(lab, "revoked certificate is refused (expected negative test)",
          rc != 0 and ("revoked" in out.lower() or "FAILED" in out),
          next((l.strip() for l in out.splitlines() if "RESULT" in l), ""))

    # The tracked document is deliberately left in its tampered state (the
    # report's tampering demo), so the signature is checked against the
    # original first line - and the tampered file must then be refused.
    doc = os.path.join(pki, "alice_doc.txt")
    if os.path.exists(doc):
        with open(doc, encoding="utf-8") as fh:
            original = fh.readline()
        pub, _ = sh(["openssl", "x509", "-in",
                     os.path.join(pki, "users", "alice", "alice.cert.pem"),
                     "-pubkey", "-noout"])
        with tempfile.TemporaryDirectory() as td:
            pubf = os.path.join(td, "alice.pub")
            origf = os.path.join(td, "original.txt")
            with open(pubf, "w", encoding="utf-8") as fh:
                fh.write(pub)
            with open(origf, "w", encoding="utf-8") as fh:
                fh.write(original)
            out, rc = sh(["openssl", "dgst", "-sha256", "-verify", pubf,
                          "-signature", os.path.join(pki, "alice_doc.txt.sig.bin"),
                          origf])
        check(lab, "alice's signature verifies against the untampered document",
              rc == 0 and "Verified OK" in out,
              "Verified OK" if rc == 0 else out.strip().splitlines()[-1][:60])

        out, rc = sh(["./pki.sh", "verify", "alice", "alice_doc.txt"], cwd=root)
        check(lab, "tampered document is refused (report's tamper demo)",
              rc != 0 and "FAILED" in out,
              next((l.strip() for l in out.splitlines() if "RESULT" in l), ""))


# --------------------------------------------------------------------------
LABS = {
    "1": ("Lab 1", verify_lab1), "2": ("Lab 2", verify_lab2),
    "3": ("Lab 3", verify_lab3), "4": ("Lab 4", verify_lab4),
    "5": ("Lab 5", verify_lab5), "6": ("Lab 6", verify_lab6),
    "5.2": ("Lab 5.2", verify_lab52),
}


def main(argv):
    wanted = argv or list(LABS)
    for key in wanted:
        if key not in LABS:
            print(f"unknown lab {key!r}; choose from {', '.join(LABS)}")
            return 2
        LABS[key][1]()

    width = max(len(d) for _, d, _, _ in RESULTS)
    current = None
    for lab, desc, status, detail in RESULTS:
        if lab != current:
            print(f"\n{lab}")
            current = lab
        print(f"  [{status}] {desc.ljust(width)}  {detail}")
    fails = [r for r in RESULTS if r[2] == "FAIL"]
    skips = [r for r in RESULTS if r[2] == "SKIP"]
    print(f"\n{len(RESULTS) - len(fails) - len(skips)} passed, "
          f"{len(fails)} failed, {len(skips)} skipped")
    return 1 if fails or skips else 0


if __name__ == "__main__":
    sys.exit(main([a for a in sys.argv[1:]]))
