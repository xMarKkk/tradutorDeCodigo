import ast
import re
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QWidget, QPushButton, QSplitter, QLabel, QHBoxLayout, QStatusBar, QCheckBox
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt


class ConversorPythonCSharp:
    def __init__(self):
        self.erros = []

    def detectar_tipo(self, valor):
        if isinstance(valor, ast.Constant):
            v = valor.value
            if isinstance(v, bool):
                return "bool"
            elif isinstance(v, int):
                return "int"
            elif isinstance(v, float):
                return "double"
            elif isinstance(v, str):
                return "string"
            elif v is None:
                return "object"
        elif isinstance(valor, ast.List):
            return "List<object>"
        elif isinstance(valor, ast.Dict):
            return "Dictionary<object, object>"
        return "var"

    def converter_tipo_hint(self, annotation):
        if annotation is None:
            return "var"
        if isinstance(annotation, ast.Name):
            mapeamento = {
                "int": "int",
                "float": "double",
                "bool": "bool",
                "str": "string",
                "None": "void",
                "list": "List<object>",
                "dict": "Dictionary<object, object>"
            }
            return mapeamento.get(annotation.id, "object")
        return "object"

    def converter_funcoes(self, node):
        nome = node.name
        args = [
            f"{self.converter_tipo_hint(arg.annotation)} {arg.arg}"
            for arg in node.args.args
        ]
        tipo_retorno = self.converter_tipo_hint(node.returns)

        cabecalho = f"public static {tipo_retorno} {nome}({', '.join(args)})"
        corpo = [
            self.converter_linha(n, nivel=1) for n in node.body
        ] or ["    // Método sem implementação"]

        codigo = f"{cabecalho}\n{{\n" + "\n".join(corpo) + "\n}}"
        return codigo

    def converter_linha(self, node, nivel=0):
        indent = "    " * nivel

        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                nome_var = node.targets[0].id
                valor = self.converter_expr(node.value)
                tipo = self.detectar_tipo(node.value)
                return f"{indent}{tipo} {nome_var} = {valor};"
            else:
                return indent + "// Atribuição não suportada"

        elif isinstance(node, ast.Expr):
            return indent + self.converter_expr(node.value) + ";"

        elif isinstance(node, ast.Return):
            retorno = self.converter_expr(node.value) if node.value else ""
            return indent + f"return {retorno};"

        elif isinstance(node, ast.If):
            cond = self.converter_expr(node.test)
            corpo = "\n".join(self.converter_linha(n, nivel + 1) for n in node.body)
            codigo = f"{indent}if ({cond})\n{indent}{{\n{corpo}\n{indent}}}"
            if node.orelse:
                corpo_else = "\n".join(self.converter_linha(n, nivel + 1) for n in node.orelse)
                codigo += f"\n{indent}else\n{indent}{{\n{corpo_else}\n{indent}}}"
            return codigo

        elif isinstance(node, ast.While):
            cond = self.converter_expr(node.test)
            corpo = "\n".join(self.converter_linha(n, nivel + 1) for n in node.body)
            return f"{indent}while ({cond})\n{indent}{{\n{corpo}\n{indent}}}"

        elif isinstance(node, ast.For):
            var = node.target.id
            iterador = self.converter_expr(node.iter)
            corpo = "\n".join(self.converter_linha(n, nivel + 1) for n in node.body)
            return f"{indent}foreach (var {var} in {iterador})\n{indent}{{\n{corpo}\n{indent}}}"

        elif isinstance(node, ast.Pass):
            return indent + "// pass"

        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            return indent + "// Estrutura não suportada"

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            return indent + "// Importação não convertida"

        elif isinstance(node, ast.Try):
            try_block = "\n".join(self.converter_linha(n, nivel + 1) for n in node.body)
            except_blocks = []
            for handler in node.handlers:
                typ = self.converter_expr(handler.type) if handler.type else "Exception"
                name = handler.name or "ex"
                corpo = "\n".join(self.converter_linha(n, nivel + 2) for n in handler.body)
                except_blocks.append(f"{indent}catch ({typ} {name})\n{indent}{{\n{corpo}\n{indent}}}")
            finally_block = ""
            if node.finalbody:
                fin = "\n".join(self.converter_linha(n, nivel + 1) for n in node.finalbody)
                finally_block = f"\n{indent}finally\n{indent}{{\n{fin}\n{indent}}}"
            return f"{indent}try\n{indent}{{\n{try_block}\n{indent}}}\n" + "\n".join(except_blocks) + finally_block

        else:
            return indent + "// Código não suportado: " + str(type(node))

    def converter_expr(self, expr):
        if isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Attribute):
                base = self.converter_expr(expr.func.value)
                attr = expr.func.attr

                # Selenium
                if attr.startswith("find_element"):
                    by = self.converter_expr(expr.args[0])
                    alvo = self.converter_expr(expr.args[1])
                    return f"{base}.FindElement(By.{by}({alvo}))"

                if attr.startswith("find_elements"):
                    by = self.converter_expr(expr.args[0])
                    alvo = self.converter_expr(expr.args[1])
                    return f"{base}.FindElements(By.{by}({alvo}))"

                args = ", ".join(self.converter_expr(a) for a in expr.args)
                return f"{base}.{attr}({args})"

            if isinstance(expr.func, ast.Name):
                nome = expr.func.id
                args = ", ".join(self.converter_expr(a) for a in expr.args)
                return f"{nome}({args})"

            return "/* chamada complexa */"

        elif isinstance(expr, ast.Name):
            return expr.id

        elif isinstance(expr, ast.Constant):
            v = expr.value
            if isinstance(v, str):
                return f"\"{v}\""
            if v is None:
                return "null"
            if isinstance(v, bool):
                return "true" if v else "false"
            return str(v)

        elif isinstance(expr, ast.Attribute):
            return f"{self.converter_expr(expr.value)}.{expr.attr}"

        elif isinstance(expr, ast.BinOp):
            left = self.converter_expr(expr.left)
            right = self.converter_expr(expr.right)
            op = self.converter_op(expr.op)
            return f"({left} {op} {right})"

        elif isinstance(expr, ast.UnaryOp):
            operand = self.converter_expr(expr.operand)
            op = self.converter_op(expr.op)
            return f"{op}{operand}"

        elif isinstance(expr, ast.Compare):
            left = self.converter_expr(expr.left)
            comparadores = " ".join(
                f"{self.converter_op(op)} {self.converter_expr(comp)}"
                for op, comp in zip(expr.ops, expr.comparators)
            )
            return f"{left} {comparadores}"

        elif isinstance(expr, ast.List):
            elementos = ", ".join(self.converter_expr(e) for e in expr.elts)
            return f"new List<object>{{ {elementos} }}"

        elif isinstance(expr, ast.Dict):
            itens = ", ".join(
                f"{{ {self.converter_expr(k)}, {self.converter_expr(v)} }}"
                for k, v in zip(expr.keys, expr.values)
            )
            return f"new Dictionary<object, object>{{ {itens} }}"

        else:
            return "/* expressão não suportada */"

    def converter_op(self, op):
        return {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%",
            ast.Pow: "^", ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
            ast.Gt: ">", ast.GtE: ">=", ast.And: "&&", ast.Or: "||",
            ast.USub: "-", ast.Not: "!"
        }.get(type(op), "/*op*/")

    def converter(self, codigo_python):
        self.erros = []
        try:
            arvore = ast.parse(codigo_python)
        except Exception as e:
            self.erros.append(str(e))
            return "// Erro na análise sintática: " + str(e)

        funcoes = []
        main_body = []

        for node in arvore.body:
            if isinstance(node, ast.FunctionDef):
                funcoes.append(self.converter_funcoes(node))
            elif isinstance(node, ast.ClassDef):
                funcoes.append("// Classes não suportadas")
            else:
                main_body.append(self.converter_linha(node, nivel=2))

        using = (
            "using System;\nusing System.Collections.Generic;\nusing OpenQA.Selenium;\n\n"
        )

        codigo = (
            using +
            "namespace ConversorPythonCSharp\n{\n" +
            "    public static class Program\n    {\n" +
            "        public static void Main(string[] args)\n        {\n" +
            "\n".join(main_body) + "\n        }\n\n" +
            "\n\n".join("        " + f.replace("\n", "\n        ") for f in funcoes) + "\n" +
            "    }\n}"
        )
        return codigo


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor Python → C#")
        self.setGeometry(100, 100, 1200, 700)

        self.conversor = ConversorPythonCSharp()

        self.editor_python = QPlainTextEdit()
        self.editor_python.setFont(QFont("Consolas", 11))

        self.editor_csharp = QPlainTextEdit()
        self.editor_csharp.setFont(QFont("Consolas", 11))
        self.editor_csharp.setReadOnly(True)

        btn_converter = QPushButton("Converter")
        btn_converter.clicked.connect(self.converter_codigo)

        btn_abrir = QPushButton("Abrir .py")
        btn_abrir.clicked.connect(self.abrir_arquivo)

        btn_salvar = QPushButton("Salvar .cs")
        btn_salvar.clicked.connect(self.salvar_arquivo)

        self.check_tema = QCheckBox("Modo Escuro")
        self.check_tema.stateChanged.connect(self.alternar_tema)

        topo = QHBoxLayout()
        topo.addWidget(btn_abrir)
        topo.addWidget(btn_salvar)
        topo.addWidget(btn_converter)
        topo.addWidget(self.check_tema)
        topo.addStretch()

        status = QStatusBar()
        self.setStatusBar(status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        esquerda = QWidget()
        esquerda_layout = QVBoxLayout()
        esquerda_layout.addWidget(QLabel("Código Python"))
        esquerda_layout.addWidget(self.editor_python)
        esquerda.setLayout(esquerda_layout)

        direita = QWidget()
        direita_layout = QVBoxLayout()
        direita_layout.addWidget(QLabel("Código C#"))
        direita_layout.addWidget(self.editor_csharp)
        direita.setLayout(direita_layout)

        splitter.addWidget(esquerda)
        splitter.addWidget(direita)
        splitter.setSizes([600, 600])

        layout = QVBoxLayout()
        layout.addLayout(topo)
        layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def alternar_tema(self):
        if self.check_tema.isChecked():
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 20))
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            self.setPalette(palette)
        else:
            self.setPalette(QApplication.style().standardPalette())

    def converter_codigo(self):
        codigo = self.editor_python.toPlainText()
        resultado = self.conversor.converter(codigo)
        self.editor_csharp.setPlainText(resultado)
        if self.conversor.erros:
            self.statusBar().showMessage("Erros: " + "; ".join(self.conversor.erros), 5000)
        else:
            self.statusBar().showMessage("Conversão realizada com sucesso!", 3000)

    def abrir_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo Python", "", "Python Files (*.py)")
        if caminho:
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    self.editor_python.setPlainText(f.read())
                self.statusBar().showMessage(f"Abrindo '{caminho}'", 3000)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível abrir: {e}")

    def salvar_arquivo(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar arquivo C#", "", "C# Files (*.cs)")
        if caminho:
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(self.editor_csharp.toPlainText())
                self.statusBar().showMessage(f"Salvo em '{caminho}'", 3000)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível salvar: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
