#!/bin/bash
# Capture Lab 2 session: frequency analysis + iterative attack on V20.
set -u
cd /home/user/Documents/GitHub/CS-labs/Lab2

CIP=$(tr '\n' ' ' < v20_cipher.txt)

echo '$ ./lab2                        # optiunea 1: exemplu de criptograma Caesar (k = 11)'
printf '1\n11\natelierul de criptografie\n0\n' | ./lab2
echo

echo '$ ./lab2                        # optiunea 2: atacul asupra criptogramei V20 (profil englez)'
{
  echo 2
  echo en
  echo "$CIP"
  # refinari manuale: litera gresita automat -> litera corecta (13 corectii)
  echo G=N
  echo N=O
  echo I=R
  echo P=S
  echo Q=H
  echo C=F
  echo D=U
  echo J=G
  echo Z=M
  echo A=B
  echo R=W
  echo B=Q
  echo Y=X
  echo tab
  echo text
  echo gata
  echo 0
} | ./lab2 > lab2_attack_full.txt
wc -l lab2_attack_full.txt
