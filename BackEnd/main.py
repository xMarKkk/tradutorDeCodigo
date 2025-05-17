import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


## a letra 'r'  significa que só vai ler o arquivo 'R'--->Read---->Ler
## a letra 'w'  significa que  vai ler o arquivo e você pode substituir o seu valor 'W'--->Write---->Escrever
## a letra 'a'  significa que vai adicionar informação ao arquivo 'A'--->Append---->Adicionar
## usar read() para arquivos simples
## usar readlines() para arquivos maiores



caminho_txt = r"C:\\TradutorDeCodigo\\assets\\arquivo.txt"

# Indificadores a serem substituidos 
substituicoes = {
    "Def": "public class",
    "Name": "Nome",
    "Yeras": "Idade"
}


with open(caminho_txt, "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()


for original, novo in substituicoes.items():
    conteudo = conteudo.replace(original, novo)


root = tk.Tk()
root.withdraw()  

pasta_destino = filedialog.askdirectory(title="teste.txt")

if pasta_destino:
   
    nome_base = os.path.splitext(os.path.basename(caminho_txt))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_base}_modificado_{timestamp}.txt"
    
    
    caminho_saida = os.path.join(pasta_destino, nome_arquivo)

  
    with open(caminho_saida, "w", encoding="utf-8") as novo_arquivo:
        novo_arquivo.write(conteudo)

    print(f"Arquivo salvo com sucesso em: {caminho_saida}")
else:
    print("Nenhuma pasta foi selecionada. Operação cancelada.")