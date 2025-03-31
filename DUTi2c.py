from machine import I2C, Pin
import time

'''
    DarkutomI2CLcd - A library for controlling I2C LCD displays with a 4-bit interface.
    Version: 1.846
    Author: Darkutom (https://github.com/darkutomofficial)
    License: MIT License (https://opensource.org/licenses/MIT)
'''



class DarkutomI2CLcd:
    LCD_CLEARDISPLAY   = 0x01
    LCD_RETURNHOME     = 0x02
    LCD_ENTRYMODESET   = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_FUNCTIONSET    = 0x20
    LCD_SETDDRAMADDR   = 0x80

    LCD_ENTRYLEFT           = 0x02
    LCD_ENTRYSHIFTDECREMENT = 0x00

    LCD_DISPLAYON = 0x04
    LCD_CURSOROFF = 0x00
    LCD_BLINKOFF  = 0x00

    LCD_2LINE    = 0x08
    LCD_5x8DOTS  = 0x00
    LCD_4BITMODE = 0x00

    ENABLE         = 0x04
    READ_WRITE     = 0x02
    REGISTER_SELECT = 0x01

    BACKLIGHT    = 0x08
    NOBACKLIGHT  = 0x00

    DRIVER_VERSION = "v1.846"
    # Final patch for row shifting

    def __init__(self, i2c: I2C, addr: int = 0x27, cols: int = 16, rows: int = 2, boot_skip: bool = False):
        self.i2c = i2c
        self.addr = addr
        self.cols = cols
        self.rows = rows
        self.boot_skip = boot_skip
        self.backlight = self.BACKLIGHT
        self._init_lcd()
        if not self.boot_skip:
            self._splash_screen()

    def _write4bits(self, data: int):
        self.i2c.writeto(self.addr, bytearray([data | self.backlight]))
        self._pulse_enable(data)

    def _pulse_enable(self, data: int):
        self.i2c.writeto(self.addr, bytearray([data | self.ENABLE | self.backlight]))
        time.sleep_us(500)
        self.i2c.writeto(self.addr, bytearray([data & ~self.ENABLE | self.backlight]))
        time.sleep_us(100)

    def _send(self, data: int, mode: int):
        highnib = data & 0xF0
        lownib  = (data << 4) & 0xF0
        self._write4bits(highnib | mode)
        self._write4bits(lownib | mode)

    def _send_command(self, cmd: int):
        self._send(cmd, 0)

    def _send_data(self, data: int):
        self._send(data, self.REGISTER_SELECT)

