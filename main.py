import sys
import math
import cmath
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                            QPushButton, QLineEdit, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette
from functools import partial

class ScientificCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scientific Calculator")
        
        # Modern dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLineEdit {
                padding: 20px;
                background-color: #2d2d2d;
                border: none;
                border-radius: 10px;
                font-size: 28px;
                color: #ffffff;
                margin: 10px;
            }
            QPushButton {
                padding: 15px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                min-width: 45px;
                min-height: 25px;
                margin: 2px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QLabel {
                color: #808080;
                font-size: 14px;
                padding: 5px;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Add history display
        self.history_display = QLabel("")
        self.history_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.history_display)

        # Create main display
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        layout.addWidget(self.display)

        # Add memory display
        self.memory_display = QLabel("Memory: 0")
        self.memory_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.memory_display)

        # Create buttons grid
        buttons_layout = QGridLayout()
        layout.addLayout(buttons_layout)

        # Button texts and their positions - expanded with more functions
        buttons = {
            'DEG': (0, 0), 'RAD': (0, 1), 'F-E': (0, 2), 'MC': (0, 3), 'MR': (0, 4), 'M+': (0, 5),
            'sin': (1, 0), 'cos': (1, 1), 'tan': (1, 2), 'M-': (1, 3), 'MS': (1, 4), '1/x': (1, 5),
            'asin': (2, 0), 'acos': (2, 1), 'atan': (2, 2), '(': (2, 3), ')': (2, 4), '%': (2, 5),
            'sinh': (3, 0), 'cosh': (3, 1), 'tanh': (3, 2), '7': (3, 3), '8': (3, 4), '9': (3, 5),
            'log': (4, 0), 'ln': (4, 1), 'e^x': (4, 2), '4': (4, 3), '5': (4, 4), '6': (4, 5),
            '√': (5, 0), 'x²': (5, 1), 'x³': (5, 2), '1': (5, 3), '2': (5, 4), '3': (5, 5),
            'π': (6, 0), 'e': (6, 1), 'x^y': (6, 2), '0': (6, 3), '.': (6, 4), '±': (6, 5),
            'AC': (7, 0), 'C': (7, 1), '⌫': (7, 2), '÷': (7, 3), '×': (7, 4), '-': (7, 5),
            'factorial': (8, 0), '|x|': (8, 1), 'rand': (8, 2), '+': (8, 3), '=': (8, 4, 1, 2)
        }

        # Create and style buttons with different color schemes
        for text, pos in buttons.items():
            button = QPushButton(text)
            if len(pos) == 4:  # Special case for buttons that span multiple cells
                buttons_layout.addWidget(button, pos[0], pos[1], pos[2], pos[3])
            else:
                buttons_layout.addWidget(button, pos[0], pos[1])

            # Style buttons based on their function
            if text.isdigit():
                button.setStyleSheet('background-color: #424242; color: #ffffff;')
            elif text in '+-×÷^%':
                button.setStyleSheet('background-color: #ff9800; color: #ffffff;')
            elif text == '=':
                button.setStyleSheet('background-color: #2196f3; color: #ffffff;')
            elif text in ['AC', 'C', '⌫']:
                button.setStyleSheet('background-color: #f44336; color: #ffffff;')
            elif text in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh']:
                button.setStyleSheet('background-color: #4caf50; color: #ffffff;')
            else:
                button.setStyleSheet('background-color: #333333; color: #ffffff;')
            
            button.clicked.connect(self.button_clicked)

        self.resize(600, 800)
        self.memory = 0
        self.result = ''
        self.angle_mode = 'DEG'  # Default to degrees
        self.history = []

    def button_clicked(self):
        button = self.sender()
        text = button.text()
        current = self.display.text()

        if text in ['DEG', 'RAD']:
            self.angle_mode = text
            return

        if text in ['MC', 'MR', 'M+', 'M-', 'MS']:
            self.handle_memory(text)
            return

        if text == 'AC':
            self.display.clear()
            self.history = []
            self.history_display.setText("")
            self.result = ''
        elif text == 'C':
            self.display.clear()
        elif text == '⌫':
            self.display.setText(current[:-1])
        elif text == '=':
            try:
                expr = self.prepare_expression(current)
                result = eval(expr)
                
                # Format result
                if isinstance(result, (int, float)):
                    if abs(result) < 1e-10:
                        result = 0
                    formatted_result = f"{result:g}"
                else:
                    formatted_result = str(result)
                
                # Update history
                self.history.append(f"{current} = {formatted_result}")
                if len(self.history) > 3:
                    self.history.pop(0)
                self.history_display.setText("\n".join(self.history))
                
                self.display.setText(formatted_result)
                self.result = formatted_result
            except Exception as e:
                self.display.setText('Error')
        else:
            self.display.setText(current + text)

    def prepare_expression(self, expr):
        # Replace mathematical symbols with Python operators
        expr = expr.replace('×', '*').replace('÷', '/')
        expr = expr.replace('π', str(math.pi)).replace('e', str(math.e))
        
        # Handle special functions
        if 'sin' in expr:
            expr = expr.replace('sin', 'math.sin')
        if 'cos' in expr:
            expr = expr.replace('cos', 'math.cos')
        if 'tan' in expr:
            expr = expr.replace('tan', 'math.tan')
        if 'log' in expr:
            expr = expr.replace('log', 'math.log10')
        if 'ln' in expr:
            expr = expr.replace('ln', 'math.log')
        if '√' in expr:
            expr = expr.replace('√', 'math.sqrt')
        if 'x²' in expr:
            expr = expr.replace('x²', '**2')
        if 'x³' in expr:
            expr = expr.replace('x³', '**3')
        if 'x^y' in expr:
            expr = expr.replace('x^y', '**')
        if '|x|' in expr:
            expr = expr.replace('|x|', 'abs')
        if 'factorial' in expr:
            expr = expr.replace('factorial', 'math.factorial')
        
        # Convert angles if needed
        if self.angle_mode == 'DEG' and any(trig in expr for trig in ['sin', 'cos', 'tan']):
            expr = expr.replace('math.sin', 'math.sin(math.radians')
            expr = expr.replace('math.cos', 'math.cos(math.radians')
            expr = expr.replace('math.tan', 'math.tan(math.radians')
            expr += ')'
        
        return expr

    def handle_memory(self, operation):
        try:
            current = float(self.display.text() or '0')
            if operation == 'MC':
                self.memory = 0
            elif operation == 'MR':
                self.display.setText(str(self.memory))
            elif operation == 'M+':
                self.memory += current
            elif operation == 'M-':
                self.memory -= current
            elif operation == 'MS':
                self.memory = current
            
            self.memory_display.setText(f"Memory: {self.memory}")
        except ValueError:
            self.display.setText('Error')

    def keyPressEvent(self, event):
        # Handle keyboard input
        key = event.key()
        if key >= Qt.Key.Key_0 and key <= Qt.Key.Key_9:
            self.display.setText(self.display.text() + str(key - Qt.Key.Key_0))
        elif key == Qt.Key.Key_Plus:
            self.display.setText(self.display.text() + '+')
        elif key == Qt.Key.Key_Minus:
            self.display.setText(self.display.text() + '-')
        elif key == Qt.Key.Key_Asterisk:
            self.display.setText(self.display.text() + '×')
        elif key == Qt.Key.Key_Slash:
            self.display.setText(self.display.text() + '÷')
        elif key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
            self.button_clicked(QPushButton('='))
        elif key == Qt.Key.Key_Escape:
            self.display.clear()
        elif key == Qt.Key.Key_Backspace:
            self.display.setText(self.display.text()[:-1])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = ScientificCalculator()
    calc.show()
    sys.exit(app.exec())
