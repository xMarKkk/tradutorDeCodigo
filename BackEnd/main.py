import tkinter as tk
from tkinter import filedialog
import re


def detectar_tipo(valor):
    valor = valor.strip()
    if valor.startswith("\"") or valor.startswith("'"):
        return "string"
    elif valor.lower() in ["true", "false"]:
        return "bool"
    elif re.match(r"^\d+\.\d+$", valor):
        return "double"
    elif re.match(r"^\d+$", valor):
        return "int"
    elif valor.startswith("[") and valor.endswith("]"):
        elementos = [e.strip() for e in valor[1:-1].split(",") if e.strip()]
        if not elementos:
            return "List<object>"
        tipo_elemento = detectar_tipo(elementos[0])
        return f"List<{tipo_elemento}>"
    elif "int.Parse" in valor:
        return "int"
    elif "Console.ReadLine()" in valor:
        return "string"
    else:
        return "var"


def converter_parametros(param_str):
    params = [p.strip() for p in param_str.split(",") if p.strip()]
    csharp_params = [f"int {p}" for p in params]
    return ", ".join(csharp_params)


def converter_operadores(condicao):
    condicao = condicao.replace(" and ", " && ")
    condicao = condicao.replace(" or ", " || ")
    condicao = condicao.replace(" not ", " !")
    return condicao


def converter_selenium(linha):
    mapeamento = {
        "webdriver.Chrome()": "new ChromeDriver()",
        "webdriver.Firefox()": "new FirefoxDriver()",
        "webdriver.Edge()": "new EdgeDriver()",
        ".get(": ".Navigate().GoToUrl(",
        ".find_element_by_id(": ".FindElement(By.Id(",
        ".find_element_by_name(": ".FindElement(By.Name(",
        ".find_element_by_xpath(": ".FindElement(By.XPath(",
        ".find_element_by_css_selector(": ".FindElement(By.CssSelector(",
        ".click()": ".Click()",
        ".send_keys(": ".SendKeys(",
        ".quit()": ".Quit()",
        ".close()": ".Close()"
    }

    for py, cs in mapeamento.items():
        if py in linha:
            linha = linha.replace(py, cs)

    return linha


def converter_python_para_csharp(linha, variaveis_declaradas, indent_nivel):
    linha_original = linha
    linha = linha.strip()

    # Conversão Selenium
    linha = converter_selenium(linha)

    if linha.startswith("print("):
        conteudo = linha[6:-1]
        return indent_nivel * "    " + f'Console.WriteLine({conteudo});'

    if "input(" in linha:
        var, valor = linha.split("=", 1)
        var = var.strip()
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
            return indent_nivel * "    " + f'{tipo} {var} = {valor_csharp}; // {prompt}'
        else:
            return indent_nivel * "    " + f'{var} = {valor_csharp}; // {prompt}'

    if linha.startswith("if "):
        condicao = converter_operadores(linha[3:-1])
        return indent_nivel * "    " + f'if ({condicao})\n' + indent_nivel * "    " + "{"

    if linha.startswith("else"):
        return indent_nivel * "    " + "} else {"

    if linha.startswith("while "):
        condicao = converter_operadores(linha[6:-1])
        return indent_nivel * "    " + f'while ({condicao})\n' + indent_nivel * "    " + "{"

    if linha.startswith("for ") and "in range" in linha:
        var = linha.split(" ")[1]
        num = linha.split("range(")[1].split(")")[0]
        variaveis_declaradas[var] = "int"
        return indent_nivel * "    " + f'for (int {var} = 0; {var} < {num}; {var}++)\n' + indent_nivel * "    " + "{"

    if linha.startswith("def "):
        partes = linha[4:-1].split("(")
        nome = partes[0]
        parametros = partes[1] if len(partes) > 1 else ""
        csharp_parametros = converter_parametros(parametros)
        return indent_nivel * "    " + f'static void {nome}({csharp_parametros})\n' + indent_nivel * "    " + "{"

    if linha.startswith("return "):
        return indent_nivel * "    " + f'return {linha[7:]};'

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
            valor_csharp = converter_selenium(valor)
            tipo = detectar_tipo(valor)

        if tipo.startswith("List"):
            valor_csharp = f"new {tipo} {{ {valor[1:-1]} }}"

        if var not in variaveis_declaradas:
            variaveis_declaradas[var] = tipo
            return indent_nivel * "    " + f'{tipo} {var} = {valor_csharp};'
        else:
            return indent_nivel * "    " + f'{var} = {valor_csharp};'

    if linha == "":
        return indent_nivel * "    " + "}"

    return indent_nivel * "    " + "// " + linha_original


def calcular_indentacao(linha):
    return (len(linha) - len(linha.lstrip(' '))) // 4


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
    linhas_convertidas = []
    indent_nivel_anterior = 0

    for linha in linhas:
        indent_nivel_atual = calcular_indentacao(linha)

        if indent_nivel_atual < indent_nivel_anterior:
            for _ in range(indent_nivel_anterior - indent_nivel_atual):
                linhas_convertidas.append("    " * (indent_nivel_anterior - 1) + "}")

        linha_convertida = converter_python_para_csharp(linha, variaveis_declaradas, indent_nivel_atual)
        linhas_convertidas.append(linha_convertida)

        indent_nivel_anterior = indent_nivel_atual

    while indent_nivel_anterior > 0:
        linhas_convertidas.append("    " * (indent_nivel_anterior - 1) + "}")
        indent_nivel_anterior -= 1

    estrutura_csharp = [
        "using System;",
        "using System.Collections.Generic;",
        "using OpenQA.Selenium;",
        "using OpenQA.Selenium.Chrome;",
        "using OpenQA.Selenium.Firefox;",
        "using OpenQA.Selenium.Edge;",
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
        estrutura_csharp.append(linha)

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
