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
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar:\n{e}")
        return None

def atualizar_interface(*args):
    operacao = var_operacao.get()
    combo_tipo.set('') 
    
    if operacao == "Entrada":
        combo_tipo['values'] = ["Churrasco Completo", "Coffee Break", "Mão de Obra", "Mão de Obra + Carne", "Outros"]
        lbl_cliente_fornecedor.config(text="Nome do Cliente:")
        lbl_nome_evento.config(text="Nome do Evento:")
        # Habilita campos exclusivos de Entrada
        entry_data_evento.config(state='normal')
        entry_convidados.config(state='normal')
        
    elif operacao == "Saída":
        combo_tipo['values'] = ["Mantimento", "Mão de Obra", "Conta (Aluguel/Contas em geral)", "Outros"]
        lbl_cliente_fornecedor.config(text="Fornecedor / Local:")
        lbl_nome_evento.config(text="Evento Vinculado:")
        # Desabilita e limpa campos exclusivos de Entrada
        entry_data_evento.delete(0, tk.END)
        entry_data_evento.config(state='disabled')
        entry_convidados.delete(0, tk.END)
        entry_convidados.config(state='disabled')

def salvar_registro():
    operacao = var_operacao.get()
    data_lancamento = entry_data_lancamento.get()
    tipo = combo_tipo.get()
    valor_texto = entry_valor.get()
    
    cliente_fornecedor = entry_cliente_fornecedor.get()
    nome_evento = entry_nome_evento.get()
    data_evento = entry_data_evento.get()
    convidados_texto = entry_convidados.get()

    if not operacao or not data_lancamento or not tipo or not valor_texto:
        messagebox.showwarning("Aviso", "Preencha os campos obrigatórios (Data, Tipo e Valor)!")
        return

    try:
        data_lancamento_fmt = datetime.strptime(data_lancamento, "%d/%m/%Y").strftime("%Y-%m-%d")
        valor_float = float(valor_texto.replace(',', '.'))   
        # Trata a data do evento (pode estar vazia em saídas)
        data_evento_fmt = None
        if data_evento and operacao == "Entrada":
            data_evento_fmt = datetime.strptime(data_evento, "%d/%m/%Y").strftime("%Y-%m-%d")
            
        # Trata o número de convidados (pode estar vazio)
        convidados_int = int(convidados_texto) if convidados_texto else None

    except ValueError:
        messagebox.showerror("Erro", "Verifique o formato das datas (DD/MM/YYYY) e se os números estão corretos!")
        return

    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        sql = """INSERT INTO transacoes 
                 (operacao, data_transacao, tipo, valor, cliente_fornecedor, nome_evento, data_evento, num_convidados) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (operacao, data_lancamento_fmt, tipo, valor_float, cliente_fornecedor, nome_evento, data_evento_fmt, convidados_int)
        
        try:
            cursor.execute(sql, valores)
            conexao.commit()
            messagebox.showinfo("Sucesso", "Registro salvo com sucesso!")
            
            # Limpa os campos para o próximo lançamento
            entry_valor.delete(0, tk.END)
            entry_cliente_fornecedor.delete(0, tk.END)
            entry_nome_evento.delete(0, tk.END)
            if operacao == "Entrada":
                entry_data_evento.delete(0, tk.END)
                entry_convidados.delete(0, tk.END)
            combo_tipo.set('')
            
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Erro: {e}")
        finally:
            cursor.close()
            conexao.close()

# Interface Gráfica
janela = tk.Tk()
janela.title("Gestão Financeira - Buffet")
janela.geometry("450x550")
janela.configure(padx=20, pady=20)

var_operacao = tk.StringVar(value="Entrada")
var_operacao.trace_add("write", atualizar_interface)

tk.Label(janela, text="Lançamento Financeiro", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

# Operação
tk.Label(janela, text="Operação:").grid(row=1, column=0, sticky="w", pady=5)
frame_op = tk.Frame(janela)
frame_op.grid(row=1, column=1, sticky="w")
tk.Radiobutton(frame_op, text="Entrada", variable=var_operacao, value="Entrada").pack(side="left")
tk.Radiobutton(frame_op, text="Saída", variable=var_operacao, value="Saída").pack(side="left")

# Data Lançamento
tk.Label(janela, text="Data (Pagamento):").grid(row=2, column=0, sticky="w", pady=5)
entry_data_lancamento = tk.Entry(janela, width=30)
entry_data_lancamento.insert(0, datetime.today().strftime("%d/%m/%Y"))
entry_data_lancamento.grid(row=2, column=1, pady=5)

# Tipo
tk.Label(janela, text="Categoria (Tipo):").grid(row=3, column=0, sticky="w", pady=5)
combo_tipo = ttk.Combobox(janela, state="readonly", width=27)
combo_tipo.grid(row=3, column=1, pady=5)

# Cliente / Fornecedor (Dinâmico)
lbl_cliente_fornecedor = tk.Label(janela, text="Nome do Cliente:")
lbl_cliente_fornecedor.grid(row=4, column=0, sticky="w", pady=5)
entry_cliente_fornecedor = tk.Entry(janela, width=30)
entry_cliente_fornecedor.grid(row=4, column=1, pady=5)

# Nome do Evento / Evento Vinculado (Dinâmico)
lbl_nome_evento = tk.Label(janela, text="Nome do Evento:")
lbl_nome_evento.grid(row=5, column=0, sticky="w", pady=5)
entry_nome_evento = tk.Entry(janela, width=30)
entry_nome_evento.grid(row=5, column=1, pady=5)

# Data do Evento (Só Entrada)
tk.Label(janela, text="Data do Evento:").grid(row=6, column=0, sticky="w", pady=5)
entry_data_evento = tk.Entry(janela, width=30)
entry_data_evento.grid(row=6, column=1, pady=5)

# Número de Convidados (Só Entrada)
tk.Label(janela, text="Nº Convidados:").grid(row=7, column=0, sticky="w", pady=5)
entry_convidados = tk.Entry(janela, width=30)
entry_convidados.grid(row=7, column=1, pady=5)

# Valor
tk.Label(janela, text="Valor (R$):").grid(row=8, column=0, sticky="w", pady=5)
entry_valor = tk.Entry(janela, width=30)
entry_valor.grid(row=8, column=1, pady=5)

# Botão Salvar
tk.Button(janela, text="Salvar Registro", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=salvar_registro).grid(row=9, column=0, columnspan=2, pady=25, ipadx=50)

# Inicializa os rótulos e campos corretamente
atualizar_interface()

janela.mainloop()