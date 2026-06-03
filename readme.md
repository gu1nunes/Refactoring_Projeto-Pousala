# Pousa.Lá

Projeto desenvolvido por **Ana Letícia Nobre da Silva**, inspirado em plataformas como o Booking.com.

 **Acesse o sistema online:**
👉 https://pousala.pythonanywhere.com/

---

## Sobre o Projeto

O **Pousa.Lá** é um sistema de reservas de hospedagem que permite que usuários encontrem, avaliem e reservem propriedades de forma simples e intuitiva.

A aplicação foi desenvolvida com foco em conceitos de **Programação Orientada a Objetos (POO)**, organização de dados e simulação de um sistema real de reservas, semelhante a plataformas conhecidas do mercado.

---

## Objetivo

O objetivo do projeto é simular um ambiente de hospedagem online onde:

* Hóspedes podem buscar e reservar locais
* Anfitriões podem anunciar propriedades
* Usuários podem interagir, avaliar e favoritar imóveis

---

## Funcionalidades

###  1. Login / Cadastro

* Permite criação de contas e autenticação de usuários
* Vincula ações (reservas, favoritos) ao usuário

---

###  2. Busca de Propriedades

* Filtragem por:
  * Localização
  * Quantidade de pessoas
  * Datas
* Mostra apenas propriedades disponíveis

---

### 3. Favoritos

* Permite salvar propriedades de interesse
* Facilita acesso rápido sem nova busca

---

###  4. Chat de Contato Direto

* Comunicação entre hóspede e anfitrião
* Permite tirar dúvidas sobre a propriedade

---

### 5. Sistema de Reservas

* Reserva propriedades por período
* Após confirmação:
  * o local fica indisponível para outros usuários

---

### 6. Avaliação com Estrelas

* Usuários avaliam propriedades
* Média das notas fica visível

---

### 7. Avaliação com Comentários

* Feedback textual sobre a experiência
* Ajuda outros usuários na decisão

---

###  8. Seção de Dúvidas

* Lista de perguntas frequentes
* Evita contato desnecessário com o anfitrião

---

###  9. Anunciar Propriedade

* Anfitriões podem cadastrar novos imóveis
* Propriedades ficam disponíveis para busca

---

### 10. Minhas Reservas

* Exibe reservas do usuário
* Organização por status:
  * Ativa
  * Concluída

---

##  Conceitos Aplicados

O projeto utiliza fortemente conceitos de **POO**:

* **Herança** → Usuário, Hóspede e Anfitrião
* **Encapsulamento** → Atributos privados e uso de `@property`
* **Polimorfismo** → Métodos como `mostrar_painel()`

---

##  Tecnologias Utilizadas

* Python 
* Programação Orientada a Objetos (POO)
* Banco de Dados 
* PythonAnywhere (deploy)

---

## 📂 Estrutura do Projeto

* `app.py` ➔ Controlador web (Rotas do Flask e integração com o frontend).
* `sistema.py` ➔ Fachada (Facade) e domínio da aplicação contendo as regras de negócio (POO).
* `banco.py` ➔ DAO (Data Access Object) responsável pelas operações de CRUD no banco SQLite.
* `pousala.db` ➔ Banco de dados local.
* `/templates/` ➔ Diretório contendo todas as interfaces (Views) em HTML.

---
##  Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/analeticiiaa/pousala.git
```

2. Acesse a pasta:

```bash
cd pousala
```

3. Execute o projeto (dependendo da estrutura):

```bash
python app.py
```

---

## Deploy

O sistema está disponível online em:

 https://pousala.pythonanywhere.com/

---

## 👩‍💻 Autora

**Ana Letícia Nobre da Silva**

--- ## -------- ## ----------

## 🔧 Refatoramento - Abstract Factory

### 📋 Análise Inicial - Por que Reservas?

Após análise profunda do código, concluiu-se que o padrão **Abstract Factory** não se encaixava na criação de propriedades/quartos (que é um simples construtor), mas sim na **criação de Reservas com diferentes pacotes de serviços**, onde cada tipo de reserva traz consigo uma "família" de serviços relacionados.

### 🎯 Aplicação: Reservas com 3 Tipos de Pacotes

O padrão foi aplicado para centralizar a criação de reservas com diferentes níveis de serviços:

```
ReservaFactory (interface abstrata)
    ├── ReservaBasicaFactory
    │   └── Cria: Reserva sem serviços adicionais
    │       Preço: R$100 (só quarto)
    │       Serviços: Nenhum
    │
    ├── ReservaPremiumFactory
    │   └── Cria: Reserva com 3 serviços inclusos
    │       Preço: R$100 + R$110 = R$210
    │       Serviços: Café da manhã, Limpeza diária, WiFi premium
    │
    └── ReservaVIPFactory
        └── Cria: Reserva com 4 serviços + benefício
            Preço: R$100 + R$210 = R$310
            Serviços: Café, Limpeza, WiFi, Concierge 24h
            Benefício: Check-in antecipado (4h antes)
