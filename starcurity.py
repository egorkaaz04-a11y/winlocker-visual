import pygame
import sys
import os
import urllib.request
import tempfile
import subprocess

# Инициализация
pygame.init()

# Информация о дисплее
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Создаём полноэкранное окно поверх всех
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
pygame.display.set_caption("starcurity beta")

# Цвета (только чёрный, белый и серые оттенки)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_50 = (50, 50, 50)
GRAY_80 = (80, 80, 80)
GRAY_120 = (120, 120, 120)
GREEN = (0, 255, 0)
RED = (255, 50, 50)

def download_minecraft_font():
    """Скачивает шрифт Minecraft на время работы программы"""
    font_url = "https://github.com/IdreesInc/Monocraft/raw/main/fonts/ttf/Monocraft.ttf"
    font_path = os.path.join(tempfile.gettempdir(), "Monocraft.ttf")
    
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_url, font_path)
        except:
            return None
    return font_path

def load_minecraft_font(size):
    """Загружает шрифт Minecraft или fallback шрифт"""
    font_path = download_minecraft_font()
    if font_path and os.path.exists(font_path):
        try:
            return pygame.font.Font(font_path, size)
        except:
            pass
    # Fallback на моноширинный шрифт
    return pygame.font.SysFont("consolas", size, bold=False)

def reboot_system():
    """Перезагружает компьютер"""
    try:
        if sys.platform == "win32":
            # Windows
            subprocess.run(["shutdown", "/r", "/t", "0"], capture_output=True)
        elif sys.platform == "linux":
            # Linux
            subprocess.run(["sudo", "reboot"], capture_output=True)
        elif sys.platform == "darwin":
            # macOS
            subprocess.run(["sudo", "shutdown", "-r", "now"], capture_output=True)
    except:
        pass

# Размеры шрифтов
FONT_SIZE_TITLE = int(HEIGHT * 0.04)
FONT_SIZE_SUBTITLE = int(HEIGHT * 0.018)
FONT_SIZE_MESSAGE = int(HEIGHT * 0.022)
FONT_SIZE_WARNING = int(HEIGHT * 0.02)
FONT_SIZE_INSTR = int(HEIGHT * 0.016)
FONT_SIZE_INPUT = int(HEIGHT * 0.025)
FONT_SIZE_FOOTER = int(HEIGHT * 0.012)

font_title = load_minecraft_font(FONT_SIZE_TITLE)
font_subtitle = load_minecraft_font(FONT_SIZE_SUBTITLE)
font_message = load_minecraft_font(FONT_SIZE_MESSAGE)
font_warning = load_minecraft_font(FONT_SIZE_WARNING)
font_instr = load_minecraft_font(FONT_SIZE_INSTR)
font_input = load_minecraft_font(FONT_SIZE_INPUT)
font_footer = load_minecraft_font(FONT_SIZE_FOOTER)

clock = pygame.time.Clock()

# Анимационные переменные
cursor_blink = 0
blink_direction = 1
message_alpha = 0
input_active = False

# Состояние блокировки
locked = True

# Пароль (в нижнем регистре для удобства ввода)
PASSWORD = "zyv corporation"
input_text = ""
error_message = ""
error_message_timer = 0
failed_attempts = 0

# Анимированные сообщения (появляются последовательно)
messages = [
    "> initializing security protocol...",
    "> system integrity check: FAILED",
    "> your files have been encrypted",
    "> this machine is under my control",
    "> do not attempt to bypass the lock",
    "> hello im sorry your system is already locked"
]

current_message_index = 0
message_chars_displayed = 0
message_animation_speed = 2
message_pause_timer = 0
message_pause_duration = 30  # кадров паузы между сообщениями

def draw_text(text, font, color, x, y, center=True):
    """Универсальная функция для рисования текста"""
    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    screen.blit(text_surf, text_rect)

