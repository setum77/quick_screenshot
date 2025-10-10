# quick_screenshot

quick_screenshot - утилита создания скриншотов активного окна в OS Windows

### Возможности

- Создание скриншота активного окна (не всего экрана) с помощью комбинации клавиш Alt + PrtSc (print screen)
- Папка для сохранения скриншотов: по умолчанию "Мои рисунки\Скриншоты" или можно указать свой путь
- Иконка в системном трее для управления сервисом

### Установка

1. Установить Python
2. На диске C создать папку "cmd" (c:\cmd\), можно любое название - просто я простые утилиты складываю в папку cmd
3. Записать в нее quick_screenshot.py
4. Установить зависимости

```bash
pip install pyautogui keyboard pystray pillow plyer pywin32
```

5. Создать в этой же папке бат файл `start_screenshot_service.bat`

```bash
@echo off

echo Запуск сервиса скриншотов...

python C:\cmd\quick_screenshot.py

pause
```

6. Создать на рабочем столе ярлык для `start_screenshot_service.bat`

### Запуск

1. Запускаем ярлык, в трее появится синий значок утилиты, и окно с выводом рабочей информации. Это окно не закрываем пока не закончим работать со скриншотами
2. Делаем скриншоты Alt + PrtSc
3. Щелкнув ПКМ по иконке в трее можно:
   1. открыть папку со скриншотами
   2. закрыть утилиту

### Если нужно изменить папку для сохранения скриншотов

1. Открыть quick_screenshot.py в редакторе
2. Найти строчки

```python
# Создаем папку для скриншотов в 'Мои рисунки'

pictures_path = get_my_pictures_path()

screenshots_folder = os.path.join(pictures_path, 'Скриншоты')


# Или используем фиксированный путь, закомменитровав две строки выше

# screenshots_folder = r"d:\my_folder\pic\screenshot\"
```

3. Комментируем строки

```python
# pictures_path = get_my_pictures_path()

# screenshots_folder = os.path.join(pictures_path, 'Скриншоты')
```

4. Расcкомментируем строку

```python
screenshots_folder = r"d:\my_folder\pic\screenshot\"
```

5. Вместо d:\my_folder\pic\screenshot\ подставляем свой путь к папке для сохранения скриншотов
