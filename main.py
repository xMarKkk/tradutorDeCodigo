import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog
from analisador_lexico import remover_comentarios, obter_padrao_tokens, gerar_tokens, agrupar_tokens

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
        return "List<int>"
    return "string"

def converter_linha(linha, variaveis):
    linha = linha.strip()

    if linha.startswith("#"):
        return "//" + linha[1:]

    # Corrigir print com múltiplos argumentos
    m_print = re.match(r'print\((.*)\)', linha)
    if m_print:
        conteudo = m_print.group(1)
        partes = [p.strip() for p in re.split(r',(?![^\[\]]*\])', conteudo)]
        partes_convertidas = ['"{}"'.format(p.strip('"')) if p.startswith('"') and p.endswith('"') else p for p in partes]
        expressao = ' + " " + '.join(partes_convertidas)
        return f'Console.WriteLine({expressao});'

    m_if = re.match(r'if (.*):', linha)
    if m_if:
        cond = m_if.group(1)
        return f'if ({cond})' + " {"

    if linha == "else:":
        return "} else {"

    m_while = re.match(r'while (.*):', linha)
    if m_while:
        cond = m_while.group(1)
        return f'while ({cond})' + " {"

    m_for = re.match(r'for (\w+) in range\(([^,]+),\s*([^)]+)\):', linha)
    if m_for:
        var, inicio, fim = m_for.groups()
        if var not in variaveis:
            variaveis[var] = "int"
            decl = f"int {var}"
        else:
            decl = var
        return f'for ({decl} = {inicio}; {var} < {fim}; {var}++)' + " {"

    m_for_simple = re.match(r'for (\w+) in range\(([^)]+)\):', linha)
    if m_for_simple:
        var, fim = m_for_simple.groups()
        if var not in variaveis:
            variaveis[var] = "int"
            decl = f"int {var}"
        else:
            decl = var
        return f'for ({decl} = 0; {var} < {fim}; {var}++)' + " {"

    m_atr = re.match(r'(\w+)\s*=\s*(.+)', linha)
    if m_atr:
        var = m_atr.group(1)
        val = m_atr.group(2)
        tipo = inferir_tipo(val)
        if var not in variaveis:
            variaveis[var] = tipo
            return f"{tipo} {var} = {val};"
        else:
            return f"{var} = {val};"

    if linha.startswith("return "):
        return_valor = linha[7:].strip()
        return ("__RETURN__", return_valor)

    return linha + ";"

def converter_corpo(corpo):
    linhas_csharp = []
    variaveis = {}
    indent_level = 1
    retorno_final = None

    for linha in corpo:
        linha_convertida = converter_linha(linha, variaveis)

        # Se é um return tratado
        if isinstance(linha_convertida, tuple) and linha_convertida[0] == "__RETURN__":
            retorno_final = linha_convertida[1]
            continue  # adiciona depois fora do bloco

        linha_csharp = linha_convertida
        linhas_csharp.append("    " * indent_level + linha_csharp)

        if linha_csharp.endswith("{"):
            indent_level += 1

    while indent_level > 1:
        indent_level -= 1
        linhas_csharp.append("    " * indent_level + "}")

    # Adiciona o return ao final se foi capturado
    if retorno_final:
        linhas_csharp.append("    " * indent_level + f"return {retorno_final};")

    return linhas_csharp, variaveis


def converter_metodo(nome, parametros, corpo):
    tipo_retorno = "void"
    tem_return = False
    retorno_valor = None

    for linha in corpo:
        if linha.strip().startswith("return "):
            tem_return = True
            retorno_valor = linha.strip()[7:].strip()
            break

    tipo_parametros = []
    for p in parametros:
        tipo_parametros.append(("int", p.strip()))

    linhas_csharp, variaveis = converter_corpo(corpo)

    if tem_return:
        if retorno_valor in variaveis:
            tipo_retorno = variaveis[retorno_valor]
        else:
            tipo_retorno = inferir_tipo(retorno_valor)

    linhas = []
    params_str = ", ".join([f"{t} {n}" for t, n in tipo_parametros])
    linhas.append(f"public static {tipo_retorno} {nome}({params_str})")
    linhas.append("{")
    linhas.extend(linhas_csharp)
    linhas.append("}")
    linhas.append("")
    return "\n".join(linhas), tipo_retorno

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
                funcoes.append((nome, params, corpo))
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
                funcoes.append((nome, params, corpo))
                nome = None
                dentro_func = False
                indent_base = None
    if nome is not None:
        funcoes.append((nome, params, corpo))
    return funcoes

class ConversorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor Python → C# + Analisador Léxico")

        self.layout = QVBoxLayout()

        self.label_entrada = QLabel("Código Python:")
        self.text_entrada = QTextEdit()
        self.label_saida = QLabel("Código C# gerado:")
        self.text_saida = QTextEdit()
        self.text_saida.setReadOnly(True)

        self.label_lexico = QLabel("Análise Léxica:")
        self.text_lexico = QTextEdit()
        self.text_lexico.setReadOnly(True)

        self.botao_converter = QPushButton("Converter e Analisar")
        self.botao_converter.clicked.connect(self.converter_codigo)

        self.botao_importar = QPushButton("Importar .txt")
        self.botao_importar.clicked.connect(self.importar_arquivo)

        self.layout.addWidget(self.label_entrada)
        self.layout.addWidget(self.text_entrada)
        self.layout.addWidget(self.botao_importar)
        self.layout.addWidget(self.botao_converter)
        self.layout.addWidget(self.label_saida)
        self.layout.addWidget(self.text_saida)
        self.layout.addWidget(self.label_lexico)
        self.layout.addWidget(self.text_lexico)

        self.setLayout(self.layout)

    def importar_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo Python", "", "Arquivos de Texto (*.txt);;Todos os Arquivos (*)")
        if caminho:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                self.text_entrada.setPlainText(conteudo)

    def converter_codigo(self):
        codigo_python = self.text_entrada.toPlainText()
        funcoes = extrair_funcoes(codigo_python)

        chamadas = []
        metodos_csharp = []
        for nome, parametros, corpo in funcoes:
            metodo, tipo_retorno = converter_metodo(nome, parametros, corpo)
            metodos_csharp.append(metodo)

            args_teste = []
            for linha in corpo:
                m_atr = re.match(r'(\w+)\s*=\s*(.+)', linha.strip())
                if m_atr:
                    valor = m_atr.group(2)
                    tipo = inferir_tipo(valor)
                    if tipo == "int":
                        args_teste.append("3")
                    elif tipo == "double":
                        args_teste.append("3.5")
                    elif tipo == "bool":
                        args_teste.append("true")
                    elif tipo == "List<int>":
                        args_teste.append("new List<int>{1,2,3}")
                    else:
                        args_teste.append('"teste"')
                if len(args_teste) >= len(parametros):
                    break
            while len(args_teste) < len(parametros):
                args_teste.append("1")

            chamadas.append({"nome": nome, "args": args_teste, "retorno": tipo_retorno})

        metodos_indentados = []
        for metodo in metodos_csharp:
            linhas = metodo.splitlines()
            linhas_indentadas = [" " * 8 + linha if linha.strip() != "" else "" for linha in linhas]
            metodos_indentados.append("\n".join(linhas_indentadas))

        metodos_str = "\n\n".join(metodos_indentados)
        main_str = gerar_main(chamadas)
        linhas_main = main_str.splitlines()
        linhas_main_indentadas = [" " * 8 + linha if linha.strip() != "" else "" for linha in linhas_main]
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
}}"""

        self.text_saida.setPlainText(codigo_csharp_final)

        # Análise léxica
        codigo_limpo = remover_comentarios(codigo_python)
        padrao = obter_padrao_tokens()
        tokens = gerar_tokens(codigo_limpo, padrao)
        agrupado = agrupar_tokens(tokens)

        resultado = []
        for tipo, lista in agrupado.items():
            if lista:
                resultado.append(f"{tipo}: {', '.join(lista)}")

        self.text_lexico.setPlainText("\n".join(resultado))

if __name__ == "__main__":
    app = QApplication([])
    window = ConversorApp()
    window.resize(800, 700)
    window.show()
    app.exec()