def draw_lock_icon(x, y, size):
    """Рисует минималистичный замок (только контур)"""
    # Дужка замка
    pygame.draw.arc(screen, WHITE, (x - size//2, y - size//2 - size//3, size, size), 
                    3.14, 6.28, max(2, size//15))
    # Корпус
    pygame.draw.rect(screen, WHITE, (x - size//2, y - size//3, size, int(size * 0.7)), 
                     max(2, size//20), border_radius=size//10)
    # Замочная скважина
    pygame.draw.circle(screen, BLACK, (x, y), size//6)
    pygame.draw.rect(screen, BLACK, (x - size//10, y + size//20, size//5, size//8))

def show_reboot_warning():
    """Показывает предупреждение о перезагрузке"""
    for alpha in range(0, 255, 10):
        screen.fill(BLACK)
        warning_lines = [
            "> WARNING <",
            "",
            "3 incorrect password attempts detected.",
            "System will reboot in 3 seconds.",
            "",
            "This is your final warning."
        ]
        
        y_offset = HEIGHT//2 - 100
        for line in warning_lines:
            if line:
                line_surf = font_warning.render(line, True, RED)
                line_surf.set_alpha(alpha)
                line_rect = line_surf.get_rect(center=(WIDTH//2, y_offset))
                screen.blit(line_surf, line_rect)
            y_offset += 40
        
        pygame.display.flip()
        pygame.time.wait(15)
    
    pygame.time.wait(3000)

def show_incorrect_message():
    """Показывает сообщение о неправильном пароле"""
    msg_font = load_minecraft_font(FONT_SIZE_INSTR)
    remaining = 3 - failed_attempts
    for alpha in range(0, 255, 20):
        screen.fill(BLACK)
        # Перерисовываем основной экран
        draw_lock_icon(60, 60, 30)
        draw_text("starcurity beta", font_title, WHITE, WIDTH//2, HEIGHT//2 - 80)
        
        msg_text = f"> access denied <"
        msg_surf = msg_font.render(msg_text, True, RED)
        msg_surf.set_alpha(alpha)
        msg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(msg_surf, msg_rect)
        
        attempts_text = f"attempts remaining: {remaining}"
        att_surf = msg_font.render(attempts_text, True, GRAY_80)
        att_surf.set_alpha(alpha)
        att_rect = att_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        screen.blit(att_surf, att_rect)
        
        pygame.display.flip()
        pygame.time.wait(10)
    
    pygame.time.wait(1000)

def show_unlock_message():
    """Показывает сообщение о разблокировке"""
    msg_font = load_minecraft_font(FONT_SIZE_INSTR)
    for alpha in range(0, 255, 15):
        screen.fill(BLACK)
        msg_surf = msg_font.render("> system unlocked <", True, GREEN)
        msg_surf.set_alpha(alpha)
        msg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(msg_surf, msg_rect)
        pygame.display.flip()
        pygame.time.wait(10)
    
    pygame.time.wait(800)

# Основной цикл
running = True
while running:
    # Анимация курсора (моргание)
    cursor_blink += 0.1 * blink_direction
    if cursor_blink >= 1:
        cursor_blink = 1
        blink_direction = -1
    elif cursor_blink <= 0:
        cursor_blink = 0
        blink_direction = 1
    
    # Анимация появления сообщений
    if message_pause_timer > 0:
        message_pause_timer -= 1
    elif not input_active and current_message_index < len(messages):
        if message_chars_displayed < len(messages[current_message_index]):
            message_chars_displayed = min(message_chars_displayed + message_animation_speed, len(messages[current_message_index]))
            pygame.time.wait(20)
        else:
            # Переход к следующему сообщению
            current_message_index += 1
            message_chars_displayed = 0
            if current_message_index < len(messages):
                message_pause_timer = message_pause_duration
    
    if current_message_index >= len(messages):
        input_active = True
    
    # Обновление таймера ошибки
    if error_message_timer > 0:
        error_message_timer -= 1
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if not locked:
                running = False
        
        elif event.type == pygame.KEYDOWN and input_active and locked:
            if event.key == pygame.K_RETURN:
                # Проверка пароля
                if input_text.lower() == PASSWORD.lower():
                    locked = False
                    show_unlock_message()
                    running = False
                else:
                    failed_attempts += 1
                    error_message = "> invalid password <"
                    error_message_timer = 120
                    show_incorrect_message()
                    
                    if failed_attempts >= 3:
                        show_reboot_warning()
                        reboot_system()
                        running = False
                    
                    input_text = ""
            
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            
            elif event.key == pygame.K_ESCAPE:
                pass  # Игнорируем ESC
            
            else:
                if len(input_text) < 50:
                    input_text += event.unicode
        
        # Блокируем ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and locked:
            pass
    
    if locked:
        # Чёрный фон
        screen.fill(BLACK)
        
        # Тонкая рамка по краям
        border_width = 1
        pygame.draw.rect(screen, GRAY_50, (border_width, border_width, WIDTH - 2*border_width, HEIGHT - 2*border_width), border_width)
        
        # === Верхняя строка (терминальная) ===
        top_text = f"starcurity@beta:~$ _"
        if cursor_blink > 0.5:
            top_text = "starcurity@beta:~$  "
        draw_text(top_text, font_footer, GRAY_80, 15, 15, center=False)
        
        # === Замок ===
        draw_lock_icon(60, 60, 30)
        
        # === Заголовок ===
        draw_text("starcurity beta", font_title, WHITE, WIDTH//2, HEIGHT//2 - 120)
        
        # === Анимированные сообщения ===
        y_offset = HEIGHT//2 - 80
        
        # Показываем уже завершённые сообщения
        for i in range(current_message_index):
            draw_text(messages[i], font_message, GRAY_80, WIDTH//2, y_offset)
            y_offset += 35
        
        # Показываем текущее анимированное сообщение
        if current_message_index < len(messages):
            displayed_msg = messages[current_message_index][:message_chars_displayed]
            if message_chars_displayed < len(messages[current_message_index]) and cursor_blink > 0.5:
                displayed_msg += "_"
            draw_text(displayed_msg, font_message, WHITE, WIDTH//2, y_offset)
            y_offset += 35
        
        # === Поле ввода пароля (появляется после всех сообщений) ===
        if input_active:
            # Разделительная линия
            line_width = min(400, WIDTH // 2)
            pygame.draw.line(screen, GRAY_50, (WIDTH//2 - line_width//2, y_offset + 10), 
                            (WIDTH//2 + line_width//2, y_offset + 10), 1)
            
            # Приглашение к вводу
            draw_text("enter password to unlock:", font_instr, GRAY_80, WIDTH//2, y_offset + 40)
            
            # Поле ввода
            display_text = input_text
            if cursor_blink > 0.5:
                display_text += "_"
            draw_text(display_text, font_input, WHITE, WIDTH//2, y_offset + 80)
            
            # Счётчик попыток
            attempts_left = 3 - failed_attempts
            attempts_text = f"attempts remaining: {attempts_left}"
            if attempts_left <= 1:
                draw_text(attempts_text, font_instr, RED, WIDTH//2, y_offset + 130)
            else:
                draw_text(attempts_text, font_instr, GRAY_50, WIDTH//2, y_offset + 130)
            
            # Сообщение об ошибке
            if error_message_timer > 0:
                draw_text(error_message, font_instr, RED, WIDTH//2, y_offset + 165)
        
        # === Нижняя строка (статус) ===
        status_text = "status: armed | esc: disabled"
        draw_text(status_text, font_footer, GRAY_50, WIDTH - 15, HEIGHT - 15, center=False)
        
        # Версия
        draw_text("v1.0", font_footer, GRAY_50, 15, HEIGHT - 15, center=False)
        
        # Скрываем курсор мыши
        pygame.mouse.set_visible(False)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()