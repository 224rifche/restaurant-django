@echo off
REM Script de configuration des médias pour la production (Windows)

echo 🔧 Configuration des médias pour la production...
echo.

REM Vérifier si nous sommes dans le bon dossier
if not exist "manage.py" (
    echo ❌ Erreur: manage.py non trouvé. Exécutez ce script depuis la racine du projet Django.
    pause
    exit /b 1
)

REM Créer les dossiers nécessaires
echo 📁 Création des dossiers médias...
if not exist "media" mkdir media
if not exist "media\plats" mkdir media\plats
if not exist "media\justificatifs" mkdir media\justificatifs
if not exist "media\depenses" mkdir media\depenses
echo ✅ Dossiers créés avec succès

REM Vérifier les permissions
echo 🔐 Vérification des permissions...
icacls media /grant Everyone:(R) >nul 2>&1
echo ✅ Permissions configurées

REM Collecter les fichiers statiques
echo 📦 Collecte des fichiers statiques...
python manage.py collectstatic --noinput --clear
if %ERRORLEVEL% neq 0 (
    echo ❌ Erreur lors de la collecte des fichiers statiques
    pause
    exit /b 1
)
echo ✅ Fichiers statiques collectés

REM Créer un fichier de test
echo 🧪 Création d'un fichier de test...
echo Ceci est un fichier de test pour vérifier que les médias fonctionnent > media\test.txt
echo ✅ Fichier de test créé

REM Vérifier la configuration
echo 🔍 Diagnostic de la configuration...
python test_media.py
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Erreur lors du diagnostic, mais la configuration continue
)

REM Instructions pour la production
echo.
echo 🚀 Configuration terminée!
echo.
echo 📋 Instructions pour la production:
echo   1. Définissez DEBUG=False dans votre .env
echo   2. Définissez USE_S3=False (ou laissez par défaut)
echo   3. Redémarrez votre serveur
echo   4. Testez: http://votre-domaine.com/diagnostic/media/
echo   5. Testez: http://votre-domaine.com/media/test.txt
echo.
echo 🌐 En développement: http://127.0.0.1:8000/diagnostic/media/
echo.
echo ✅ Les médias devraient maintenant fonctionner en production!
echo.
pause
