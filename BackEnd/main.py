###As palavras-chave são identificadores predefinidos e reservados que têm significados especiais para o compilador. Eles não podem ser usados como identificadores em seu programa, a menos que incluam @ como um prefixo. Por exemplo, @if é um identificador válido, mas if não é porque if é uma palavra-chave.


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


### Uma palavra-chave contextual é usada para fornecer um significado específico no código, mas não é uma palavra reservada em C#. Algumas palavras-chave contextuais, como partial e where, têm significados especiais em dois ou mais contextos.

csharp_contextuais = {
    "add", "allows", "alias", "and", "ascending", "args", "async", "await", "by",
    "descending", "dynamic", "equals", "extension", "field", "file", "from", "get",
    "global", "group", "init", "into", "join", "let", "managed", "nameof", "nint",
    "not", "notnull", "nuint", "on", "or", "orderby", "partial", "record", "remove",
    "required", "scoped", "select", "set", "unmanaged", "value", "var", "when",
    "where", "with", "yield"
}

start_class_csharp = """

        public class Start {
            private string nome;
            public void Falar() {
            Console.WriteLine("Olá!");
        }
        }
"""

def encontrar_palavras_chave_csharp(codigo: str) -> list:
    tokens = codigo.split()
    return [token for token in tokens if token in csharp_identificadores]

palavras_chave_encontradas = encontrar_palavras_chave_csharp(start_class_csharp)
print("Palavras-chave C# encontradas:", palavras_chave_encontradas)