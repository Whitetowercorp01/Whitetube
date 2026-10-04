@echo off
chcp 65001 >nul
title WhiteTube - Descargador de Música

echo ======================================================
echo           Iniciando WhiteTube...
echo ======================================================

:: Verificar lanzador py o python
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYCMD=py
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PYCMD=python
    ) else (
        echo [ERROR] No se encontró Python instalado en tu computadora.
        echo Por favor instala Python desde https://www.python.org/
        pause
        exit /b 1
    )
)

:: Verificar e instalar dependencias si faltan
echo Comprobando dependencias...
%PYCMD% -c "import yt_dlp, imageio_ffmpeg, mutagen, PIL" >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando librerías necesarias (yt-dlp, imageio-ffmpeg, mutagen, pillow)...
    %PYCMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Ocurrió un error al instalar las dependencias.
        pause
        exit /b 1
    )
)

:: Iniciar la aplicación
echo Abriendo WhiteTube...
%PYCMD% whitetube.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrió un error al ejecutar WhiteTube.
    pause
)