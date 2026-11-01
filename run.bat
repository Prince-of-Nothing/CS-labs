@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title CS Labs - Dinu Plesu, FAF-241

set "PY="
py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
    python -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY=python"
)
if not defined PY (
    echo.
    echo Python 3 was not found.
    echo Install it from https://www.python.org/downloads/ and run this file again.
    echo.
    pause
    exit /b 1
)

:menu
cls
echo ======================================================================
echo   Cryptography and Security - Laboratory Works
echo   Dinu Plesu, FAF-241 - Technical University of Moldova
echo ======================================================================
echo.
echo   1. Lab 1 - Caesar cipher (tasks 1.1 and 1.2)
echo   2. Lab 2 - Cryptanalysis of monoalphabetic ciphers (variant V20)
echo   3. Lab 3 - Vigenere (task 3.2) / Playfair (task 3.1 bonus)
echo   4. Lab 4 - DES (task 2.9, 20 mod 11 = 9)
echo   5. Lab 5 - RSA, ElGamal, Diffie-Hellman + AES-256
echo   6. Lab 6 - Hashes and signatures (RSA/NTLM, ElGamal/Whirlpool)
echo   7. Lab 5.2 - PKI with OpenSSL and digital signatures
echo.
echo   8. Verify every laboratory work (reportgen/verify.py)
echo   9. Rebuild the Word reports (reportgen/build_reports.py)
echo   0. Exit
echo.
choice /c 1234567890 /n /m "Choose an option: "
set "OPT=%errorlevel%"
if "%OPT%"=="255" goto end
if "%OPT%"=="1" goto lab1
if "%OPT%"=="2" goto lab2
if "%OPT%"=="3" goto lab3
if "%OPT%"=="4" goto lab4
if "%OPT%"=="5" goto lab5
if "%OPT%"=="6" goto lab6
if "%OPT%"=="7" goto lab52
if "%OPT%"=="8" goto verify
if "%OPT%"=="9" goto reports
if "%OPT%"=="10" goto end
goto menu

:lab1
if exist "Lab1\caesar.exe" (
    pushd "Lab1"
    caesar.exe
    popd
) else (
    where go >nul 2>nul
    if errorlevel 1 (
        echo.
        echo Lab1\caesar.exe is missing and Go is not installed.
        echo Install Go from https://go.dev/dl/ or restore the executable.
    ) else (
        pushd "Lab1"
        go run .
        popd
    )
)
pause
goto menu

:lab2
if exist "Lab2\freq.exe" (
    pushd "Lab2"
    freq.exe
    popd
) else (
    where go >nul 2>nul
    if errorlevel 1 (
        echo.
        echo Lab2\freq.exe is missing and Go is not installed.
        echo Install Go from https://go.dev/dl/ or restore the executable.
    ) else (
        pushd "Lab2"
        go run .
        popd
    )
)
pause
goto menu

:lab3
if exist "Lab3\lab3.exe" (
    pushd "Lab3"
    lab3.exe
    popd
) else (
    where go >nul 2>nul
    if errorlevel 1 (
        echo.
        echo Lab3\lab3.exe is missing and Go is not installed.
        echo Install Go from https://go.dev/dl/ or restore the executable.
    ) else (
        pushd "Lab3"
        go run .
        popd
    )
)
pause
goto menu

:lab4
%PY% "Lab4\des_lab.py" --seed
pause
goto menu

:lab5
pushd "Lab5"
%PY% main.py all
echo.
%PY% verify_dh_aes.py
popd
pause
goto menu

:lab6
call :ensure_whirlpool
if errorlevel 1 goto menu
pushd "Lab6"
echo.
echo --- Whirlpool known-answer test ---
%PY% main.py --hash-test
echo.
echo --- RSA/NTLM and ElGamal/Whirlpool signatures ---
%PY% main.py
popd
pause
goto menu

:lab52
set "BASH="
if exist "C:\Program Files\Git\bin\bash.exe" set "BASH=C:\Program Files\Git\bin\bash.exe"
if not defined BASH (
    where bash >nul 2>nul
    if not errorlevel 1 set "BASH=bash"
)
if not defined BASH (
    echo.
    echo Bash/OpenSSL was not found. Install Git for Windows:
    echo https://git-scm.com/download/win
    echo.
    pause
    goto menu
)
cls
echo ======================================================================
echo   Lab 5.2 - PKI with OpenSSL
echo ======================================================================
echo.
echo   1. Show PKI status
echo   2. Show the CRL
echo   3. Verify bob (revoked certificate - expected to fail)
echo   4. Verify alice (tampered document - expected to fail)
echo   5. Show all pki.sh commands
echo   0. Back
echo.
choice /c 123450 /n /m "Choose an option: "
set "OPT=%errorlevel%"
if "%OPT%"=="255" goto end
if "%OPT%"=="1" "%BASH%" "Lab5.2/pki.sh" status
if "%OPT%"=="2" "%BASH%" "Lab5.2/pki.sh" crl
if "%OPT%"=="3" "%BASH%" "Lab5.2/pki.sh" verify bob bob_doc.txt
if "%OPT%"=="4" "%BASH%" "Lab5.2/pki.sh" verify alice alice_doc.txt
if "%OPT%"=="5" "%BASH%" "Lab5.2/pki.sh"
if "%OPT%"=="6" goto menu
pause
goto menu

:verify
%PY% reportgen\verify.py
pause
goto menu

:reports
call :ensure_docx
if errorlevel 1 goto menu
echo.
echo WARNING: this rebuilds all six reports from build_reports.py.
echo The committed Lab 1, 3, 4, 5 and 6 contain hand edits that are NOT
echo in the generator. Rebuilding will replace those edits with the
echo earlier generated layout.
choice /c yn /n /m "Continue? [y/n] "
if errorlevel 2 goto menu
%PY% reportgen\build_reports.py
pause
goto menu

:ensure_whirlpool
%PY% -c "import whirlpool" >nul 2>nul && exit /b 0
echo.
echo Lab 6 needs the Python package "whirlpool".
choice /c yn /n /m "Install it now with pip? [y/n] "
if errorlevel 2 (
    echo Install it manually with: %PY% -m pip install whirlpool
    exit /b 1
)
%PY% -m pip install whirlpool
%PY% -c "import whirlpool" >nul 2>nul
if errorlevel 1 (
    echo.
    echo The installation failed. Run: %PY% -m pip install whirlpool
    exit /b 1
)
exit /b 0

:ensure_docx
%PY% -c "import docx, PIL" >nul 2>nul && exit /b 0
echo.
echo Rebuilding the reports needs python-docx and Pillow.
choice /c yn /n /m "Install them now with pip? [y/n] "
if errorlevel 2 (
    echo Install them manually with: %PY% -m pip install python-docx Pillow
    exit /b 1
)
%PY% -m pip install python-docx Pillow
%PY% -c "import docx, PIL" >nul 2>nul
if errorlevel 1 (
    echo.
    echo The installation failed. Run: %PY% -m pip install python-docx Pillow
    exit /b 1
)
exit /b 0

:end
echo.
echo Bye.
endlocal
