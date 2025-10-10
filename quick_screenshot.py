# C:\cmd\quick_screenshot.py
"""
Сервис для быстрого создания скриншотов активного окна с помощью горячих клавиш.
- Горячая клавиша для скриншота: Alt + PrtSc    
- Горячая клавиша для выхода: Ctrl + Alt + Q
- Папка для сохранения скриншотов: screenshots_folder - по умолчанию "Мои рисунки\Скриншоты" или можно указать свой путь
- Формат файлов: PNG
- Иконка в системном трее для управления сервисом
- Требуются библиотеки: pyautogui, keyboard, pystray, pillow, plyer, pywin32
"""

import os
import sys
import time
import threading
import warnings
from datetime import datetime
from pathlib import Path

import keyboard
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Подавляем предупреждения
warnings.filterwarnings("ignore")


class ScreenshotService:
    def __init__(self, folder):
        self.folder = folder
        self.running = False
        self.registered_hotkey = None
        self.tray_icon = None
        self.keyboard_thread = None
        os.makedirs(self.folder, exist_ok=True)
        
    def _get_window_rect(self):
        """Получить координаты активного окна"""
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        return win32gui.GetWindowRect(hwnd)
    
    def _create_bitmap_screenshot(self, left, top, width, height):
        """Создать скриншот через Win32 API"""
        import win32gui
        import win32ui
        import win32con
        
        hwndDC = win32gui.GetWindowDC(0)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        
        result = saveDC.BitBlt(
            (0, 0), 
            (width, height), 
            mfcDC, 
            (left, top),
            win32con.SRCCOPY
        )
        
        if result is None:
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(0, hwndDC)
            
            return im
        return None

    def get_active_window_screenshot(self):
        """Упрощенный метод с использованием GetSystemMetrics для DPI"""
        try:
            import ctypes
            
            # Устанавливаем DPI awareness
            ctypes.windll.user32.SetProcessDPIAware()
            
            rect = self._get_window_rect()
            if not rect:
                print("❌ Не найдено активное окно")
                return None
            
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            print(f"📐 Координаты окна: ({left}, {top}, {right}, {bottom})")
            print(f"📏 Размеры окна: {width}x{height}")
            
            screenshot = self._create_bitmap_screenshot(left, top, width, height)
            if screenshot:
                return screenshot
                
            print("❌ Ошибка при захвате изображения окна")
            return None
                
        except Exception as e:
            print(f"❌ Ошибка Win32 метода: {e}")
            return self._simple_dpi_screenshot()

    def _simple_dpi_screenshot(self):
        """Самый простой метод с pyautogui"""
        try:
            import pyautogui
            import ctypes
            
            # Включаем DPI awareness
            ctypes.windll.user32.SetProcessDPIAware()
            
            rect = self._get_window_rect()
            if not rect:
                return None
            
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            print(f"📐 PyAutoGUI метод: {width}x{height}")
            
            return pyautogui.screenshot(region=(left, top, width, height))
            
        except Exception as e:
            print(f"❌ Ошибка PyAutoGUI: {e}")
            return self._fallback_screenshot()
    
    def _fallback_screenshot(self):
        """Резервный метод через pyautogui - захват полного окна"""
        try:
            import pyautogui
            
            rect = self._get_window_rect()
            if not rect:
                return None
            
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            print(f"📐 Резервный метод (полное окно): {width}x{height}")
            
            return pyautogui.screenshot(region=(left, top, width, height))
            
        except Exception as e:
            print(f"❌ Ошибка резервного метода: {e}")
            return None
    
    def _get_window_info(self):
        """Получить информацию об активном окне"""
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            rect = self._get_window_rect()
            if rect:
                left, top, right, bottom = rect
                width = right - left
                height = bottom - top
                print(f"   📋 Активное окно: {window_title}")
                print(f"   📏 Размеры: {width}x{height}")
                
        except Exception as e:
            print(f"   ℹ️  Не удалось получить информацию об окне: {e}")
    
    def take_screenshot(self):
        """Сделать скриншот активного окна"""
        filename = f"window_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        full_path = os.path.join(self.folder, filename)
        
        try:
            print("📸 Захватываем полное активное окно...")
            
            # Получаем информацию об активном окне перед скриншотом
            self._get_window_info()
            
            screenshot = self.get_active_window_screenshot()
            
            if screenshot:
                screenshot.save(full_path)
                print(f"✅ Скриншот полного окна сохранен: {filename}")
                self.show_notification("Скриншот сохранен", f"Полное окно: {filename}")
            else:
                print("❌ Не удалось создать скриншот активного окна")
                self.show_notification("Ошибка", "Не удалось создать скриншот активного окна")
                
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            self.show_notification("Ошибка", f"Не удалось сохранить скриншот: {e}")
    
    def show_notification(self, title, message):
        """Современные уведомления через plyer"""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                timeout=2,
                app_name="Сервис скриншотов окон"
            )
        except ImportError:
            print(f"💡 {title}: {message}")
    
    def _create_tray_image(self):
        """Создать изображение для иконки в трее"""
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white', outline='black')
        return image
    
    def create_tray_icon(self):
        """Создать иконку в системном трее"""
        image = self._create_tray_image()
        
        menu = Menu(
            MenuItem('Сделать скриншот полного окна (Alt + Print Screen)', self.take_screenshot),
            MenuItem('Открыть папку со скриншотами', self.open_folder),
            MenuItem('Выход', self.exit_app)
        )
        
        self.tray_icon = Icon("screenshot_service", image, "Сервис скриншотов активных окон", menu)
        return self.tray_icon
    
    def open_folder(self, icon=None, item=None):
        """Открыть папку со скриншотами"""
        try:
            os.startfile(self.folder)
            print(f"📁 Открыта папка: {self.folder}")
        except Exception as e:
            print(f"❌ Не удалось открыть папку: {e}")
    
    def exit_app(self, icon=None, item=None):
        """Выход из приложения"""
        print("🛑 Завершение работы сервиса...")
        self.running = False
        
        # Останавливаем горячие клавиши
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # Останавливаем иконку в трее
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        
        # Даем время на очистку ресурсов
        time.sleep(0.5)
        print("👋 Сервис остановлен")
        os._exit(0)
    
    def _register_hotkey_combinations(self, combinations, callback):
        """Зарегистрировать комбинации горячих клавиш"""
        for combo in combinations:
            try:
                keyboard.add_hotkey(combo, callback)
                print(f"✅ Зарегистрирована горячая клавиша: {combo}")
                return combo
            except Exception as e:
                print(f"❌ Не удалось зарегистрировать {combo}: {e}")
        return None
    
    def keyboard_listener(self):
        """Поток для прослушивания горячих клавиш"""
        # Основные комбинации для Print Screen
        main_combinations = [
            'alt+print screen',
            'alt+printscreen', 
            'alt+prtsc',
        ]
        
        # Альтернативные комбинации
        alt_combinations = ['ctrl+alt+a', 'f11', 'ctrl+f11']
        
        # Регистрируем основную горячую клавишу
        self.registered_hotkey = self._register_hotkey_combinations(main_combinations, self.take_screenshot)
        
        if not self.registered_hotkey:
            print("⚠️  Пробуем альтернативные комбинации...")
            self.registered_hotkey = self._register_hotkey_combinations(alt_combinations, self.take_screenshot)
        
        # Регистрируем горячую клавишу для выхода
        keyboard.add_hotkey('ctrl+alt+q', self.exit_app)
        
        print("\n🎹 Горячие клавиши:")
        if self.registered_hotkey:
            print(f"   {self.registered_hotkey} - скриншот полного активного окна")
        else:
            print("   ❌ Не удалось зарегистрировать горячие клавиши")
        print("   Ctrl + Alt + Q - выход")
        print("─" * 50)
        
        # Простой цикл ожидания вместо keyboard.wait()
        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.exit_app()
    
    def start_tray_icon(self):
        """Запустить иконку в трее в отдельном потоке"""
        try:
            if not self.tray_icon:
                self.create_tray_icon()
            self.tray_icon.run()
        except Exception as e:
            print(f"❌ Ошибка иконки в трее: {e}")
            # Не завершаем программу при ошибке иконки
    
    def start(self):
        """Запустить сервис"""
        self.running = True
        
        print("🚀 Сервис скриншотов полных окон запущен!")
        print(f"📁 Папка для скриншотов: {self.folder}")
        print("📍 Иконка в системном трее")
        print("─" * 50)
        
        # Запускаем поток с горячими клавишами
        self.keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.keyboard_thread.start()
        
        # Запускаем иконку в трее в главном потоке
        # Это важно для избежания множественных иконок
        try:
            self.start_tray_icon()
        except Exception as e:
            print(f"❌ Ошибка создания иконки в трее: {e}")
            print("💡 Сервис продолжит работу в фоновом режиме")
            
            # Если иконка не работает, ждем в основном потоке
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.exit_app()


def get_my_pictures_path():
    """Получаем путь к папке 'Мои рисунки'"""
    try:
        user_profile = os.environ['USERPROFILE']
        pictures_path = os.path.join(user_profile, 'Pictures')
        
        if os.path.exists(pictures_path):
            print('📁 Путь к папке "Мои рисунки":', pictures_path)
            return pictures_path
        else:
            pictures_path = Path.home() / 'Pictures'
            return str(pictures_path)
            
    except Exception as e:
        print(f"Ошибка получения пути: {e}")
        return os.getcwd()


# Создаем папку для скриншотов в 'Мои рисунки'
pictures_path = get_my_pictures_path()
screenshots_folder = os.path.join(pictures_path, 'Скриншоты')

# Или используем фиксированный путь, закомменитровав две строки выше
# screenshots_folder = r"d:\my_folder\pic\screenshot\"


# Создаем папку если не существует
os.makedirs(screenshots_folder, exist_ok=True)

if __name__ == "__main__":
    service = ScreenshotService(screenshots_folder)
    service.start()