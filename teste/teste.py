import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt


class PythonToCSharpConverter:
    def __init__(self):
        # Mapeamento Selenium By
        self.selenium_by_map = {
            'By.ID': 'By.Id',
            'By.NAME': 'By.Name',
            'By.XPATH': 'By.XPath',
            'By.CSS_SELECTOR': 'By.CssSelector',
            'By.CLASS_NAME': 'By.ClassName',
            'By.TAG_NAME': 'By.TagName',
            'By.LINK_TEXT': 'By.LinkText',
            'By.PARTIAL_LINK_TEXT': 'By.PartialLinkText'
        }

    def detect_type(self, value):
        value = value.strip()
        if re.match(r'^-?\d+$', value):
            return 'int'
        elif re.match(r'^-?\d+\.\d+$', value):
            return 'float'
        elif value.lower() in ['true', 'false']:
            return 'bool'
        elif value.startswith('"') or value.startswith("'"):
            return 'string'
        elif value.startswith('['):
            return 'List<string>'
        elif value.startswith('{'):
            return 'Dictionary<string, string>'
        else:
            return 'var'

    def convert(self, python_code):
        lines = python_code.split('\n')
        converted_lines = []

        for line in lines:
            original_line = line
            indent = '    ' * (len(line) - len(line.lstrip())) // 4
            line = line.strip()

            if line == '':
                converted_lines.append('')
                continue

            # Selenium By conversão
            for key, value in self.selenium_by_map.items():
                line = line.replace(key, value)

            # Selenium driver e wait
            line = re.sub(r'webdriver\.Chrome\(\)', 'new ChromeDriver()', line)
            line = re.sub(r'WebDriverWait\((.*?),\s*(\d+)\)', r'new WebDriverWait(\1, TimeSpan.FromSeconds(\2))', line)
            line = re.sub(r'driver\.get\((.+?)\)', r'driver.Navigate().GoToUrl(\1);', line)
            line = re.sub(r'driver\.find_element\((.+?)\)', r'driver.FindElement(\1)', line)
            line = re.sub(r'driver\.find_elements\((.+?)\)', r'driver.FindElements(\1)', line)
            line = line.replace('.click()', '.Click();')
            line = re.sub(r'\.send_keys\((.+?)\)', r'.SendKeys(\1);', line)
            line = re.sub(r'\.get_attribute\((.+?)\)', r'.GetAttribute(\1)', line)

            # Tratamento básico de exceções
            if line.startswith('try:'):
                line = 'try {'
            elif line.startswith('except'):
                line = 'catch (Exception e) {'
            elif line.startswith('finally:'):
                line = 'finally {'

            # Variáveis
            match = re.match(r'(\w+)\s*=\s*(.+)', line)
            if match and not line.startswith(('def ', 'for ', 'if ', 'elif ', 'else', 'while ')):
                var, value = match.groups()
                csharp_type = self.detect_type(value)
                line = f'{csharp_type} {var} = {value};'

            # Funções
            if line.startswith('def '):
                func_name = re.findall(r'def (\w+)', line)[0]
                params = re.findall(r'\((.*?)\)', line)[0]
                csharp_params = ', '.join([
                    f'string {p.strip()}' for p in params.split(',')
                    if p.strip() != ''
                ])
                line = f'void {func_name}({csharp_params})' + ' {'

            # If / elif / else
            elif line.startswith('if '):
                condition = line[3:].rstrip(':')
                line = f'if ({condition})' + ' {'
            elif line.startswith('elif '):
                condition = line[5:].rstrip(':')
                line = f'else if ({condition})' + ' {'
            elif line.startswith('else'):
                line = 'else {'

            # Loops
            elif line.startswith('for '):
                match = re.match(r'for (\w+) in range\((\d+),\s*(\d+)\):', line)
                if match:
                    var, start, end = match.groups()
                    line = f'for (int {var} = {start}; {var} < {end}; {var}++)' + ' {'
                else:
                    line = '// Unsupported for-loop'

            elif line.startswith('while '):
                condition = line[6:].rstrip(':')
                line = f'while ({condition})' + ' {'

            # Fechamento de blocos
            if line.endswith(':'):
                line = line[:-1] + ' {'

            converted_lines.append(indent + line)

        # Fecha blocos
        indent_level = 0
        final_lines = []
        for line in converted_lines:
            stripped = line.strip()

            if stripped.endswith('{'):
                final_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped == '':
                final_lines.append('')
            else:
                final_lines.append('    ' * indent_level + stripped)
                if not (stripped.endswith(';') or stripped.endswith('{') or stripped.startswith('//')):
                    final_lines[-1] += ';'

        for _ in range(indent_level):
            indent_level -= 1
            final_lines.append('    ' * indent_level + '}')

        return '\n'.join(final_lines)


class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.converter = PythonToCSharpConverter()
        self.dark_mode = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Conversor Python → C# (com Selenium)")
        self.setGeometry(100, 100, 1000, 650)

        layout = QVBoxLayout()

        title = QLabel("Conversor Python → C#")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Cole seu código Python aqui...")
        layout.addWidget(self.input_text)

        buttons_layout = QHBoxLayout()

        open_button = QPushButton("Abrir Arquivo")
        open_button.clicked.connect(self.open_file)
        buttons_layout.addWidget(open_button)

        convert_button = QPushButton("Converter")
        convert_button.clicked.connect(self.convert_code)
        buttons_layout.addWidget(convert_button)

        save_button = QPushButton("Salvar Arquivo")
        save_button.clicked.connect(self.save_file)
        buttons_layout.addWidget(save_button)

        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.clear_text)
        buttons_layout.addWidget(clear_button)

        theme_button = QPushButton("Alternar Tema")
        theme_button.clicked.connect(self.toggle_theme)
        buttons_layout.addWidget(theme_button)

        layout.addLayout(buttons_layout)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Código C# convertido aparecerá aqui...")
        layout.addWidget(self.output_text)

        self.setLayout(layout)
        self.apply_light_theme()

    def convert_code(self):
        python_code = self.input_text.toPlainText()
        if not python_code.strip():
            QMessageBox.warning(self, "Aviso", "O campo de entrada está vazio!")
            return
        csharp_code = self.converter.convert(python_code)
        self.output_text.setPlainText(csharp_code)

    def clear_text(self):
        self.input_text.clear()
        self.output_text.clear()

    def toggle_theme(self):
        if self.dark_mode:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QTextEdit {
                background-color: #3c3f41;
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        self.dark_mode = True

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTextEdit {
                background-color: white;
                color: #333333;
            }
            QPushButton {
                background-color: #dddddd;
                color: black;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)
        self.dark_mode = False

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo Python", "", "Arquivos Python (*.py)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.input_text.setPlainText(content)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo C#", "", "Arquivos C# (*.cs)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.output_text.toPlainText())
            QMessageBox.information(self, "Sucesso", "Arquivo salvo com sucesso!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec())
