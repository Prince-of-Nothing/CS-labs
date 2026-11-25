#!/bin/bash
# Capture Lab 1 session: Caesar encrypt/decrypt, error handling, keyword cipher.
set -u
cd /home/user/Documents/GitHub/CS-labs/Lab1

MSG="criptografia este o stiinta frumoasa"
KWMSG="criptografia pe intelesul tuturor"

echo '$ ./caesar                      # Sarcina 1.1: cifrare cu cheia k = 7'
printf '1\n1\n7\n%s\n' "$MSG" | ./caesar
echo

echo '$ ./caesar                      # Sarcina 1.1: decriptare (intoarcerea transformarii)'
CIP=$(printf '1\n1\n7\n%s\n' "$MSG" | ./caesar | sed -n 's/.*Ciphertext: //p')
printf '1\n2\n7\n%s\n' "$CIP" | ./caesar
echo

echo '$ ./caesar                      # verificarea validarilor de intrare'
printf '1\n1\n0\n31\n7\nHELLO2\n%s\n' "$MSG" | ./caesar
echo

echo '$ ./caesar                      # Sarcina 1.2: cifrul cu cuvant-cheie (ROMANIA), k = 3'
printf '2\n1\n3\nROMANIA\n%s\n' "$KWMSG" | ./caesar
echo

echo '$ ./caesar                      # Sarcina 1.2: decriptarea cu acelasi cuvant-cheie'
KCIP=$(printf '2\n1\n3\nROMANIA\n%s\n' "$KWMSG" | ./caesar | sed -n 's/.*Ciphertext: //p')
printf '2\n2\n3\nROMANIA\n%s\n' "$KCIP" | ./caesar
echo

echo '$ ./caesar                      # Sarcina 1.2: verificarea cuvantului-cheie'
printf '2\n1\n3\nabece\nchei!\nROMANIA\ntest\n' | ./caesar
