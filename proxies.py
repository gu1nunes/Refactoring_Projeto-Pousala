from datetime import datetime

# ============== PADRÃO PROXY - CONTROLE DE ACESSO ==============

class ProxyPropriedade:
    """Proxy que controla acesso aos dados de propriedades"""
    
    def __init__(self, propriedade):
        self.propriedade = propriedade
        self.erro = None
    
    def pode_visualizar(self, usuario_email):
        """Valida se usuário pode visualizar os detalhes da propriedade"""
        if not usuario_email:
            self.erro = "Erro: Usuário não autenticado. Faça login para ver detalhes."
            return False
        
        if not self.propriedade:
            self.erro = "Erro: Propriedade não encontrada."
            return False
        
        # Propriedade pode ser visualizada por qualquer um
        return True
    
    def pode_editar(self, usuario_email):
        """Valida se usuário pode editar a propriedade (só anfitrião)"""
        if not usuario_email:
            self.erro = "Erro: Usuário não autenticado. Faça login."
            return False
        
        # Só o anfitrião pode editar
        if self.propriedade.anfitriao.email.strip().lower() != usuario_email.strip().lower():
            self.erro = "Erro: Apenas o anfitrião pode editar esta propriedade."
            return False
        
        return True
    
    def pode_reservar(self, data_inicio, data_fim):
        """Valida se propriedade pode ser reservada nessas datas"""
        if not data_inicio or not data_fim:
            self.erro = "Erro: Datas inválidas."
            return False
        
        if not self.propriedade.esta_disponivel(data_inicio, data_fim):
            self.erro = "Erro: Propriedade não está disponível para essas datas."
            return False
        
        # Validar datas no passado
        hoje = datetime.now().strftime('%Y-%m-%d')
        if data_inicio < hoje:
            self.erro = "Erro: Não pode reservar para datas passadas."
            return False
        
        return True
    
    def obter_erro(self):
        """Retorna a mensagem de erro"""
        return self.erro


class ProxyChat:
    """Proxy que controla acesso ao chat entre hóspede e anfitrião"""
    
    def __init__(self, propriedade, hospede_email, anfitriao_email, sistema):
        self.propriedade = propriedade
        self.hospede_email = hospede_email.strip().lower() if hospede_email else None
        self.anfitriao_email = anfitriao_email.strip().lower() if anfitriao_email else None
        self.sistema = sistema
        self.erro = None
    
    def pode_iniciar_chat(self):
        """Valida se hóspede pode iniciar chat com anfitrião"""
        if not self.hospede_email:
            self.erro = "Erro: Hóspede não autenticado."
            return False
        
        if not self.propriedade:
            self.erro = "Erro: Propriedade não encontrada."
            return False
        
        # Verifica se hóspede fez reserva nessa propriedade
        tem_reserva = any(
            reserva.hospede.email.strip().lower() == self.hospede_email 
            for reserva in self.propriedade.reservas
        )
        
        if not tem_reserva:
            self.erro = "Erro: Você precisa ter feito uma reserva nesta propriedade para chatear."
            return False
        
        return True
    
    def pode_enviar_mensagem(self, remetente_email, texto):
        """Valida se mensagem pode ser enviada"""
        if not remetente_email or not texto:
            self.erro = "Erro: Remetente ou texto da mensagem inválido."
            return False
        
        if not texto.strip():
            self.erro = "Erro: Mensagem não pode estar vazia."
            return False
        
        # Valida limite de 500 caracteres
        if len(texto) > 500:
            self.erro = "Erro: Mensagem muito longa (máximo 500 caracteres)."
            return False
        
        # Verifica se remetente é hóspede ou anfitrião do chat
        remetente_normalizado = remetente_email.strip().lower()
        if remetente_normalizado not in [self.hospede_email, self.anfitriao_email]:
            self.erro = "Erro: Você não faz parte desta conversa."
            return False
        
        return True
    
    def obter_erro(self):
        """Retorna a mensagem de erro"""
        return self.erro


