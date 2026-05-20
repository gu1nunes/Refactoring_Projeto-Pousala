import sqlite3

class BancoDeDados:
    def __init__(self, nome_arquivo="pousala.db"):
        self.conexao = sqlite3.connect(nome_arquivo, check_same_thread=False, timeout=10)
        self.cursor = self.conexao.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, tipo TEXT NOT NULL)''')
        # ATENÇÃO: Adicionado o campo "preco" aqui!
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS propriedades (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL, localizacao TEXT NOT NULL, capacidade INTEGER NOT NULL, preco REAL NOT NULL, anfitriao_email TEXT NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS reservas (id INTEGER PRIMARY KEY AUTOINCREMENT, propriedade_nome TEXT NOT NULL, hospede_email TEXT NOT NULL, data_inicio TEXT NOT NULL, data_fim TEXT NOT NULL, status TEXT NOT NULL, tipo_reserva TEXT DEFAULT 'basica', preco_final REAL DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS servicos_reserva (id INTEGER PRIMARY KEY AUTOINCREMENT, reserva_id INTEGER NOT NULL, nome_servico TEXT NOT NULL, custo REAL NOT NULL, incluido BOOLEAN DEFAULT TRUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS beneficios_vip (id INTEGER PRIMARY KEY AUTOINCREMENT, reserva_id INTEGER NOT NULL, beneficio TEXT NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS avaliacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, propriedade_nome TEXT NOT NULL, hospede_nome TEXT NOT NULL, nota INTEGER NOT NULL, comentario TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS favoritos (id INTEGER PRIMARY KEY AUTOINCREMENT, hospede_email TEXT NOT NULL, propriedade_nome TEXT NOT NULL, UNIQUE(hospede_email, propriedade_nome))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens (id INTEGER PRIMARY KEY AUTOINCREMENT, propriedade_nome TEXT NOT NULL, remetente TEXT NOT NULL, destinatario TEXT NOT NULL, texto TEXT NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS duvidas (id INTEGER PRIMARY KEY AUTOINCREMENT, propriedade_nome TEXT NOT NULL, pergunta TEXT NOT NULL, resposta TEXT NOT NULL)''')
        self.conexao.commit()

    def salvar_usuario(self, nome, email, senha, tipo):
        try:
            self.cursor.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', (nome, str(email).strip().lower(), senha, tipo))
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError: return False

    def buscar_todos_usuarios(self):
        self.cursor.execute('SELECT * FROM usuarios'); return self.cursor.fetchall()

    # Atualizado para receber o preço
    def salvar_propriedade(self, nome, localizacao, capacidade, preco, anfitriao_email):
        try:
            self.cursor.execute('INSERT INTO propriedades (nome, localizacao, capacidade, preco, anfitriao_email) VALUES (?, ?, ?, ?, ?)', (nome, localizacao, capacidade, preco, str(anfitriao_email).strip().lower()))
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError: return False

    def buscar_propriedades(self):
        self.cursor.execute('SELECT * FROM propriedades'); return self.cursor.fetchall()

    def salvar_reserva(self, propriedade_nome, hospede_email, data_inicio, data_fim, status, tipo_reserva="basica", preco_final=0):
        self.cursor.execute('INSERT INTO reservas (propriedade_nome, hospede_email, data_inicio, data_fim, status, tipo_reserva, preco_final) VALUES (?, ?, ?, ?, ?, ?, ?)', (propriedade_nome, str(hospede_email).strip().lower(), data_inicio, data_fim, status, tipo_reserva, preco_final))
        self.conexao.commit()
        return self.cursor.lastrowid  # Retorna o ID da reserva criada

    def buscar_reservas(self):
        self.cursor.execute('SELECT * FROM reservas'); return self.cursor.fetchall()

    def salvar_avaliacao(self, propriedade_nome, hospede_nome, nota, comentario):
        self.cursor.execute('INSERT INTO avaliacoes (propriedade_nome, hospede_nome, nota, comentario) VALUES (?, ?, ?, ?)', (propriedade_nome, hospede_nome, nota, comentario))
        self.conexao.commit()

    def buscar_avaliacoes(self):
        self.cursor.execute('SELECT * FROM avaliacoes'); return self.cursor.fetchall()

    def adicionar_favorito(self, hospede_email, propriedade_nome):
        try:
            self.cursor.execute('INSERT INTO favoritos (hospede_email, propriedade_nome) VALUES (?, ?)', (str(hospede_email).strip().lower(), propriedade_nome))
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError: return False

    def remover_favorito(self, hospede_email, propriedade_nome):
        self.cursor.execute('DELETE FROM favoritos WHERE hospede_email = ? AND propriedade_nome = ?', (str(hospede_email).strip().lower(), propriedade_nome))
        self.conexao.commit()

    def buscar_favoritos(self):
        self.cursor.execute('SELECT * FROM favoritos'); return self.cursor.fetchall()

    def salvar_mensagem(self, propriedade_nome, remetente, destinatario, texto):
        self.cursor.execute('INSERT INTO mensagens (propriedade_nome, remetente, destinatario, texto) VALUES (?, ?, ?, ?)', (propriedade_nome, str(remetente).strip().lower(), str(destinatario).strip().lower(), texto))
        self.conexao.commit()

    def buscar_mensagens(self):
        self.cursor.execute('SELECT * FROM mensagens'); return self.cursor.fetchall()

    def salvar_duvida(self, propriedade_nome, pergunta, resposta):
        self.cursor.execute('INSERT INTO duvidas (propriedade_nome, pergunta, resposta) VALUES (?, ?, ?)', (propriedade_nome, pergunta, resposta))
        self.conexao.commit()

    def buscar_duvidas(self, propriedade_nome):
        self.cursor.execute('SELECT * FROM duvidas WHERE propriedade_nome = ?', (propriedade_nome,))
        return self.cursor.fetchall()

    # ============== MÉTODOS PARA ABSTRACT FACTORY - RESERVAS ==============
    
    def salvar_servico_reserva(self, reserva_id, nome_servico, custo, incluido=True):
        """Salva um serviço associado a uma reserva"""
        self.cursor.execute('INSERT INTO servicos_reserva (reserva_id, nome_servico, custo, incluido) VALUES (?, ?, ?, ?)', 
                           (reserva_id, nome_servico, custo, incluido))
        self.conexao.commit()
    
    def buscar_servicos_reserva(self, reserva_id):
        """Busca todos os serviços de uma reserva"""
        self.cursor.execute('SELECT * FROM servicos_reserva WHERE reserva_id = ?', (reserva_id,))
        return self.cursor.fetchall()
    
    def salvar_beneficio_vip(self, reserva_id, beneficio):
        """Salva um benefício VIP associado a uma reserva"""
        self.cursor.execute('INSERT INTO beneficios_vip (reserva_id, beneficio) VALUES (?, ?)', 
                           (reserva_id, beneficio))
        self.conexao.commit()
    
    def buscar_beneficios_vip(self, reserva_id):
        """Busca todos os benefícios VIP de uma reserva"""
        self.cursor.execute('SELECT * FROM beneficios_vip WHERE reserva_id = ?', (reserva_id,))
        return self.cursor.fetchall()