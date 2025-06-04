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
    if valor.startswith("[") and valor.endswith("]"):
        return "List<int>"  # Simples suposição para lista de inteiros
    return "var"

def converter_linha(linha, variaveis):
    linha = linha.strip()
    # Comentário
    if linha.startswith("#"):
        return "//" + linha[1:]

    # print
    m_print = re.match(r'print\((.*)\)', linha)
    if m_print:
        conteudo = m_print.group(1)
        return f'Console.WriteLine({conteudo});'

    # if
    m_if = re.match(r'if (.*):', linha)
    if m_if:
        cond = m_if.group(1)
        return f'if ({cond})' + " {"

    # else
    if linha == "else:":
        return "} else {"

    # while
    m_while = re.match(r'while (.*):', linha)
    if m_while:
        cond = m_while.group(1)
        return f'while ({cond})' + " {"

    # for (somente em range simples: for i in range(n):)
    m_for = re.match(r'for (\w+) in range\((\d+)\):', linha)
    if m_for:
        var = m_for.group(1)
        fim = m_for.group(2)
        # Declara variável se não declarada
        if var not in variaveis:
            variaveis.add(var)
            decl = f"int {var}"
        else:
            decl = var
        return f'for ({decl} = 0; {var} < {fim}; {var}++)' + " {"

    # atribuição simples
    m_atr = re.match(r'(\w+)\s*=\s*(.+)', linha)
    if m_atr:
        var = m_atr.group(1)
        val = m_atr.group(2)
        tipo = inferir_tipo(val)
        # Declara variável se não declarada
        if var not in variaveis:
            variaveis.add(var)
            return f"{tipo} {var} = {val};"
        else:
            return f"{var} = {val};"

    # return
    if linha.startswith("return "):
        return linha + ";"

    # fim de bloco (deduzido pela indentação fora do converter_linha)
    # Só retornar linha vazia
    return linha + ";"

def converter_corpo(corpo):
    linhas_csharp = []
    variaveis = set()
    indent_level = 1
    indent_stack = []

    for i, linha in enumerate(corpo):
        linha_stripped = linha.strip()
        # detectar fim de bloco (deduzindo pela indentação menor que anterior)
        # Como corpo é já indentado, simplificamos
        # Apenas fechar blocos se encontrar linha '}' na python não existe, então baseado em indentação (complexo para um conversor simples)
        # Vamos assumir que o corpo já veio separado, e converter { e } pelo if, else, for, while.

        # converter a linha
        linha_csharp = converter_linha(linha, variaveis)

        # Adicionar indentação (4 espaços * indent_level)
        linhas_csharp.append("    " * indent_level + linha_csharp)

        # Ajustar indent_level para blocos
        # Abrir bloco
        if linha_csharp.endswith("{"):
            indent_level += 1
        # Fechar bloco na linha seguinte ao else ou fim bloco não detectado aqui (simplificação)
        # Para simplificar, nada fecha aqui, pois o bloco fecha quando indentação python cai (não tratado aqui)

    # Fechar blocos abertos - para evitar erros, fechar todos ao final
    while indent_level > 1:
        indent_level -= 1
        linhas_csharp.append("    " * indent_level + "}")

    return linhas_csharp

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
    linhas_csharp.extend(converter_corpo(corpo))
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
            if linha.strip() == "":
                continue
            if indent_base is None:
                indent_base = len(linha) - len(linha.lstrip())
            indent_atual = len(linha) - len(linha.lstrip())
            if indent_atual >= indent_base:
                corpo.append(linha[indent_base:])
            else:
                funcoes.append( (nome, params, corpo) )
                nome = None
                dentro_func = False
                indent_base = None
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
            args_teste = ["3" for _ in parametros]
            chamadas.append({"nome": nome, "args": args_teste, "retorno": tipo_retorno})

        metodos_indentados = []
        for metodo in metodos_csharp:
            linhas = metodo.splitlines()
            linhas_indentadas = [(" " * 8) + linha if linha.strip() != "" else "" for linha in linhas]
            metodos_indentados.append("\n".join(linhas_indentadas))

        metodos_str = "\n\n".join(metodos_indentados)

        main_str = gerar_main(chamadas)
        linhas_main = main_str.splitlines()
        linhas_main_indentadas = [(" " * 8) + linha if linha.strip() != "" else "" for linha in linhas_main]
        main_indentado = "\n".join(linhas_main_indentadas)

        codigo_csharp_final = f"""using System;
using System.Collections.Generic;

namespace MeuProjeto
{{
    class Program
    {{
{metodos_str}

{main_indentado}
    }}
}}
"""
        self.text_saida.setPlainText(codigo_csharp_final)


if __name__ == "__main__":
    app = QApplication([])
    window = ConversorApp()
    window.resize(700, 600)
    window.show()
    app.exec()
