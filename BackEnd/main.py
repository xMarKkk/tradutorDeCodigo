import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

## a letra 'r'  significa que só vai ler o arquivo 'R'--->Read---->Ler
## a letra 'w'  significa que  vai ler o arquivo e você pode substituir o seu valor 'W'--->Write---->Escrever
## a letra 'a'  significa que vai adicionar informação ao arquivo 'A'--->Append---->Adicionar
## usar read() para arquivos simples
## usar readlines() para arquivos maiores



# Inicializa o tkinter sem exibir a janela principal
root = tk.Tk()
root.withdraw()

# Abre janela para escolher o arquivo .txt de entrada
caminho_entrada = filedialog.askopenfilename(
    title="Selecione o arquivo .txt",
    filetypes=[("Arquivos de texto", "*.txt")]
)

if not caminho_entrada:
    print("Nenhum arquivo foi selecionado. Operação cancelada.")
    exit()

# Dicionário com palavras a substituir (tudo no texto)
substituicoes = {
    "as": "as",
    "super()": "base",
    "bool": "bool",
    "break": "break",
    "int": "int",
    "case": "case",
    "except": "catch",
    "str": "string",
    "class": "class",
    "UPPERCASE": "const",
    "continue": "continue",
    "decimal.Decimal": "decimal",
    "default": "default",
    "function && functools.partial": "delegate",
    "while True + break": "do",
    "float": "double",
    "else": "else",
    "enum.Enum": "enum",
    "callback": "event",
    "int(), float()": "explicit",
    "ctypes": "extern",
    "False": "false",
    "finally": "finally",
    "for": "foreach",
    "None": "null",
    "if": "if",
    "conversão automática": "implicit",
    "in": "in",
    "abc.ABC": "interface",
    "_ (convenção)": "internal",
    "__ (convenção)": "private",
    "is": "is",
    "with threading.Lock()": "lock",
    "módulo ou pacote": "namespace",
    "__init__": "new",
    "object": "object",
    "__add__, __eq__, etc.": "operator",
    "retorno múltiplo": "out",
    "override normal": "override",
    "*args": "params",
    "padrão": "public",
    "propriedade de leitura": "readonly",
    "por referência (natural em objetos)": "ref",
    "return": "return",
    "sys.getsizeof()": "sizeof",
    "@staticmethod": "static",
    "dataclass ou namedtuple": "struct",
    "match": "switch",
    "self": "this",
    "raise": "throw",
    "True": "true",
    "try": "try",
    "type()": "typeof",
    "with": "using",
    "métodos padrão": "virtual",
    "None (retorno)": "void",
    "lock / thread-safe controle": "volatile",
    "while": "while"
}


with open(caminho_entrada, "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()


for original, novo in substituicoes.items():
    conteudo = conteudo.replace(original, str(novo))  


# Regex para encontrar literais de string ('...' ou "...")
# padrao_string = r"(['\"])(.*?)(\1)"

# def substituir_em_string(match):
  #  aspas = match.group(1)
   # texto = match.group(2)
   # for original, novo in substituicoes.items():
    # texto = texto.replace(original, novo)
    # return f"{aspas}{texto}{aspas}"

# Aplica substituições apenas dentro de literais de string
# conteudo_modificado = re.sub(padrao_string, substituir_em_string, conteudo)    


pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar o novo arquivo")

if not pasta_destino:
    print("Nenhuma pasta foi selecionada. Operação cancelada.")
    exit()

nome_base = os.path.splitext(os.path.basename(caminho_entrada))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo = f"{nome_base}_modificado_{timestamp}.txt"
caminho_saida = os.path.join(pasta_destino, nome_arquivo)


with open(caminho_saida, "w", encoding="utf-8") as novo_arquivo:
    novo_arquivo.write(conteudo)

print(f"Arquivo salvo com sucesso em: {caminho_saida}")

