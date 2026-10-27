#!/bin/bash
# Capture Lab 3 session: Vigenere (task 3.2) encrypt + decrypt, invalid keyword.
set -u
cd /home/user/Documents/GitHub/CS-labs/Lab3

KW="ROMANIA"
MSG="criptografia este o stiinta frumoasa si importanta"

echo '$ ./lab3                        # Sarcina 3.2: criptare Vigenere, k2 = ROMANIA'
CIP=$(printf '2\n1\n%s\n%s\n0\n' "$KW" "$MSG" | ./lab3 | sed -n 's/.*Criptograma: //p')
printf '2\n1\n%s\n%s\n0\n' "$KW" "$MSG" | ./lab3
echo

echo '$ ./lab3                        # Sarcina 3.2: decriptarea criptogramei (rotunjire exacta)'
printf '2\n2\n%s\n%s\n0\n' "$KW" "$CIP" | ./lab3
echo

echo '$ ./lab3                        # verificarea validarilor (cheie prea scurta / caractere invalide)'
printf '2\n1\nAB\nAB12\n%s\n%s\n0\n' "$KW" "$MSG" | ./lab3 | sed -n '1,12p'
