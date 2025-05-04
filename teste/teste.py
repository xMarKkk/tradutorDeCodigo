# Lista de palavras-chave C#
csharp_keywords = {
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

def encontrar_palavras_chave_csharp(codigo: str) -> list:
    tokens = codigo.split()
    return [token for token in tokens if token in csharp_keywords]

# Exemplo de uso
codigo_exemplo = """
public class Pessoa {
    private string nome;
    public void Falar() {
        Console.WriteLine("Olá!");
    }
}
"""

palavras_chave_encontradas = encontrar_palavras_chave_csharp(codigo_exemplo)
print("Palavras-chave C# encontradas:", palavras_chave_encontradas)
