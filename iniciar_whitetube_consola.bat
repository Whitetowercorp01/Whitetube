@echo off
chcp 65001 >nul
title WhiteTube (Modo Consola)

where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYCMD=py
) else (
    set PYCMD=python
)

%PYCMD% whitetube.py --cli
pause