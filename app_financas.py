import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

load_dotenv()

def conectar_db():
    try:
        conexao = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return conexao
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao MySQL:\n{e}")
        return None


def atualizar_tipos(*args):
    #Atualiza a lista suspensa de Tipos com base na Operação escolhida.
    operacao = var_operacao.get()
    combo_tipo.set('') 

    if operacao == "Entrada":
        combo_tipo['values'] = ["Churrasco Completo", "Coffee Break", "Mão de Obra", "Mão de Obra + Carne", "Outros"]
    elif operacao == "Saída":
        combo_tipo['values'] = ["Mantimento", "Mão de Obra", "Conta (Aluguel/Contas em geral)", "Outros"]


def salvar_registro():
    #Valida os dados e salva no banco MySQL.
    operacao = var_operacao.get()
    data_texto = entry_data.get()
    tipo = combo_tipo.get()
    valor_texto = entry_valor.get()

    # Validação básica
    if not operacao or not data_texto or not tipo or not valor_texto:
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return

    try:
        # Converte a data de DD/MM/YYYY para YYYY-MM-DD (formato do MySQL)
        data_formatada = datetime.strptime(data_texto, "%d/%m/%Y").strftime("%Y-%m-%d")
        # Converte o valor para float, substituindo vírgula por ponto se necessário
        valor_float = float(valor_texto.replace(',', '.'))
    except ValueError:
        messagebox.showerror("Erro", "Formato de data (DD/MM/YYYY) ou valor inválido!")
        return

    # Inserção no Banco
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        sql = "INSERT INTO transacoes (operacao, data_transacao, tipo, valor) VALUES (%s, %s, %s, %s)"
        valores = (operacao, data_formatada, tipo, valor_float)
        
        try:
            cursor.execute(sql, valores)
            conexao.commit()
            messagebox.showinfo("Sucesso", "Registro salvo com sucesso!")
            # Limpa os campos de valor após salvar (mantém a data para facilitar lançamentos em lote)
            entry_valor.delete(0, tk.END)
            combo_tipo.set('')
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Erro: {e}")
        finally:
            cursor.close()
            conexao.close()

#INTEFACE GRÁFICA
janela = tk.Tk()
janela.title("Gestão Financeira - Buffet")
janela.geometry("400x350")
janela.configure(padx=20, pady=20)

# Variáveis
var_operacao = tk.StringVar(value="Entrada")
var_operacao.trace_add("write", atualizar_tipos) # Chama a função sempre que a operação mudar

# Título
tk.Label(janela, text="Novo Lançamento", font=("Arial", 16, "bold")).pack(pady=(0, 20))

# Frame de Operação (Radio Buttons)
frame_operacao = tk.Frame(janela)
frame_operacao.pack(fill="x", pady=5)
tk.Label(frame_operacao, text="Operação:", width=10, anchor="w").pack(side="left")
tk.Radiobutton(frame_operacao, text="Entrada", variable=var_operacao, value="Entrada").pack(side="left", padx=10)
tk.Radiobutton(frame_operacao, text="Saída", variable=var_operacao, value="Saída").pack(side="left")

# Data
frame_data = tk.Frame(janela)
frame_data.pack(fill="x", pady=5)
tk.Label(frame_data, text="Data:", width=10, anchor="w").pack(side="left")
entry_data = tk.Entry(frame_data)
entry_data.insert(0, datetime.today().strftime("%d/%m/%Y")) # Preenche com a data de hoje
entry_data.pack(side="left", fill="x", expand=True)

# Tipo
frame_tipo = tk.Frame(janela)
frame_tipo.pack(fill="x", pady=5)
tk.Label(frame_tipo, text="Tipo:", width=10, anchor="w").pack(side="left")
combo_tipo = ttk.Combobox(frame_tipo, state="readonly")
combo_tipo.pack(side="left", fill="x", expand=True)
atualizar_tipos() # Popula os valores iniciais

# Valor
frame_valor = tk.Frame(janela)
frame_valor.pack(fill="x", pady=5)
tk.Label(frame_valor, text="Valor (R$):", width=10, anchor="w").pack(side="left")
entry_valor = tk.Entry(frame_valor)
entry_valor.pack(side="left", fill="x", expand=True)

# Botão Salvar
tk.Button(janela, text="Salvar Registro", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=salvar_registro).pack(pady=25, fill="x")

janela.mainloop()