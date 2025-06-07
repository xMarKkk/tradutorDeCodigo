import re

python_identificadores = {
    "False", "None", "True", "and", "as", "assert", "async", "await", "break",
    "class", "continue", "def", "del", "elif", "else", "except", "finally", "for",
    "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or",
    "pass", "raise", "return", "try", "while", "with", "yield"
}

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        return f"[{self.tipo}] {self.valor}"

def remover_comentarios(codigo):
    return re.sub(r'#.*', '', codigo)

def obter_padrao_tokens():
    padroes_token = [
        ('String', r'(\".*?\"|\'.*?\')'),
        ('Number', r'\b\d+(\.\d+)?\b'),
        ('Operator', r'(==|!=|<=|>=|\+|\-|\*{1,2}|//|/|%|=|>|<)'),
        ('Delimiter', r'[()\[\]{},:;.]'),
        ('Identifier', r'[a-zA-Z_][a-zA-Z0-9_]*')
    ]
    regex_list = [f'(?P<{nome}>{regex})' for nome, regex in padroes_token]
    return re.compile('|'.join(regex_list))

def gerar_tokens(codigo, padrao_regex):
    tokens = []
    for match in padrao_regex.finditer(codigo):
        tipo = match.lastgroup
        valor = match.group()

        if tipo == 'Identifier' and valor in python_identificadores:
            tipo = 'Keyword'

        tokens.append(Token(tipo, valor))
    return tokens

def agrupar_tokens(tokens):
    agrupado = {
        '[Palavra-chave]': [],
        '[Identificador]': [],
        '[Operadores]': [],
        '[Numeros]': [],
        '[Strings]': [],
        '[Delimitadores]': [],
        '[Desconhecido]': []
    }

    for token in tokens:
        if token.tipo == 'Keyword':
            agrupado['[Palavra-chave]'].append(token.valor)
        elif token.tipo == 'Identifier':
            agrupado['[Identificador]'].append(token.valor)
        elif token.tipo == 'Operator':
            agrupado['[Operadores]'].append(token.valor)
        elif token.tipo == 'Number':
            agrupado['[Numeros]'].append(token.valor)
        elif token.tipo == 'String':
            agrupado['[Strings]'].append(token.valor)
        elif token.tipo == 'Delimiter':
            agrupado['[Delimitadores]'].append(token.valor)
        else:
            agrupado['[Desconhecido]'].append(token.valor)

    return agrupado

def analisar_codigo_python(codigo):
    codigo_limpo = remover_comentarios(codigo)
    padrao = obter_padrao_tokens()
    tokens = gerar_tokens(codigo_limpo, padrao)
    agrupado = agrupar_tokens(tokens)
    return agrupado
