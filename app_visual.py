import tkinter as tk
from tkinter import ttk, messagebox
import requests

# URL base onde a sua API está rodando
API_URL = "http://127.0.0.1:8000"

class AplicativoFaculdade:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reserva de Salas")
        self.root.geometry("400x250") # Começa menor para a tela de login
        self.root.eval('tk::PlaceWindow . center') # Centraliza na tela
        
        # Variável para guardar o usuário logado
        self.usuario_logado = ""
        
        # Inicia mostrando a tela de login
        self.tela_login()

    # --- TELA 1: LOGIN E SENHA ---
    def tela_login(self):
        # Container do Login
        self.frame_login = ttk.Frame(self.root, padding=20)
        self.frame_login.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(self.frame_login, text="Acesso ao Sistema", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Campo Usuário
        ttk.Label(self.frame_login, text="Usuário (E-mail):").pack(anchor=tk.W)
        self.ent_usuario = ttk.Entry(self.frame_login, width=30)
        self.ent_usuario.pack(pady=5)
        self.ent_usuario.insert(0, "professor@faculdade.edu") # Exemplo padrão
        
        # Campo Senha
        ttk.Label(self.frame_login, text="Senha:").pack(anchor=tk.W)
        self.ent_senha = ttk.Entry(self.frame_login, width=30, show="*")
        self.ent_senha.pack(pady=5)
        self.ent_senha.insert(0, "123456") # Exemplo padrão
        
        # Botão Entrar
        btn_entrar = ttk.Button(self.frame_login, text="Entrar no Sistema", command=self.autenticar)
        btn_entrar.pack(pady=15, fill=tk.X)

    def autenticar(self):
        usuario = self.ent_usuario.get().strip()
        senha = self.ent_senha.get().strip()
        
        # Simulação simples de login (Pode ser expandida na API depois)
        if usuario == "professor@faculdade.edu" and senha == "123456":
            self.usuario_logado = usuario
            
            # Destrói a tela de login
            self.frame_login.destroy()
            
            # Muda o tamanho da janela para o painel principal e redesenha a tela
            self.root.geometry("850x450")
            self.tela_principal()
        else:
            messagebox.showerror("Erro de Acesso", "Usuário ou senha incorretos!")

    # --- TELA 2: PAINEL PRINCIPAL (BOTÕES, CAIXAS E TABELA) ---
    def tela_principal(self):
        # Janela dividida em Esquerda (Formulário) e Direita (Tabela)
        
        # --- PAINEL DA ESQUERDA: FORMULÁRIO ---
        frame_esquerdo = ttk.LabelFrame(self.root, text=" Nova Reserva ", padding=15)
        frame_esquerdo.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        
        # Mostrar quem está logado
        ttk.Label(frame_esquerdo, text=f"Conectado como:", font=("Arial", 9, "italic")).pack(anchor=tk.W)
        ttk.Label(frame_esquerdo, text=self.usuario_logado, font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        # Caixas de Seleção (Combobox) - Buscando as opções da API
        ttk.Label(frame_esquerdo, text="Selecione a Sala:").pack(anchor=tk.W, pady=2)
        self.cb_sala = ttk.Combobox(frame_esquerdo, state="readonly", width=25)
        self.cb_sala.pack(pady=5)
        
        ttk.Label(frame_esquerdo, text="Selecione o Horário:").pack(anchor=tk.W, pady=2)
        self.cb_horario = ttk.Combobox(frame_esquerdo, state="readonly", width=25)
        self.cb_horario.pack(pady=5)
        
        # Carrega os dados nas caixas de seleção vindo das configurações da API
        self.carregar_opcoes_combobox()
        
        # Botões de Ação
        btn_reservar = ttk.Button(frame_esquerdo, text="Confirmar Reserva", command=self.enviar_reserva_api)
        btn_reservar.pack(fill=tk.X, pady=(20, 5))
        
        btn_atualizar = ttk.Button(frame_esquerdo, text="Atualizar Tabela", command=self.puxar_reservas_api)
        btn_atualizar.pack(fill=tk.X, pady=5)

        btn_cancelar = ttk.Button(frame_esquerdo, text="Cancelar Reserva Selecionada", command=self.deletar_reserva_api)
        btn_cancelar.pack(fill=tk.X, pady=5)

        # --- PAINEL DA DIREITA: TABELA VISUAL ---
        frame_direito = ttk.LabelFrame(self.root, text=" Quadro de Ocupação das Salas ", padding=10)
        frame_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configuração da Tabela Organizada (Treeview)
        colunas = ("id", "sala", "horario", "responsavel")
        self.tabela = ttk.Treeview(frame_direito, columns=colunas, show="headings")
        
        # Cabeçalhos
        self.tabela.heading("id", text="ID")
        self.tabela.heading("sala", text="Sala / Ambiente")
        self.tabela.heading("horario", text="Horário Reservado")
        self.tabela.heading("responsavel", text="Professor Responsável")
        
        # Largura das Colunas
        self.tabela.column("id", width=40, anchor=tk.CENTER)
        self.tabela.column("sala", width=200)
        self.tabela.column("horario", width=130, anchor=tk.CENTER)
        self.tabela.column("responsavel", width=180)
        
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Carrega os dados na tabela pela primeira vez automaticamente
        self.puxar_reservas_api()

    # --- INTEGRAÇÃO DIRETA COM AS ROTAS DA API ---
    def carregar_opcoes_combobox(self):
        """Define as opções das caixas de seleção."""
        # Definidos de forma estática alinhados com as regras da API
        salas = ["Sala 101 (Laboratório)", "Sala 102 (Teórica)", "Auditório A", "Bloco B - Sala 05"]
        horarios = ["08:00 - 10:00", "10:00 - 12:00", "14:00 - 16:00", "16:00 - 18:00"]
        
        self.cb_sala['values'] = salas
        self.cb_sala.current(0)
        
        self.cb_horario['values'] = horarios
        self.cb_horario.current(0)

    def puxar_reservas_api(self):
        """Faz um GET na API e atualiza as linhas da tabela."""
        try:
            resposta = requests.get(f"{API_URL}/reservas")
            if resposta.status_code == 200:
                # Limpa as linhas antigas da tabela
                for item in self.tabela.get_children():
                    self.tabela.delete(item)
                
                # Insere os dados novos vindos do banco SQLite da API
                for res in resposta.json():
                    self.tabela.insert("", tk.END, values=(res["id"], res["sala"], res["horario"], res["responsavel"]))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Erro de Conexão", "A API está desligada! Ligue o arquivo api.py primeiro.")

    def enviar_reserva_api(self):
        """Faz um POST enviando os dados selecionados para a API."""
        dados_formulario = {
            "sala": self.cb_sala.get(),
            "horario": self.cb_horario.get(),
            "responsavel": self.usuario_logado
        }
        
        try:
            resposta = requests.post(f"{API_URL}/reservas", json=dados_formulario)
            
            if resposta.status_code == 200:
                messagebox.showinfo("Sucesso", "Reserva gravada no banco com sucesso!")
                self.puxar_reservas_api() # Recarrega a tabela visual automaticamente
            elif resposta.status_code == 409:
                # Captura o erro de choque de horário enviado pela API
                erro_msg = resposta.json().get("detail", "Conflito de horário.")
                messagebox.showerror("Sala Ocupada", erro_msg)
            else:
                messagebox.showwarning("Aviso", "Erro ao processar requisição.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Erro", "Erro de comunicação com a API.")

    def deletar_reserva_api(self):
        """Pega o ID da linha clicada na tabela e manda um DELETE para a API."""
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma linha da tabela para cancelar!")
            return
            
        valores_da_linha = self.tabela.item(item_selecionado, "values")
        reserva_id = valores_da_linha[0] # Pega o ID da primeira coluna
        
        try:
            resposta = requests.delete(f"{API_URL}/reservas/{reserva_id}")
            if resposta.status_code == 200:
                messagebox.showinfo("Cancelada", f"Reserva {reserva_id} excluída do banco!")
                self.puxar_reservas_api()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Erro", "Erro de comunicação com a API.")

if __name__ == "__main__":
    janela_raiz = tk.Tk()
    app = AplicativoFaculdade(janela_raiz)
    janela_raiz.mainloop()