```

### ✨ Benefícios Alcançados

✅ **Encapsulamento:** Cada factory encapsula a lógica de criação de sua família de serviços  
✅ **Escalabilidade:** Adicionar novo tipo de reserva requer apenas uma nova factory  
✅ **Manutenibilidade:** Lógica de criação isolada por tipo, sem `if/else` espalhados  
✅ **Consistência:** Impossível misturar serviços incompatíveis com tipos de reserva  
✅ **Rastreamento:** Banco de dados guarda histórico completo (tipo, preço, serviços, benefícios)

### 📂 Estrutura de Implementação

**Novos arquivos:**
- `factories.py` - Define ReservaFactory e suas implementações concretas

**Tabelas do banco (modificadas/novas):**
```sql
-- Modificada: adicionados tipo_reserva e preco_final
CREATE TABLE reservas (
    id INTEGER PRIMARY KEY,
    propriedade_nome TEXT NOT NULL,
    hospede_email TEXT NOT NULL,
    data_inicio TEXT NOT NULL,
    data_fim TEXT NOT NULL,
    status TEXT NOT NULL,
    tipo_reserva TEXT DEFAULT 'basica',    -- NOVO
    preco_final REAL DEFAULT 0             -- NOVO
);

-- NOVA: Rastreia serviços inclusos em cada reserva
CREATE TABLE servicos_reserva (
    id INTEGER PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    nome_servico TEXT NOT NULL,
    custo REAL NOT NULL,
    incluido BOOLEAN DEFAULT TRUE
);

-- NOVA: Rastreia benefícios VIP de cada reserva
CREATE TABLE beneficios_vip (
    id INTEGER PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    beneficio TEXT NOT NULL
);
```

**Arquivos modificados:**
- `banco.py` - Novos métodos para gerenciar serviços e benefícios
- `sistema.py` - Importa factories e integra na criação de reservas
- `app.py` - Rota `/reservar` agora aceita parâmetro `tipo_reserva`

### 🔄 Fluxo de Execução

```
1. Hóspede seleciona tipo de reserva (básica/premium/vip) no formulário
2. app.py captura o tipo_reserva e chama sistema.registrar_reserva()
3. Sistema chama hospede.fazer_reserva(tipo_reserva)
4. Factory correspondente é instanciada e cria() a reserva completa
5. Factory calcula preço final = quarto + serviços
6. Dados salvos em 3 tabelas: reservas, servicos_reserva, beneficios_vip
7. Confirmação mostra tipo e preço total ao hóspede
```

### 💡 Exemplo Prático

**Entrada:** Hóspede reserva "Apartamento Luxo" como PREMIUM de 01/06 a 03/06

**Processamento:**
1. ReservaPremiumFactory.criar() é acionada
2. Cria Reserva com:
   - tipo = "premium"
   - servicos = [Café (R$50), Limpeza (R$40), WiFi (R$20)]
   - preco_final = R$200 (quarto) + R$110 (serviços) = R$310

**Saída:** "✅ Reserva PREMIUM confirmada! Preço total: R$310.00"

### 🚀 Conclusão

O **Abstract Factory aplicado a Reservas** permite que o sistema evolua naturalmente:
- Adicionar novo tipo de reserva é trivial (criar nova factory)
- Modificar serviços de um tipo não afeta outros tipos
- Histórico completo de cada reserva fica registrado no banco
- Código limpo, sem condicionais, seguindo Single Responsibility Principle

---

## 🛡️ Padrão Estrutural - Proxy

### Descrição

O padrão Proxy será utilizado para controlar o acesso a operações críticas no sistema, validando permissões e estado antes de executar ações. Cada proxy funcionará como um "intermediário" entre o usuário e a ação desejada.

### Estrutura de Implementação

**ProxyPropriedade:**
- Valida se propriedade está ativa antes de mostrar detalhes
- Bloqueia reserva se não há disponibilidade
- Verifica permissões do usuário (só anfitrião pode editar)
- Registra tentativas de acesso não autorizado

**ProxyChat:**
- Só permite chat se há reserva ativa na propriedade
- Bloqueia mensagens se usuário foi bloqueado
- Valida se ambos os participantes existem
- Impede mensagens para propriedades deletadas

**ProxyAvaliacao:**
- Só permite avaliar se hospedagem foi concluída
- Impede avaliação duplicada (um hóspede por propriedade)
- Bloqueia se período de avaliação expirou
- Valida nota entre 1-5 estrelas

**ProxyReserva:**
- Verifica disponibilidade de datas
- Valida capacidade vs número de hóspedes
- Bloqueia se hóspede tem reserva ativa no mesmo período
- Verifica se propriedade está ativa

### Benefícios

✅ Segurança: Valida permissões antes de executar  
✅ Integridade: Impede estados inválidos no banco  
✅ Experiência: Usuário recebe mensagens de erro claras  
✅ Auditoria: Registra tentativas de acesso  
✅ Manutenibilidade: Lógica de validação centralizada

---

## 🔗 Padrão Comportamental - Mediator

### Descrição

O padrão Mediator centraliza a comunicação entre hóspedes e anfitriões. Ao invés de deixar essas duas entidades se comunicarem diretamente, um intermediário (ChatMediator) gerencia todas as interações, validações e notificações.

**Sem Mediator (Problema):**
```
Hospede <--diretamente--> Anfitriao (Acoplamento)
```

**Com Mediator (Solução):**
```
Hospede <--> ChatMediator <--> Anfitriao (Desacoplado)
```

### Implementação

#### Arquivo: `mediator.py`

A classe `ChatMediator` implementa:

**1. Validações de Comunicação**
```python
pode_conversar(hospede_email, anfitriao_email, propriedade_nome) -> (bool, str)
```
- Valida se não é comunicação com a mesma pessoa
- Verifica se existe reserva ativa entre hóspede e anfitrião
- Retorna (autorizado, mensagem_erro)

**2. Envio de Mensagens**
```python
enviar_mensagem(propriedade_nome, remetente_email, destinatario_email, texto, banco_dados) -> (bool, str)
```
- Valida se pode conversar
- Valida conteúdo da mensagem (não vazia, máx 500 caracteres)
- Armazena no histórico em memória
- Persiste no banco de dados
- Notifica destinatário

**3. Gerenciamento de Histórico**
```python
obter_historico(hospede_email, anfitriao_email) -> List[Dict]
marcar_como_lida(hospede_email, anfitriao_email, indice_msg) -> bool
```
- Retorna conversa entre dois usuários ordenada por timestamp
- Marca mensagens como lidas

**4. Notificações**
```python
obter_notificacoes_pendentes(usuario_email) -> List[Dict]
limpar_notificacoes(usuario_email) -> None
```
- Sistema de notificações em tempo real
- Registra eventos (nova mensagem, etc)

**5. Gerenciamento de Usuários**
```python
registrar_usuario_ativo(usuario_email, tipo) -> None
usuario_esta_ativo(usuario_email) -> bool
```
- Rastreia quem está online
- Permite coordenar comunicação de usuários ativos

### Fluxo de Envio de Mensagem

```
1. Hóspede submete mensagem no formulário (/chat)
   ↓
