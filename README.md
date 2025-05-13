# Analisador Léxico para C# com Suporte Aprimorado

Este projeto é um analisador léxico (lexer) desenvolvido em Python para processar código-fonte em C#. Ele identifica tokens como palavras-chave, identificadores, números, strings, operadores e delimitadores, além de remover comentários. O código foi aprimorado a partir de uma base existente, com adições significativas de funcionalidades e melhorias na precisão.

## Funcionalidades Principais

✅ **Suporte a Comentários**  
Remove comentários de linha (`//`) e bloco (`/* ... */`) do código-fonte antes da análise.

✅ **Delimitadores Reconhecidos**  
Identifica corretamente delimitadores como `()`, `{}`, `[]`, `,`, `:`, `;` e `.`.

✅ **Tokens Mais Precisos**  
Regex aprimorado para:
- Números (inteiros, decimais, notação científica)
- Strings (incluindo caracteres escapados e verbatim `@""`)
- Operadores compostos (`++`, `==`, `=>`, etc.)
- Identificadores Unicode

✅ **Classificação de Tokens**  
Agrupa os tokens em categorias para visualização clara:
- Palavras-chave
- Identificadores
- Operadores
- Números
- Strings
- Delimitadores

## Como Usar

### Pré-requisitos
- Python 3.6 ou superior

### Instalação
```bash
git clone https://github.com/seu-usuario/analisador-lexico-csharp.git
cd analisador-lexico-csharp