# AussieAdobo better then filipinoAdobo -vils
# thease boots are made for walking -BootsDilligaf
# you cant put brains in a statue -Grad


    def _init_lcd(self):
        time.sleep_ms(50)
        self._write4bits(0x30)
        time.sleep_ms(5)
        self._write4bits(0x30)
        time.sleep_us(100)
        self._write4bits(0x30)
        time.sleep_us(100)
        self._write4bits(0x20)
        time.sleep_us(100)

        self._send_command(self.LCD_FUNCTIONSET | self.LCD_4BITMODE | self.LCD_2LINE | self.LCD_5x8DOTS)
        self._send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF)
        self.clear()
        self._send_command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT)
        time.sleep_ms(2)

    def clear(self):
        self._send_command(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2)

    def home(self):
        self._send_command(self.LCD_RETURNHOME)
        time.sleep_ms(2)

    def move_to(self, col: int, row: int):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.rows:
            row = self.rows - 1
        self._send_command(self.LCD_SETDDRAMADDR | (col + row_offsets[row]))

    def putstr(self, string: str):
        if isinstance(string, str):  # Check if input is a string
            for char in string:
                self._send_data(ord(char))
        else:
            print(f"Error: Expected a string, but got {type(string)}")



    def _fade_out(self):
        steps = self.cols // 2
        for i in range(steps):
            for row in range(self.rows):
                self.move_to(i, row)
                self._send_data(ord(' '))
                right_col = self.cols - 1 - i
                if right_col != i:
                    self.move_to(right_col, row)
                    self._send_data(ord(' '))
            time.sleep(0.1)

    def _fade_in(self, text: str, row: int, speed: float):
        start_col = max((self.cols - len(text)) // 2, 0)
        self.move_to(start_col, row)
        for char in text:
            self.putstr(char)
            time.sleep(speed)

    def print_top(self, text: str):
        start_col = (self.cols - len(text)) // 2
        self.move_to(start_col, 0)
        self.putstr(text)

    def print_bottom(self, text: str):
        start_col = (self.cols - len(text)) // 2
        self.move_to(start_col, 1)
        self.putstr(text)

    def _splash_screen(self):
        if not self.boot_skip:
            msg1_line1 = "I2C driver"
            msg1_line2 = "made by darkutom"
            self.clear()
            self.print_top(msg1_line1)
            self.print_bottom(msg1_line2)
            time.sleep(2)
            self._fade_out()

            version_msg = self.DRIVER_VERSION
            self.clear()
            self.print_top(version_msg)
            time.sleep(1.5)
            self._fade_out()
            self.clear()


    def scroll_text(self, text: str, speed: float):
        for i in range(len(text) + self.cols):
            self.clear()
            start = max(i - self.cols, 0)
            self.putstr(text[start:i])
            time.sleep(speed)

    def blink_text(self, text: str, interval: float = 0.5):
        while True:
            self.clear()
            self.putstr(text)
            time.sleep(interval)
            self.clear()
            time.sleep(interval)

    def print_left(self, text: str):
        self.move_to(0, 0)
        self.putstr(text)

    def print_center(self, text: str):
        start_col = (self.cols - len(text)) // 2
        self.move_to(start_col, 0)
        self.putstr(text)

    def print_right(self, text: str):
        start_col = self.cols - len(text)
        self.move_to(start_col, 0)
        self.putstr(text)

    def wipe_text(self, text: str, row: int, speed: float):
        for i in range(len(text)):
            self.move_to(i, row)
            self._send_data(ord(text[i]))
            time.sleep(speed)


    def print_multiline(self, text: str):
        lines = [text[i:i + self.cols] for i in range(0, len(text), self.cols)]
        for i, line in enumerate(lines):
            self.move_to(0, i)
            self.putstr(line)

    def auto_scroll(self, text: str, speed: float):
        lines = text.split("\n")
        for i in range(len(lines)):
            self.clear()
            self.print_multiline("\n".join(lines[i:i + self.rows]))
            time.sleep(speed)

    def progress_bar(self, progress: float):
        bar_length = self.cols - 2
        block = int(round(bar_length * progress))
        bar = "#" * block + "-" * (bar_length - block)
        self.clear()
        self.move_to(0, 0)
        self.putstr(f"[{bar}] {int(progress * 100)}%")

    def loading_animation(self):
        for i in range(4):
            self.clear()
            self.move_to(0, 0)
            self.putstr("." * i)
            time.sleep(0.5)

    def wrap_text(self, text: str):
        wrapped = text
        if len(text) > self.cols:
            wrapped = "\n".join([text[i:i + self.cols] for i in range(0, len(text), self.cols)])
        self.print_multiline(wrapped)

    def scroll_if_needed(self, text: str, speed: float):
        # Check if text overflows the screen
        if len(text) > self.cols:
            # Scroll the text to the left, cycling it
            while True:
                for i in range(len(text) + self.cols):
                    self.clear()
                    start = max(i - self.cols, 0)
                    self.putstr(text[start:i])
                    time.sleep(speed)

                    # Once the text has scrolled off the screen, reset it with 16 black spaces
                    if i == len(text) + self.cols - 1:
                        self.clear()
                        self.putstr(text[start:i] + " " * 16)  # Add 16 black spaces at the end
                        time.sleep(speed)  # Pause before restarting
                        break
        else:
            # If the text fits within the screen, just print it normally
            self.clear()
            self.putstr(text)