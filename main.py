def gerar_analisador_lexico_csharp():
    codigo_csharp = """
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

class Program
{
    enum TokenType
    {
        Number,
        Identifier,
        Operator,
        Unknown
    }

    struct Token
    {
        public TokenType Type;
        public string Value;

        public Token(TokenType type, string value)
        {
            Type = type;
            Value = value;
        }

        public override string ToString()
        {
            return $"[{Type}] {Value}";
        }
    }

    static void Main()
    {
        Console.WriteLine("Digite o código Python:");
        string input = Console.ReadLine();

        List<Token> tokens = Analyze(input);

        foreach (var token in tokens)
        {
            Console.WriteLine(token);
        }
    }

    static List<Token> Analyze(string input)
    {
        var tokens = new List<Token>();

        var tokenPatterns = new Dictionary<TokenType, string>()
        {
            { TokenType.Number, @"\\\\d+(\\\\.\\\\d+)?" },
            { TokenType.Identifier, @"[a-zA-Z_][a-zA-Z0-9_]*" },
            { TokenType.Operator, @"[\\\\+\\\\-\\\\*/]" }
        };

        string pattern = string.Join("|", tokenPatterns.Values);
        var regex = new Regex(pattern);
        var matches = regex.Matches(input);

        foreach (Match match in matches)
        {
            TokenType type = TokenType.Unknown;
            foreach (var pair in tokenPatterns)
            {
                if (Regex.IsMatch(match.Value, $"^{pair.Value}$"))
                {
                    type = pair.Key;
                    break;
                }
            }
            tokens.Add(new Token(type, match.Value));
        }

        return tokens;
    }
}
"""
    # Salvando o código em um arquivo
    with open('AnalisadorLexico.cs', 'w', encoding='utf-8') as arquivo:
        arquivo.write(codigo_csharp)

    print("Arquivo 'AnalisadorLexico.cs' gerado com sucesso!")

# Executa a função
gerar_analisador_lexico_csharp()
