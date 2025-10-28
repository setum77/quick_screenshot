@echo off
chcp 65001 >nul
title Cервис скриншотов

echo Проверка необходимых Python-пакетов...

:: Список требуемых пакетов (имена для pip)
set "PACKAGES=keyboard Pillow pystray"

:: Проверяем и устанавливаем каждый пакет по очереди
for %%P in (%PACKAGES%) do (
    echo Проверка пакета %%P...
    python -c "import %%P" >nul 2>&1
    if errorlevel 1 (
        echo Пакет %%P не найден. Установка...
        pip install %%P
        if errorlevel 1 (
            echo Ошибка: не удалось установить пакет %%P.
            pause
            exit /b 1
        )
    )
)

echo Все пакеты установлены.
echo Запуск сервиса скриншотов...
python quick_screenshot.py

pause