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
        
        entry_data_evento.config(state='normal')
        entry_convidados.config(state='normal')
        
    elif operacao == "Saída":
        combo_tipo['values'] = ["Mantimento", "Mão de Obra", "Conta (Aluguel/Contas em geral)", "Outros"]
        lbl_cliente_fornecedor.config(text="Fornecedor / Local:")
        lbl_nome_evento.config(text="Evento Vinculado:")
        
        entry_data_evento.delete(0, tk.END)
        entry_data_evento.config(state='disabled')
        entry_convidados.delete(0, tk.END)
        entry_convidados.config(state='disabled')

def carregar_tabela():
    #Busca os últimos registros no banco e exibe na tabela.

    # Limpa a tabela antes de carregar
    for item in tabela.get_children():
        tabela.delete(item)
        
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        comando_sql = "SELECT id, operacao, data_transacao, tipo, valor, nome_evento FROM transacoes ORDER BY id DESC LIMIT 15"
        
        try:
            cursor.execute(comando_sql)
            linhas = cursor.fetchall()
            for linha in linhas:
                id_reg, op, data_db, tipo, valor, evento = linha
                data_br = data_db.strftime("%d/%m/%Y") if data_db else ""
                valor_br = f"R$ {valor:.2f}".replace('.', ',')
                tabela.insert("", "end", values=(id_reg, data_br, op, tipo, evento, valor_br))
        except Exception as e:
            print(f"Erro ao carregar tabela: {e}")
        finally:
            cursor.close()
            conexao.close()

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
        
        data_evento_fmt = None
        if data_evento and operacao == "Entrada":
            data_evento_fmt = datetime.strptime(data_evento, "%d/%m/%Y").strftime("%Y-%m-%d")
            
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
            
            entry_valor.delete(0, tk.END)
            entry_cliente_fornecedor.delete(0, tk.END)
            entry_nome_evento.delete(0, tk.END)
            if operacao == "Entrada":
                entry_data_evento.delete(0, tk.END)
                entry_convidados.delete(0, tk.END)
            combo_tipo.set('')
            carregar_tabela()
            
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Erro: {e}")
        finally:
            cursor.close()
            conexao.close()

# Interface Gráfica
janela = tk.Tk()
janela.title("Gestão Financeira - Buffet")
janela.geometry("650x650") # Janela um pouco maior para caber a tabela
janela.configure(padx=20, pady=20)

var_operacao = tk.StringVar(value="Entrada")
var_operacao.trace_add("write", atualizar_interface)

tk.Label(janela, text="Lançamento Financeiro", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))

# --- FRAME FORMULÁRIO ---
frame_form = tk.Frame(janela)
frame_form.grid(row=1, column=0, sticky="w")

tk.Label(frame_form, text="Operação:").grid(row=0, column=0, sticky="w", pady=5)
frame_op = tk.Frame(frame_form)
frame_op.grid(row=0, column=1, sticky="w")
tk.Radiobutton(frame_op, text="Entrada", variable=var_operacao, value="Entrada").pack(side="left")
tk.Radiobutton(frame_op, text="Saída", variable=var_operacao, value="Saída").pack(side="left")

tk.Label(frame_form, text="Data (Pagamento):").grid(row=1, column=0, sticky="w", pady=5)
entry_data_lancamento = tk.Entry(frame_form, width=30)
entry_data_lancamento.insert(0, datetime.today().strftime("%d/%m/%Y"))
entry_data_lancamento.grid(row=1, column=1, pady=5)

tk.Label(frame_form, text="Categoria (Tipo):").grid(row=2, column=0, sticky="w", pady=5)
combo_tipo = ttk.Combobox(frame_form, state="readonly", width=27)
combo_tipo.grid(row=2, column=1, pady=5)

lbl_cliente_fornecedor = tk.Label(frame_form, text="Nome do Cliente:")
lbl_cliente_fornecedor.grid(row=3, column=0, sticky="w", pady=5)
entry_cliente_fornecedor = tk.Entry(frame_form, width=30)
entry_cliente_fornecedor.grid(row=3, column=1, pady=5)

lbl_nome_evento = tk.Label(frame_form, text="Nome do Evento:")
lbl_nome_evento.grid(row=4, column=0, sticky="w", pady=5)
entry_nome_evento = tk.Entry(frame_form, width=30)
entry_nome_evento.grid(row=4, column=1, pady=5)

tk.Label(frame_form, text="Data do Evento:").grid(row=5, column=0, sticky="w", pady=5)
entry_data_evento = tk.Entry(frame_form, width=30)
entry_data_evento.grid(row=5, column=1, pady=5)

tk.Label(frame_form, text="Nº Convidados:").grid(row=6, column=0, sticky="w", pady=5)
entry_convidados = tk.Entry(frame_form, width=30)
entry_convidados.grid(row=6, column=1, pady=5)

tk.Label(frame_form, text="Valor (R$):").grid(row=7, column=0, sticky="w", pady=5)
entry_valor = tk.Entry(frame_form, width=30)
entry_valor.grid(row=7, column=1, pady=5)

tk.Button(frame_form, text="Salvar Registro", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=salvar_registro).grid(row=8, column=0, columnspan=2, pady=15, ipadx=30)

# --- FRAME TABELA (Histórico Recente) ---
tk.Label(janela, text="Últimos Lançamentos", font=("Arial", 12, "bold")).grid(row=2, column=0, pady=(10, 5), sticky="w")

colunas = ("ID", "Data", "Operação", "Tipo", "Evento", "Valor")
tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=8)

# Formatando as colunas
tabela.heading("ID", text="ID")
tabela.column("ID", width=30, anchor="center")
tabela.heading("Data", text="Data")
tabela.column("Data", width=80, anchor="center")
tabela.heading("Operação", text="Operação")
tabela.column("Operação", width=70, anchor="center")
tabela.heading("Tipo", text="Tipo")
tabela.column("Tipo", width=120)
tabela.heading("Evento", text="Evento")
tabela.column("Evento", width=150)
tabela.heading("Valor", text="Valor")
tabela.column("Valor", width=80, anchor="e")

tabela.grid(row=3, column=0, sticky="ew")

# Adicionando barra de rolagem
scrollbar = ttk.Scrollbar(janela, orient="vertical", command=tabela.yview)
tabela.configure(yscroll=scrollbar.set)
scrollbar.grid(row=3, column=1, sticky="ns")

atualizar_interface()
carregar_tabela() 
janela.mainloop()