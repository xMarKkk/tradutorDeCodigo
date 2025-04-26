🛠️ Gerador de Analisador Léxico (Python → C#)
📌 1. Objetivo
O objetivo deste projeto é criar um script Python que gera automaticamente um arquivo em C# chamado AnalisadorLexico.cs.

Este arquivo implementa um analisador léxico simples, que lê um trecho de código Python digitado pelo usuário e separa em tokens, como:

🔢 Números (123, 45.67)

🆔 Identificadores (ex: variavel, nome_cliente)

➕➖ Operadores (+, -, *, /)

O projeto é uma base para estudos de compiladores e geração de código automática.

⚙️ 2. Funcionamento
🐍 Python Script (gerar_analisador_lexico_csharp.py)
Define o conteúdo do analisador léxico como uma grande string C#.

Cria um arquivo AnalisadorLexico.cs e escreve o conteúdo nele.

Informa o sucesso da operação no terminal.

💻 Código C# Gerado (AnalisadorLexico.cs)
Pede para o usuário digitar um código Python.

Usa expressões regulares (Regex) para identificar os tokens:

Números

Identificadores

Operadores

Salva os tokens em uma lista.

Imprime no console o tipo e o valor de cada token encontrado.

🔍 3. Observações Importantes
🚧 O analisador atual reconhece apenas estruturas básicas.

❌ Ainda não reconhece:

Palavras-chave reservadas (if, def, for, etc.)

Strings ("texto", 'texto')

Comentários (# isto é um comentário)

Delimitadores como (), {}, :

🔎 Caracteres não reconhecidos são classificados como Unknown.

⚡ Este projeto é um MVP (versão mínima viável) para facilitar melhorias futuras.
