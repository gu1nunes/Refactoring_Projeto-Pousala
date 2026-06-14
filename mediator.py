"""
PADRÃO MEDIATOR - Coordenação de Comunicação entre Hóspedes e Anfitriões

Problema sem Mediator:
  Hospede <--> Anfitriao (comunicação direta, acoplamento)
  
Solução com Mediator:
  Hospede <--> ChatMediator <--> Anfitriao (comunicação centralizada)

Benefícios:
  1. Desacoplamento entre participantes
  2. Lógica centralizada de comunicação
  3. Fácil adicionar novas regras
  4. Melhor controle e auditoria
"""

from datetime import datetime
from typing import List, Dict, Tuple


class ChatMediator:
    """
    Mediator que coordena toda a comunicação entre Hóspedes e Anfitriões.
    
    Responsabilidades:
    - Validar se dois usuários podem conversar
    - Coordenar envio de mensagens
    - Manter histórico de conversas
    - Notificar participantes
    """
    
    def __init__(self, banco_dados):
        """
        Args:
            banco_dados: Referência ao BancoDeDados para persistência
        """
        self.banco = banco_dados
        self.historico_conversas: Dict[str, List[Dict]] = {}
        self.usuarios_ativos: Dict[str, str] = {}  # email -> tipo (hospede/anfitriao)
        self.notificacoes_pendentes: Dict[str, List[str]] = {}  # email -> lista de notificações
    
    # ============================================================
    # MÉTODOS DE VALIDAÇÃO
    # ============================================================
    
    def pode_conversar(self, hospede_email: str, anfitriao_email: str, propriedade_nome: str) -> Tuple[bool, str]:
        """
        Verifica se hóspede e anfitrião podem conversar sobre uma propriedade.
        
        Regras de validação:
        1. Ambos devem ter contas ativas
        2. Deve haver uma reserva ativa entre eles
        3. Não pode ser comunicação com a mesma pessoa
        
        Returns:
            (pode_conversar: bool, motivo_erro: str)
        """
        # Regra 1: Validar que não é comunicação consigo mesmo
        if hospede_email.strip().lower() == anfitriao_email.strip().lower():
            return False, "Erro: Não é possível conversar consigo mesmo."
        
        # Regra 2: Validar que existe reserva ativa entre hóspede e anfitrião nesta propriedade
        reservas = self.banco.buscar_reservas()
        tem_reserva = False
        
        for reserva in reservas:
            # reserva[1] = propriedade_nome, reserva[2] = hospede_email
            if (str(reserva[1]).strip().lower() == propriedade_nome.strip().lower() and
                str(reserva[2]).strip().lower() == hospede_email.strip().lower()):
                tem_reserva = True
                break
        
        if not tem_reserva:
            return False, "Erro: Você só pode conversar se tiver uma reserva ativa."
        
        return True, ""
    
    def pode_enviar_mensagem(self, remetente_email: str, destinatario_email: str, texto: str) -> Tuple[bool, str]:
        """
        Valida se uma mensagem pode ser enviada.
        
        Regras de validação:
        1. Texto não pode estar vazio
        2. Texto não pode exceder 500 caracteres
        3. Remetente deve estar autenticado
        
        Returns:
            (pode_enviar: bool, motivo_erro: str)
        """
        # Regra 1: Validar texto vazio
        if not texto or not texto.strip():
            return False, "Erro: Mensagem não pode estar vazia."
        
        # Regra 2: Validar comprimento da mensagem
        if len(texto) > 500:
            return False, "Erro: Mensagem muito longa (máximo 500 caracteres)."
        
        # Regra 3: Validar caracteres inválidos
        if any(char in texto for char in ['\x00', '\r\n\r\n']):
            return False, "Erro: Mensagem contém caracteres inválidos."
        
        return True, ""
    
    # ============================================================
    # MÉTODOS DE COMUNICAÇÃO
    # ============================================================
    
    def enviar_mensagem(self, propriedade_nome: str, remetente_email: str, 
                       destinatario_email: str, texto: str, banco_dados) -> Tuple[bool, str]:
        """
        Coordena o envio de uma mensagem entre participantes.
        
        Fluxo:
        1. Valida se pode conversar
        2. Valida a mensagem
        3. Armazena no histórico
        4. Persiste no banco de dados
        5. Notifica o destinatário
        
        Args:
            propriedade_nome: Nome da propriedade
            remetente_email: Email de quem envia
            destinatario_email: Email de quem recebe
            texto: Conteúdo da mensagem
            banco_dados: Referência ao BancoDeDados
        
        Returns:
            (sucesso: bool, mensagem: str)
        """
        # PASSO 1: Validar se pode conversar
        pode_conversar, erro_conversa = self.pode_conversar(
            remetente_email, destinatario_email, propriedade_nome
        )
        if not pode_conversar:
            return False, erro_conversa
        
        # PASSO 2: Validar mensagem
        pode_enviar, erro_msg = self.pode_enviar_mensagem(
            remetente_email, destinatario_email, texto
        )
        if not pode_enviar:
            return False, erro_msg
        
        # PASSO 3: Criar objeto de mensagem
        mensagem = {
            'remetente': remetente_email.strip().lower(),
            'destinatario': destinatario_email.strip().lower(),
            'texto': texto.strip(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lida': False
        }
        
        # PASSO 4: Armazenar no histórico local
        chave_conversa = self._gerar_chave_conversa(remetente_email, destinatario_email)
        if chave_conversa not in self.historico_conversas:
            self.historico_conversas[chave_conversa] = []
        self.historico_conversas[chave_conversa].append(mensagem)
        
        # PASSO 5: Persistir no banco de dados (através do Sistema)
        banco_dados.salvar_mensagem(propriedade_nome, remetente_email, destinatario_email, texto)
        
        # PASSO 6: Notificar participante
        self._notificar_novo_evento(
            destinatario_email,
            f"Nova mensagem de {remetente_email}: {texto[:50]}..."
        )
        
        return True, "✅ Mensagem enviada com sucesso!"
    
    def obter_historico(self, hospede_email: str, anfitriao_email: str) -> List[Dict]:
        """
        Retorna o histórico de conversa entre dois participantes.
        
        Args:
            hospede_email: Email do hóspede
            anfitriao_email: Email do anfitrião
        
        Returns:
            Lista de mensagens ordenadas por timestamp
        """
        chave = self._gerar_chave_conversa(hospede_email, anfitriao_email)
        
        if chave not in self.historico_conversas:
            return []
        
        return sorted(
            self.historico_conversas[chave],
            key=lambda m: m['timestamp']
        )
    
    def marcar_como_lida(self, hospede_email: str, anfitriao_email: str, indice_msg: int) -> bool:
        """
        Marca uma mensagem como lida.
        
        Args:
            hospede_email: Email do hóspede
            anfitriao_email: Email do anfitrião
            indice_msg: Índice da mensagem no histórico
        
        Returns:
            True se conseguiu marcar, False caso contrário
        """
        chave = self._gerar_chave_conversa(hospede_email, anfitriao_email)
        
        if chave in self.historico_conversas and 0 <= indice_msg < len(self.historico_conversas[chave]):
            self.historico_conversas[chave][indice_msg]['lida'] = True
            return True
        
        return False
    
    # ============================================================
    # MÉTODOS DE NOTIFICAÇÃO
    # ============================================================
    
    def _notificar_novo_evento(self, usuario_email: str, evento: str) -> None:
        """
        Registra uma notificação para um usuário.
        
        Args:
            usuario_email: Email do usuário a notificar
            evento: Descrição do evento
        """
        email_normalizado = usuario_email.strip().lower()
        
        if email_normalizado not in self.notificacoes_pendentes:
            self.notificacoes_pendentes[email_normalizado] = []
        
        notificacao = {
            'evento': evento,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lida': False
        }
        
        self.notificacoes_pendentes[email_normalizado].append(notificacao)
    
    def obter_notificacoes_pendentes(self, usuario_email: str) -> List[Dict]:
        """
        Retorna todas as notificações pendentes de um usuário.
        
        Args:
            usuario_email: Email do usuário
        
        Returns:
            Lista de notificações não lidas
        """
        email_normalizado = usuario_email.strip().lower()
        
        if email_normalizado not in self.notificacoes_pendentes:
            return []
        
        return [n for n in self.notificacoes_pendentes[email_normalizado] if not n['lida']]
    
    def limpar_notificacoes(self, usuario_email: str) -> None:
        """
        Marca todas as notificações de um usuário como lidas.
        
        Args:
            usuario_email: Email do usuário
        """
        email_normalizado = usuario_email.strip().lower()
        
        if email_normalizado in self.notificacoes_pendentes:
            for notificacao in self.notificacoes_pendentes[email_normalizado]:
                notificacao['lida'] = True
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    
    def _gerar_chave_conversa(self, email1: str, email2: str) -> str:
        """
        Gera uma chave única para uma conversa entre dois emails.
        Garante que a ordem dos emails não importa.
        
        Args:
            email1: Primeiro email
            email2: Segundo email
        
        Returns:
            Chave única para a conversa
        """
        emails = sorted([email1.strip().lower(), email2.strip().lower()])
        return f"{emails[0]}___{emails[1]}"
    
    def registrar_usuario_ativo(self, usuario_email: str, tipo: str) -> None:
        """
        Registra um usuário como ativo no sistema.
        
        Args:
            usuario_email: Email do usuário
            tipo: Tipo de usuário ('hospede' ou 'anfitriao')
        """
        self.usuarios_ativos[usuario_email.strip().lower()] = tipo
    
    def usuario_esta_ativo(self, usuario_email: str) -> bool:
        """
        Verifica se um usuário está ativo.
        
        Args:
            usuario_email: Email do usuário
        
        Returns:
            True se ativo, False caso contrário
        """
        return usuario_email.strip().lower() in self.usuarios_ativos
    
    def desregistrar_usuario(self, usuario_email: str) -> None:
        """
        Desregistra um usuário do sistema.
        
        Args:
            usuario_email: Email do usuário
        """
        email_normalizado = usuario_email.strip().lower()
        if email_normalizado in self.usuarios_ativos:
            del self.usuarios_ativos[email_normalizado]
    
    # ============================================================
    # MÉTODOS DE ESTATÍSTICAS (PARA AUDITORIA)
    # ============================================================
    
    def obter_total_mensagens(self, hospede_email: str, anfitriao_email: str) -> int:
        """Retorna o total de mensagens entre dois usuários."""
        chave = self._gerar_chave_conversa(hospede_email, anfitriao_email)
        return len(self.historico_conversas.get(chave, []))
    
    def obter_usuarios_ativos_count(self) -> int:
        """Retorna a quantidade de usuários ativos."""
        return len(self.usuarios_ativos)
    
    def obter_conversas_ativas(self) -> List[str]:
        """Retorna lista de todas as conversas ativas."""
        return list(self.historico_conversas.keys())
