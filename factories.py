from abc import ABC, abstractmethod

# ============== ABSTRACT FACTORY ==============

class ReservaFactory(ABC):
    """Interface abstrata para factories de reservas"""
    
    @abstractmethod
    def criar(self, hospede, propriedade, data_inicio, data_fim):
        """Cria uma reserva completa com seus serviços"""
        pass


# ============== CONCRETE FACTORIES ==============

class ReservaBasicaFactory(ReservaFactory):
    """Factory que cria reservas básicas (sem serviços adicionais)"""
    
    def criar(self, hospede, propriedade, data_inicio, data_fim):
        from sistema import Reserva
        
        reserva = Reserva(hospede, propriedade, data_inicio, data_fim)
        reserva.tipo = "basica"
        reserva.servicos = []
        
        # Preço = apenas o quarto
        reserva.preco_final = propriedade.preco
        
        return reserva


class ReservaPremiumFactory(ReservaFactory):
    """Factory que cria reservas premium com 3 serviços inclusos"""
    
    def criar(self, hospede, propriedade, data_inicio, data_fim):
        from sistema import Reserva
        
        reserva = Reserva(hospede, propriedade, data_inicio, data_fim)
        reserva.tipo = "premium"
        
        # Define os serviços inclusos no pacote premium
        reserva.servicos = [
            {"nome": "Café da manhã", "custo": 50},
            {"nome": "Limpeza diária", "custo": 40},
            {"nome": "WiFi premium", "custo": 20}
        ]
        
        # Calcula preço total: quarto + serviços
        total_servicos = sum(s["custo"] for s in reserva.servicos)
        reserva.preco_final = propriedade.preco + total_servicos
        
        return reserva


class ReservaVIPFactory(ReservaFactory):
    """Factory que cria reservas VIP com serviços premium e benefício especial"""
    
    def criar(self, hospede, propriedade, data_inicio, data_fim):
        from sistema import Reserva
        
        reserva = Reserva(hospede, propriedade, data_inicio, data_fim)
        reserva.tipo = "vip"
        
        # Define os serviços inclusos no pacote VIP (mais completo que premium)
        reserva.servicos = [
            {"nome": "Café da manhã", "custo": 50},
            {"nome": "Limpeza diária", "custo": 40},
            {"nome": "WiFi premium", "custo": 20},
            {"nome": "Concierge 24h", "custo": 100}
        ]
        
        # Benefício especial VIP: check-in antecipado
        reserva.beneficio_especial = "check_in_antecipado"
        
        # Calcula preço total: quarto + serviços
        total_servicos = sum(s["custo"] for s in reserva.servicos)
        reserva.preco_final = propriedade.preco + total_servicos
        
        return reserva
