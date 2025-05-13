import re

# Definir as palavras-chave de C#
csharp_identificadores = {
    "abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char",
    "checked", "class", "const", "continue", "decimal", "default", "delegate",
    "do", "double", "else", "enum", "event", "explicit", "extern", "false",
    "finally", "fixed", "float", "for", "foreach", "goto", "if", "implicit",
    "in", "int", "interface", "internal", "is", "lock", "long", "namespace",
    "new", "null", "object", "operator", "out", "override", "params", "private",
    "protected", "public", "readonly", "ref", "return", "sbyte", "sealed",
    "short", "sizeof", "stackalloc", "static", "string", "struct", "switch",
    "this", "throw", "true", "try", "typeof", "uint", "ulong", "unchecked",
    "unsafe", "ushort", "using", "virtual", "void", "volatile", "while"
}


# Será usado quando começarmos a implementar a analise sintática
# csharp_contextuais = {
#     "add", "allows", "alias", "and", "ascending", "args", "async", "await", "by",
#     "descending", "dynamic", "equals", "extension", "field", "file", "from", "get",
#     "global", "group", "init", "into", "join", "let", "managed", "nameof", "nint",
#     "not", "notnull", "nuint", "on", "or", "orderby", "partial", "record", "remove",
#     "required", "scoped", "select", "set", "unmanaged", "value", "var", "when",
#     "where", "with", "yield"
# }


# Definindo o tipo de token
class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        return f"[{self.tipo}] {self.valor}"


# Função para remover comentários de linha e bloco do código
def remover_comentarios(codigo):
    # Remover comentários de linha (//)
    codigo = re.sub(r'//.*', '', codigo)
    # Remover comentários de múltiplas linhas (/* ... */)
    codigo = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
    return codigo

# Função para identificar os tokens no código
def analisar_codigo(codigo):
    # Primeiro, remover os comentários do código
    codigo = remover_comentarios(codigo)


    padroes_token = [
        ('String', r'@?"(?:[^"\\]|\\.)*"'),
        ('Number', r'-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?[fdm]?\b'),
        ('Operator', r'(==|!=|<=|>=|\+\+|\+|--|-|\*=|\*|/=|/|%=|%|&&|&=|&=|\^=|\^|>>=|>>|<<=|<<|->|=>|~|!)'), 
        ('Delimiter', r'[(){}[\],:;.]'),
        ('Identifier', r'\w+')
    ]

    # Construção segura da regex
    regex_list = [f'(?P<{nome}>{regex})' for nome, regex in padroes_token]
    padrao = re.compile('|'.join(regex_list), flags=re.UNICODE)

    tokens = []
    
    for match in padrao.finditer(codigo):
        tipo = match.lastgroup
        valor = match.group()
        
        if tipo == 'Identifier' and valor in csharp_identificadores:
            tipo = 'Keyword'
            
        tokens.append(Token(tipo, valor))

    return tokens

# Função para agrupar os tokens por tipo e exibir
def exibir_tokens_agrupados(tokens):
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
    
    for tipo, lista in agrupado.items():
        if lista:
            print(f"{tipo}: {', '.join(lista)}")

# Função para ler o código do usuário e analisar
def main():
    # Exemplo de código C# (pode ser modificado pelo usuário)
    codigo = """
    // Este é um comentário de linha
    public class Start {
        private string nome; // Declaração da variável nome
        public void Falar() {
            Console.WriteLine("Olá!"); // Exibe a saudação
        }
    }

    /* Este é um comentário
       de múltiplas linhas */
    public void OutroMetodo() {
        Console.WriteLine("Outro código!");
    }


    var lista = new List<string>();
    double x = -3.14e-5f;
    string msg = @"Texto com \n escape";
    if (x <= 10 && x != 0) {}
    """

    # Chama a função para analisar o código
    tokens = analisar_codigo(codigo)

    # Exibe os tokens agrupados
    exibir_tokens_agrupados(tokens)

# Chama a função principal
if __name__ == '__main__':
    main()