2. app.py captura e valida com ProxyChat
   ↓
3. app.py chama meu_pousala.pode_conversar() via Mediator
   ↓
4. ChatMediator.pode_conversar() valida:
   - Não é comunicação com si mesmo
   - Existe reserva ativa
   ↓
5. Se validou, app.py chama meu_pousala.enviar_mensagem()
   ↓
6. Sistema.enviar_mensagem() delega ao ChatMediator
   ↓
7. ChatMediator.enviar_mensagem() executa:
   - Valida mensagem (não vazia, 500 char max)
   - Armazena em histórico em memória
   - Persiste no banco via BancoDeDados
   - Notifica o destinatário
   ↓
8. Retorna sucesso ✅
```

### Integração com Código Existente

**Em `sistema.py`:**
```python
class Sistema:
    def __init__(self):
        self.chat_mediator = ChatMediator(self.db)  # Inicializa
    
    def pode_conversar(self, hospede_email, anfitriao_email, propriedade_nome):
        """Delega ao Mediator a validação de conversa"""
        return self.chat_mediator.pode_conversar(...)
    
    def enviar_mensagem(self, prop, rem, dest, texto):
        """Mediator coordena o envio de mensagem"""
        sucesso, msg = self.chat_mediator.enviar_mensagem(...)
        if not sucesso: raise Exception(msg)
```

**Em `app.py` rota `/chat`:**
```python
# Proxy valida acesso
if proxy_chat.pode_enviar_mensagem(log, texto):
    # Mediator coordena envio
    pode_conversar, erro = meu_pousala.pode_conversar(h_e, a_e, p_nome)
    if pode_conversar:
        meu_pousala.enviar_mensagem(...)
```

### Regras de Negócio Centralizadas

**Quem pode conversar?**
- ✅ Hóspede e Anfitrião com reserva ativa
- ❌ Usuários sem reserva relacionada
- ❌ Comunicação com a mesma pessoa
- ❌ Propriedades não encontradas

**Validações de Mensagem**
- ❌ Mensagem vazia
- ❌ Mais de 500 caracteres
- ❌ Caracteres inválidos (\x00, quebras duplas)

### Benefícios

✅ **Desacoplamento** - Hóspede e Anfitrião não dependem um do outro  
✅ **Centralização** - Toda lógica de chat em um só lugar  
✅ **Extensibilidade** - Fácil adicionar email, push notifications, etc  
✅ **Auditoria** - Histórico completo em um só ponto  
✅ **Reusabilidade** - Múltiplas conversas usam a mesma lógica  
✅ **Manutenibilidade** - Mudanças só afetam o Mediator

### Estatísticas e Monitoramento

```python
obter_total_mensagens(hospede_email, anfitriao_email) -> int
obter_usuarios_ativos_count() -> int
obter_conversas_ativas() -> List[str]
```

Facilita análise de padrões de comunicação e uso do sistema.