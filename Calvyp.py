import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit,
    QGridLayout, QVBoxLayout, QLabel, QDialog, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QRectF
from PyQt6.QtGui import QFont, QMouseEvent, QPainter, QColor, QPainterPath, QKeyEvent, QScreen


class AboutDialog(QDialog):
    """Диалог остался на случай, если вы захотите вернуть его позже."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 180)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("О программе")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")

        info = QLabel(
            "Калькулятор v1.0\n"
            "Разработано: xstopiop\n"
            "© 2025 Все права защищены."
        )
        info.setFont(QFont("Segoe UI", 10))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #c0c0d0; line-height: 1.4;")

        close_btn = QPushButton("Закрыть")
        close_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        close_btn.setFixedSize(80, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #5a5b72;
                color: white;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #6a6b82;
            }
        """)
        close_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def paintEvent(self, event):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 14, 14)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, QColor(30, 31, 41))


class AnimatedButton(QPushButton):
    def __init__(self, text, normal_color, hover_color, pressed_color):
        super().__init__(text)
        self._normal_color = QColor(normal_color)
        self._hover_color = QColor(hover_color)
        self._pressed_color = QColor(pressed_color)
        self._current_color = self._normal_color

        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.setFixedSize(75, 75)
        self._update_style()

        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._current_color.name()};
                color: white;
                border: none;
                border-radius: 18px;
            }}
        """)

    @pyqtProperty(QColor)
    def color(self):
        return self._current_color

    @color.setter
    def color(self, value: QColor):
        self._current_color = value
        self._update_style()

    def enterEvent(self, event):
        self.animate_to(self._hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_to(self._normal_color)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.animate_to(self._pressed_color)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.animate_to(self._hover_color)
        super().mouseReleaseEvent(event)

    def animate_to(self, color: QColor):
        if self.animation.state() == self.animation.State.Running:
            self.animation.stop()
        self.animation.setStartValue(self._current_color)
        self.animation.setEndValue(color)
        self.animation.start()


class DisplayLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Segoe UI", 24, QFont.Weight.Medium))
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setReadOnly(True)
        self.setFixedHeight(90)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2a2b3a;
                color: white;
                border: none;
                border-radius: 18px;
                padding: 0 20px;
            }
        """)
        self._opacity = 1.0
        self._target_text = ""

    def setTextAnimated(self, text):
        self._target_text = text
        self._opacity = 0.0
        self.update()
        QTimer.singleShot(10, self._fade_in)

    def _fade_in(self):
        if self._opacity < 1.0:
            self._opacity += 0.1
            self.update()
            QTimer.singleShot(10, self._fade_in)
        else:
            self.setText(self._target_text)

    def paintEvent(self, event):
        if self._opacity < 1.0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setOpacity(self._opacity)
            super().paintEvent(event)
        else:
            super().paintEvent(event)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 600)  # ТОЧНЫЙ размер

        # Тень для глубины
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

        # Основной контейнер
        self.container = QWidget(self)
        self.container.setGeometry(10, 10, 380, 580)
        self.container.setStyleSheet("background-color: #1e1f29; border-radius: 22px;")

        # Заголовок БЕЗ КНОПКИ "i"
        title_bar = QWidget(self.container)
        title_bar.setFixedHeight(40)
        title_layout = QVBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 5, 15, 0)

        title_label = QLabel("Калькулятор • xstopiop")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #a0a0c0;")
        title_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Дисплей
        self.display = DisplayLineEdit()

        # Кнопки
        buttons = [
            ('C', 0, 0), ('⌫', 0, 1), ('÷', 0, 2), ('×', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('−', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('+', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('=', 3, 3),
            ('0', 4, 0), ('.', 4, 2)
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(15, 5, 15, 15)

        for text, row, col in buttons:
            if text == '0':
                btn = AnimatedButton(text, "#3a3b4d", "#4a4b5d", "#2a2b3a")
                grid.addWidget(btn, row, col, 1, 2)  # занимает 2 колонки
            elif text == '=':
                btn = AnimatedButton(text, "#8a2be2", "#9b45ff", "#7a1bd2")
                btn.setFixedSize(75, 160)  # высота на 2 строки
                grid.addWidget(btn, row, col, 2, 1)
            else:
                if text in '÷×−+':
                    btn = AnimatedButton(text, "#4a6cf7", "#5a7cff", "#3a5ce7")
                elif text == 'C' or text == '⌫':
                    btn = AnimatedButton(text, "#ff4d6d", "#ff6b8a", "#e03a5d")
                else:
                    btn = AnimatedButton(text, "#3a3b4d", "#4a4b5d", "#2a2b3a")
                grid.addWidget(btn, row, col)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.display)
        main_layout.addLayout(grid)

        self.current_input = ""
        self.last_was_operator = False

        # Плавное появление
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(250)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.setWindowOpacity(0.0)

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_in_animation.start()
        self.center_window()

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        window_rect = self.frameGeometry()
        window_rect.moveCenter(screen.center())
        self.move(window_rect.topLeft())

    # УБРАНО: show_about() и кнопка "i"

    def paintEvent(self, event):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 22, 22)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, Qt.GlobalColor.transparent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_start_position)
            event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        text = event.text()

        key_map = {
            Qt.Key.Key_Escape: 'C',
            Qt.Key.Key_Backspace: '⌫',
            Qt.Key.Key_Return: '=',
            Qt.Key.Key_Enter: '=',
            Qt.Key.Key_Plus: '+',
            Qt.Key.Key_Minus: '−',
            Qt.Key.Key_Asterisk: '×',
            Qt.Key.Key_Slash: '÷',
            Qt.Key.Key_Period: '.',
        }

        if key in key_map:
            self.handle_input(key_map[key])
        elif text.isdigit():
            self.handle_input(text)
        elif text == ',':
            self.handle_input('.')

    def handle_input(self, char):
        if char == 'C':
            self.current_input = ""
            self.display.setText("")
            self.last_was_operator = False
        elif char == '⌫':
            self.current_input = self.current_input[:-1]
            self.display.setText(self.current_input)
            if self.current_input and self.current_input[-1] in "+−×÷":
                self.last_was_operator = True
            else:
                self.last_was_operator = False
        elif char == '=':
            self.calculate_result()
        else:
            if char in "+−×÷":
                if self.last_was_operator or not self.current_input:
                    return
                self.last_was_operator = True
            else:
                self.last_was_operator = False
            self.current_input += char
            self.display.setText(self.current_input)

    def calculate_result(self):
        if not self.current_input:
            return
        expr = self.current_input.replace('×', '*').replace('÷', '/').replace('−', '-')
        if not re.match(r'^[0-9+\-*/(). ]+$', expr):
            self.display.setTextAnimated("Ошибка")
            self.current_input = ""
            self.last_was_operator = False
            return
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)
            self.display.setTextAnimated(str(result))
            self.current_input = str(result)
            self.last_was_operator = False
        except Exception:
            self.display.setTextAnimated("Ошибка")
            self.current_input = ""
            self.last_was_operator = False


def connect_buttons(calc: Calculator):
    for child in calc.findChildren(AnimatedButton):
        text = child.text()
        child.clicked.connect(lambda _, t=text: calc.handle_input(t))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(30, 31, 41))
    palette.setColor(palette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(palette)

    calc = Calculator()
    connect_buttons(calc)
    calc.show()
    sys.exit(app.exec())