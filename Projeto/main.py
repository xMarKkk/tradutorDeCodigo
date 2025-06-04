import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel

def inferir_tipo(valor):
    valor = valor.strip()
    if valor.startswith('"') and valor.endswith('"'):
        return "string"
    if valor.isdigit():
        return "int"
    try:
        float(valor)
        return "double"
    except:
        pass
    if valor.lower() in ['true', 'false']:
        return "bool"
    return "var"

def converter_metodo(nome, parametros, corpo):
    tipo_retorno = "void"
    tem_return = False
    tipo_retorno_detectado = "void"

    for linha in corpo:
        if linha.strip().startswith("return "):
            tem_return = True
            retorno_valor = linha.strip()[7:]
            tipo_retorno_detectado = inferir_tipo(retorno_valor)
            break

    # Inferir tipo dos parâmetros como int por padrão (pode melhorar)
    tipo_parametros = []
    for p in parametros:
        tipo_parametros.append( ("int", p.strip()) )

    if tem_return:
        tipo_retorno = tipo_retorno_detectado

    linhas_csharp = []
    params_str = ", ".join([f"{t} {n}" for t, n in tipo_parametros])
    linhas_csharp.append(f"public static {tipo_retorno} {nome}({params_str})")
    linhas_csharp.append("{")
    for linha in corpo:
        linha_stripped = linha.strip()
        if linha_stripped.startswith("return "):
            linhas_csharp.append(f"    {linha_stripped};")
        else:
            if linha_stripped != "":
                linhas_csharp.append(f"    {linha_stripped};")
    linhas_csharp.append("}")
    linhas_csharp.append("")
    return "\n".join(linhas_csharp), tipo_retorno

def gerar_main(chamadas):
    linhas = []
    linhas.append("static void Main(string[] args)")
    linhas.append("{")
    for chamada in chamadas:
        nome_func = chamada['nome']
        args = chamada['args']
        tipo_retorno = chamada['retorno']
        args_str = ", ".join(args)
        if tipo_retorno != "void":
            linhas.append(f"    {tipo_retorno} resultado = {nome_func}({args_str});")
            linhas.append(f"    Console.WriteLine($\"Resultado de {nome_func}: {{resultado}}\");")
        else:
            linhas.append(f"    {nome_func}({args_str});")
    linhas.append("}")
    return "\n".join(linhas)

def extrair_funcoes(codigo):
    linhas = codigo.splitlines()
    funcoes = []
    nome = None
    params = []
    corpo = []
    dentro_func = False
    indent_base = None

    for linha in linhas:
        if linha.strip().startswith("def "):
            # salva a função anterior se existir
            if nome is not None:
                funcoes.append( (nome, params, corpo) )
            m = re.match(r'def (\w+)\((.*?)\):', linha.strip())
            if m:
                nome = m.group(1)
                params = [p.strip() for p in m.group(2).split(",") if p.strip() != ""]
                corpo = []
                dentro_func = True
                indent_base = None
            else:
                nome = None
                dentro_func = False
        elif dentro_func:
            # considerar que corpo tem indentação maior que base
            if linha.strip() == "":
                continue
            if indent_base is None:
                indent_base = len(linha) - len(linha.lstrip())
            indent_atual = len(linha) - len(linha.lstrip())
            if indent_atual >= indent_base:
                corpo.append(linha[indent_base:])
            else:
                # fim da função
                funcoes.append( (nome, params, corpo) )
                nome = None
                dentro_func = False
                indent_base = None
    # pegar última função se no final do arquivo
    if nome is not None:
        funcoes.append( (nome, params, corpo) )
    return funcoes

class ConversorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor Python → C#")

        self.layout = QVBoxLayout()

        self.label_entrada = QLabel("Código Python:")
        self.text_entrada = QTextEdit()
        self.label_saida = QLabel("Código C# gerado:")
        self.text_saida = QTextEdit()
        self.text_saida.setReadOnly(True)

        self.botao_converter = QPushButton("Converter")
        self.botao_converter.clicked.connect(self.converter_codigo)

        self.layout.addWidget(self.label_entrada)
        self.layout.addWidget(self.text_entrada)
        self.layout.addWidget(self.botao_converter)
        self.layout.addWidget(self.label_saida)
        self.layout.addWidget(self.text_saida)

        self.setLayout(self.layout)

    def converter_codigo(self):
        codigo_python = self.text_entrada.toPlainText()
        funcoes = extrair_funcoes(codigo_python)

        chamadas = []
        metodos_csharp = []
        for nome, parametros, corpo in funcoes:
            metodo, tipo_retorno = converter_metodo(nome, parametros, corpo)
            metodos_csharp.append(metodo)
            # Para testes, chamar cada função com argumentos fixos "3" e "5" se tiver pelo menos 2 parâmetros
            args_teste = []
            for _ in parametros:
                args_teste.append("3")
            chamadas.append({"nome": nome, "args": args_teste, "retorno": tipo_retorno})

        metodos_str = "\n".join(metodos_csharp)
        main_str = gerar_main(chamadas)

        codigo_csharp_final = f"""using System;

class Program
{{
{metodos_str}

{main_str}
}}
"""
        self.text_saida.setPlainText(codigo_csharp_final)


if __name__ == "__main__":
    app = QApplication([])
    window = ConversorApp()
    window.resize(700, 600)
    window.show()
    app.exec()
