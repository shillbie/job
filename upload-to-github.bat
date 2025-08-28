@echo off
echo Mengupload proyek kasir ke GitHub...

REM Initialize Git repository
git init

REM Add semua file
git add .

REM Commit pertama
git commit -m "Initial commit - Aplikasi Kasir Android"

REM Set branch utama
git branch -M main

REM Tambahkan remote origin (ganti URL dengan repository Anda)
echo.
echo PENTING: Ganti URL berikut dengan URL repository GitHub Anda!
echo Contoh: git remote add origin https://github.com/username/kasir-app.git
echo.
pause

REM Push ke GitHub
git push -u origin main

echo.
echo Upload selesai! Cek GitHub Actions untuk build APK.
pause
