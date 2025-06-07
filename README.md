# Conversor Python → C# com Interface Gráfica (PyQt6) e Analisador Léxico Integrado 🚀

Este projeto apresenta uma ferramenta prática desenvolvida em Python que permite converter automaticamente scripts escritos em **Python** para código equivalente em **C#**, facilitando o trabalho de equipes técnicas com diferentes tecnologias. Além disso, possui uma interface gráfica intuitiva desenvolvida com **PyQt6** e um analisador léxico embutido.

---

## 📌 Funcionalidades

* **Conversão Automática**:

  * `print()` → `Console.WriteLine()`
  * Estruturas condicionais e loops (`if`, `for`, `while`)
  * Inferência automática de tipos (`int`, `double`, `bool`, `string`, `List<int>`)

* **Interface Gráfica (PyQt6)**:

  * Entrada direta de código Python.
  * Importação rápida de arquivos externos.
  * Visualização imediata do código C# gerado.

* **Analisador Léxico**:

  * Remoção automática de comentários.
  * Identificação clara dos tokens utilizados no código original.

---

## 🛠️ Estrutura Técnica

* **Inferência de Tipos**: Reconhece automaticamente o tipo das variáveis.
* **Analisador Léxico**: Utiliza expressões regulares para identificar tokens.
* **Interface gráfica**: Desenvolvida com PyQt6 para facilitar o uso.

---

## 🔧 Como usar?

1. Instale as dependências necessárias:

```bash
pip install PyQt6
```

2. Rode a aplicação:

```bash
python conversor.py
```

3. Insira ou importe seu código Python e clique em "Converter e Analisar".

---

## 📂 Estrutura do Projeto

```
📁 Projeto
├── 📄 main.py            # Aplicação principal
├── 📄 analisador_lexico.py    # Funções auxiliares de análise léxica
├── 📄 entrada.txt      # Exemplo de entrada Python (opcional)
└── 📄 README.md               # Este arquivo
```

---

## ✅ Benefícios Principais

* **Economia de tempo**: Conversão automática evita retrabalho manual.
* **Precisão**: Inferência inteligente melhora a qualidade do código gerado.
* **Facilidade de Uso**: Interface gráfica amigável, ideal para qualquer nível de usuário.

---

## 📝 Licença

Este projeto é aberto para fins acadêmicos e educativos.

---

🎯 **Palavras-chave**: Python, C#, Transpilação, Interface Gráfica, PyQt6, Analisador Léxico
