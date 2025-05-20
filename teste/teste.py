import tkinter as tk
from tkinter import filedialog
import re

def detectar_tipo(valor):
    valor = valor.strip()
     # Se o valor começa com aspas simples ou duplas, é uma string
    if valor.startswith("\"") or valor.startswith("'"):
        return "string"
    # Se o valor é 'true' ou 'false' (case-insensitive), é um booleano
    elif valor.lower() in ["true", "false"]:
        return "bool"
    # Se o valor corresponde a um número decimal (ex: 3.14), é um double (float em C#)
    elif re.match(r"^\d+\.\d+$", valor):  
        return "double"
     # Se o valor é um número inteiro (ex: 42), é um int
    elif re.match(r"^\d+$", valor): 
        return "int"
    # Se o valor está entre colchetes, é uma lista em Python
    elif valor.startswith("[") and valor.endswith("]"):
        elementos = valor[1:-1].split(",")
         # Se a lista está vazia, retorna uma lista genérica de objetos
        if not elementos:
            return "List<object>"
        # Detecta o tipo do primeiro elemento para definir o tipo da lista em C#
        primeiro = elementos[0].strip()
        tipo_elemento = detectar_tipo(primeiro)
        return f"List<{tipo_elemento}>"
    # Se contém 'int.Parse', provavelmente é um int vindo da entrada do usuário convertida em C#
    elif "int.Parse" in valor:
        return "int"
     # Se contém 'Console.ReadLine()', é uma string obtida da entrada do usuário
    elif "Console.ReadLine()" in valor:
        return "string"
    # Caso não corresponda a nenhum tipo conhecido, retorna 'var' para tipo implícito
    else:
        return "var"

def converter_parametros(param_str):
    params = [p.strip() for p in param_str.split(",") if p.strip()]
    csharp_params = [f"int {p}" for p in params]  # padrão: int
    return ", ".join(csharp_params)

def converter_python_para_csharp(linha, variaveis_declaradas):
    linha = linha.strip()
# se conter instrução print() em Python e converte para Console.WriteLine(...)
    if linha.startswith("print("):
        conteudo = linha[6:-1]
        return f'Console.WriteLine({conteudo});'
# Verifica se a linha envolve uma entrada de usuário com input(). Se a entrada for numérica (int(input(...))), converte para int.Parse(Console.ReadLine()). Caso contrário, usa Console.ReadLine().
    if "input(" in linha:
        var, valor = linha.split("=", 1)
        var = var.strip()
        prompt = ""
        if "int(input(" in valor:
            prompt = valor.split("int(input(")[1].split(")")[0]
            valor_csharp = "int.Parse(Console.ReadLine())"
            tipo = "int"
        else:
            prompt = valor.split("input(")[1].split(")")[0]
            valor_csharp = "Console.ReadLine()"
            tipo = "string"

        if var not in variaveis_declaradas:
            variaveis_declaradas[var] = tipo
            return f'{tipo} {var} = {valor_csharp}; // {prompt}'
        else:
            return f'{var} = {valor_csharp}; // {prompt}'
# Detecta uma estrutura condicional if em Python e a converte para if (...) { em C#.
    if linha.startswith("if "):
        condicao = linha[3:-1]
        return f'if ({condicao})\n{{'
#Converte um bloco else: do Python para } else { em C#.
    if linha.startswith("else"):
        return "} else {"
#Detecta um loop while do Python e o converte para a estrutura de loop while (...) { em C#.
    if linha.startswith("while "):
        condicao = linha[6:-1]
        return f'while ({condicao})\n{{'
#Identifica um for com range(...) em Python e o converte para um for (int i = 0; i < n; i++) em C#.
    if linha.startswith("for ") and "in range" in linha:
        var = linha.split(" ")[1]
        num = linha.split("range(")[1].split(")")[0]
        variaveis_declaradas[var] = "int"
        return f'for (int {var} = 0; {var} < {num}; {var}++)\n{{'
#Converte a definição de uma função (def nome(...)) para um método static void nome(...) em C# com parâmetros assumindo tipo int por padrão.
    if linha.startswith("def "):
        partes = linha[4:-1].split("(")
        nome = partes[0]
        parametros = partes[1] if len(partes) > 1 else ""
        csharp_parametros = converter_parametros(parametros)
        return f'static void {nome}({csharp_parametros})\n{{'
#Converte a instrução return do Python para a mesma instrução em C# (return ...;).
    if linha.startswith("return "):
        return f'return {linha[7:]};'
# Detecta o tipo da variável (int, double, bool, string, List<T>) e gera a declaração apropriada em C#. Caso a variável já tenha sido declarada, apenas atualiza o valor.
    if "=" in linha and "==" not in linha:
        var, valor = linha.split("=", 1)
        var = var.strip()
        valor = valor.strip()

        if "int(input(" in valor:
            valor_csharp = "int.Parse(Console.ReadLine())"
            tipo = "int"
        elif "input(" in valor:
            valor_csharp = "Console.ReadLine()"
            tipo = "string"
        else:
            valor_csharp = valor
            tipo = detectar_tipo(valor)

        if tipo.startswith("List"):
            valor_csharp = f"new {tipo} {{ {valor[1:-1]} }}"

        if var not in variaveis_declaradas:
            variaveis_declaradas[var] = tipo
            return f'{tipo} {var} = {valor_csharp};'
        else:
            return f'{var} = {valor_csharp};'
#Trata linhas em branco como fim de bloco em C#, adicionando }.
    if linha == "":
        return "}"
#Se nenhum dos if for atendido, comenta a linha original de Python com // no C# indicando que não foi convertida.
    return "// " + linha

def converter_arquivo_python_para_csharp():
    root = tk.Tk()
    root.withdraw()
    caminho_entrada = filedialog.askopenfilename(
        title="Selecione o arquivo Python (.txt)",
        filetypes=[("Arquivos de Texto", "*.txt")]
    )

    if not caminho_entrada:
        print("Nenhum arquivo selecionado.")
        return

    with open(caminho_entrada, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    variaveis_declaradas = {}
    linhas_convertidas = [converter_python_para_csharp(linha, variaveis_declaradas) for linha in linhas]

    estrutura_csharp = [
        "using System;",
        "using System.Collections.Generic;",
        "",
        "namespace ProgramaConvertido",
        "{",
        "    class Program",
        "    {",
        "        static void Main(string[] args)",
        "        {",
        "            // Código convertido de Python para C#",
    ]

    for linha in linhas_convertidas:
        estrutura_csharp.append("            " + linha)

    estrutura_csharp += [
        "        }",
        "    }",
        "}"
    ]

    caminho_saida = filedialog.asksaveasfilename(
        defaultextension=".cs",
        filetypes=[("Arquivo C#", "*.cs")],
        title="Salvar arquivo convertido como"
    )

    if not caminho_saida:
        print("Arquivo não salvo.")
        return

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write('\n'.join(estrutura_csharp))

    print(f"Arquivo convertido salvo em: {caminho_saida}")

if __name__ == "__main__":
    converter_arquivo_python_para_csharp()