class ProxyAvaliacao:
    """Proxy que controla quem pode avaliar uma propriedade"""
    
    def __init__(self, propriedade, hospede_email):
        self.propriedade = propriedade
        self.hospede_email = hospede_email.strip().lower() if hospede_email else None
        self.erro = None
    
    def pode_avaliar(self, nota, comentario):
        """Valida se hóspede pode avaliar a propriedade"""
        if not self.hospede_email:
            self.erro = "Erro: Hóspede não autenticado."
            return False
        
        # Valida nota
        try:
            nota_int = int(nota)
            if nota_int < 1 or nota_int > 5:
                self.erro = "Erro: Nota deve ser entre 1 e 5 estrelas."
                return False
        except (ValueError, TypeError):
            self.erro = "Erro: Nota inválida."
            return False
        
        # Verifica se hóspede fez reserva
        fez_reserva = any(
            reserva.hospede.email.strip().lower() == self.hospede_email 
            for reserva in self.propriedade.reservas
        )
        
        if not fez_reserva:
            self.erro = "Erro: Você só pode avaliar propriedades onde já fez uma reserva."
            return False
        
        # Impede avaliação duplicada (mesmo hóspede, mesma propriedade)
        ja_avaliou = any(
            av['hospede'].strip().lower() == self.hospede_email 
            for av in self.propriedade.avaliacoes
        )
        
        if ja_avaliou:
            self.erro = "Erro: Você já avaliou esta propriedade."
            return False
        
        if not comentario or not comentario.strip():
            self.erro = "Erro: Comentário não pode estar vazio."
            return False
        
        return True
    
    def obter_erro(self):
        """Retorna a mensagem de erro"""
        return self.erro


class ProxyReserva:
    """Proxy que valida antes de criar uma reserva"""
    
    def __init__(self, propriedade, hospede, data_inicio, data_fim, tipo_reserva="basica"):
        self.propriedade = propriedade
        self.hospede = hospede
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.tipo_reserva = tipo_reserva
        self.erro = None
    
    def pode_reservar(self):
        """Valida todas as regras antes de permitir reserva"""
        # Valida datas
        if not self.data_inicio or not self.data_fim:
            self.erro = "Erro: Datas inválidas."
            return False
        
        # Valida se datas não estão no passado
        hoje = datetime.now().strftime('%Y-%m-%d')
        if self.data_inicio < hoje:
            self.erro = "Erro: Data de check-in não pode ser no passado."
            return False
        
        # Valida se data_fim é depois de data_inicio
        if self.data_fim <= self.data_inicio:
            self.erro = "Erro: A data de saída deve ser depois da data de entrada."
            return False
        
        # Valida disponibilidade
        if not self.propriedade.esta_disponivel(self.data_inicio, self.data_fim):
            self.erro = "Erro: Propriedade não está disponível para essas datas."
            return False
        
        # Valida tipo de reserva
        tipos_validos = ["basica", "premium", "vip"]
        if self.tipo_reserva not in tipos_validos:
            self.erro = f"Erro: Tipo de reserva inválido. Use: {', '.join(tipos_validos)}"
            return False
        
        # Valida capacidade
        if not self.propriedade.capacidade > 0:
            self.erro = "Erro: Propriedade não tem capacidade válida."
            return False
        
        # Valida hóspede
        if not self.hospede or not self.hospede.email:
            self.erro = "Erro: Hóspede não autenticado ou inválido."
            return False
        
        return True
    
    def obter_erro(self):
        """Retorna a mensagem de erro"""
        return self.erro
    
    def obter_preco_estimado(self):
        """Calcula preço estimado baseado no tipo de reserva"""
        from datetime import datetime as dt
        
        data_in = dt.strptime(self.data_inicio, '%Y-%m-%d')
        data_out = dt.strptime(self.data_fim, '%Y-%m-%d')
        noites = (data_out - data_in).days
        
        preco_base = self.propriedade.preco * noites
        
        # Adiciona custos de serviços conforme tipo
        if self.tipo_reserva == "premium":
            servicos = 110  # Café (50) + Limpeza (40) + WiFi (20)
            return preco_base + servicos
        elif self.tipo_reserva == "vip":
            servicos = 210  # Café (50) + Limpeza (40) + WiFi (20) + Concierge (100)
            return preco_base + servicos
        
        return preco_base
