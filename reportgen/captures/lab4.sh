#!/bin/bash
# Capture Lab 4 session: DES round schedule, full encryption, task 2.9, S-boxes, FIPS test.
set -u
cd /home/user/Documents/GitHub/CS-labs/Lab4

PT=0123456789ABCDEF
KEY=133457799BBCDFF1
# K5 XOR E(R4), taken din rularea meniului 4 (reproducibila cu --seed)
V5=110001100000010100000011111010110101000110100010

echo '$ python3 des_lab.py --seed     # meniul 5: test de verificare (vectorul FIPS)'
printf '5\n0\n' | python3 des_lab.py --seed
echo

echo '$ python3 des_lab.py --seed     # meniul 3: programul de chei (PC-1, deplasari, PC-2)'
printf '3\n%s\n0\n' "$KEY" | python3 des_lab.py --seed
echo

echo '$ python3 des_lab.py --seed     # meniul 4: criptarea completa a unui bloc (16 runde)'
printf '4\n%s\n%s\n0\n' "$PT" "$KEY" | python3 des_lab.py --seed > lab4_encrypt_full.txt
tail -n +1 lab4_encrypt_full.txt | sed -n '/SARCIN/,/La revedere/p' | head -80
echo

echo '$ python3 des_lab.py --seed     # meniul 1: sarcina 2.9, i=5, j=3'
printf '1\n5\n%s\n3\n0\n' "$V5" | python3 des_lab.py --seed
echo

echo '$ python3 des_lab.py --seed     # meniul 2: cutia-S S3'
printf '2\n3\n0\n' | python3 des_lab.py --seed
