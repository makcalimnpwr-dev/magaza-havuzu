@echo off
echo GitHub'a push etme script'i
echo.
echo 1. GitHub'da repository oluşturduktan sonra
echo 2. YOUR_USERNAME ve REPO_NAME'i değiştirin
echo 3. Bu dosyayı çalıştırın
echo.

git init
git add .
git commit -m "Render deployment için hazırlandı"

echo.
echo GitHub repository URL'inizi girin (örn: https://github.com/kullaniciadi/magaza-yonetim-sistemi.git)
set /p REPO_URL="Repository URL: "

git remote add origin %REPO_URL%
git branch -M main
git push -u origin main

echo.
echo Tamamlandi! GitHub'a push edildi.
pause


