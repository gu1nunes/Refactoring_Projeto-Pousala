

| Problema "encontrado"                       | Padrão utilizado    |
| ----------------------------------------- | -------------------- |
| Criação de diferentes tipos de reserva    | **Abstract Factory** |
| Validações espalhadas pelo sistema        | **Proxy**            |
| Comunicação muito acoplada entre usuários | **Mediator**         |

---

# 1. ABSTRACT FACTORY

## Evita lógica de criação espalhada e muitos if/else

##  Problema identificado

No sistema original, toda reserva era criada da mesma forma.

Porém, o projeto precisava oferecer diferentes categorias:

* Reserva Básica
* Reserva Premium
* Reserva VIP

Cada uma possui:

* preço diferente;
* serviços diferentes;
* benefícios diferentes.

Sem um padrão, a lógica ficaria cheia de condicionais:

```python
if tipo == "basica":
    ...

elif tipo == "premium":
    ...

elif tipo == "vip":
    ...
```

Quanto mais categorias fossem adicionadas, maior seria a duplicação de código.

---

#  Por que utilizar Abstract Factory?

O Abstract Factory permite criar famílias de objetos relacionados sem que o restante do sistema saiba como eles são construídos.

Ou seja:
```
Sistema
↓
Escolhe Factory
↓
Factory cria Reserva
↓
Reserva pronta
```

O sistema apenas solicita uma reserva.

Quem conhece todas as regras de criação é a Factory.

---

#  Como implementamos

Foi criado o arquivo:

```text
factories.py
```
Nele implementamos:
```python
ReservaBasicaFactory
ReservaPremiumFactory
ReservaVIPFactory
```
Cada classe é responsável por montar um tipo específico de reserva.

Exemplo:

```python
class ReservaPremiumFactory:

    def criar(...):

        servicos = [
            "Café",
            "Limpeza",
            "WiFi"
        ]

        preco_final = propriedade.preco + 110

        return Reserva(...)
```

Já a Factory VIP adiciona novos benefícios:

```python
class ReservaVIPFactory:

    def criar(...):

        servicos = [
            "Café",
            "Limpeza",
            "WiFi",
            "Concierge"
        ]

        beneficio = "Check-in antecipado"

        return Reserva(...)
```

---

#  Onde é invocado?

Fluxo completo:

```
Usuário
↓
Tela de Reserva
↓
app.py
↓
Sistema.registrar_reserva()
↓
Escolha da Factory
↓
factory.criar(...)
↓
Reserva criada
↓
Banco de Dados
```
Trecho do sistema:

```python
if tipo == "premium":
    factory = ReservaPremiumFactory()

elif tipo == "vip":
    factory = ReservaVIPFactory()

else:
    factory = ReservaBasicaFactory()

return factory.criar(...)
```
---
#  Conceitos de POO utilizados

* Encapsulamento
* Polimorfismo
* Baixo acoplamento
---

#  Benefício obtido

Antes:

```
Sistema
↓
if
↓
if
↓
if
↓
Reserva
```

Depois:

```
Sistema
↓
Factory
↓
Reserva
```

Adicionar uma nova categoria agora significa apenas criar uma nova Factory.

Nenhum código existente precisa ser alterado.

---























#  2. PROXY

## Controla acesso e centraliza validações antes de operações

##  Problema identificado
Durante a análise percebemos que diversas validações estavam espalhadas pelo sistema.

Para reservar:
* validar datas;
* validar disponibilidade;
* validar capacidade;
* validar tipo da reserva.

Para avaliação:
* verificar se houve reserva;
* verificar nota válida;
* verificar duplicidade.

Para chat:
* verificar mensagem vazia;
* verificar tamanho;
* verificar permissões.

As rotas acumulavam muita responsabilidade.

Exemplo:

```python
if data < hoje:
    return erro

if data_final <= data_inicio:
    return erro

if nota > 5:
    return erro
```

---

#  Por que utilizar Proxy?

O Proxy controla o acesso antes que a operação aconteça.
Primeiro o sistema pergunta ao Proxy:
> "Essa operação pode ser realizada?"
Se a resposta for positiva, a operação continua.
Caso contrário, ela é interrompida.

---

#  Como implementamos

Foi criado:

```text
proxies.py
```
Com quatro proxies especializados:
```python
ProxyReserva
ProxyAvaliacao
ProxyChat
ProxyPropriedade
```

Cada um possui uma responsabilidade específica.

Exemplo:

```python
proxy = ProxyReserva(...)

if proxy.pode_reservar():

    sistema.registrar_reserva(...)
```

Internamente:

```python
def pode_reservar():

    if data_inicio < hoje:
        return False

    if data_fim <= data_inicio:
        return False

    if conflito_datas:
        return False

    if tipo not in ["basica","premium","vip"]:
        return False

    return True
```

---

#  Onde é invocado?

Fluxo:

```
Usuário
↓
app.py
↓
ProxyReserva
↓
Validação
↓
Sistema
↓
Banco
```

Na rota:

```python
proxy = ProxyReserva(...)

if not proxy.pode_reservar():

    erro = proxy.obter_erro()

    return render_template(...)

meu_pousala.registrar_reserva(...)
```

Somente após a validação o sistema realiza a operação.

---

#  Conceitos de POO utilizados

* Encapsulamento
* Composição

---

#  Benefício obtido

Antes:

```
Rota
↓
20 validações
↓
Operação
```

Depois:

```
Rota
↓
Proxy
↓
Operação
```
Se uma regra mudar, basta alterar o Proxy.
---












#  3. MEDIATOR

## Reduz o acoplamento entre objetos que precisam se comunicar. 

##  Problema identificado

O sistema possui comunicação entre:

* hóspede;
* anfitrião.

Se essa comunicação fosse direta, haveria alto acoplamento entre as classes.

Além disso, funcionalidades futuras como:

* notificações;
* histórico;
* auditoria;

ficariam espalhadas pelo projeto.

---

#  Por que utilizar Mediator?

O Mediator centraliza toda comunicação.

Antes:

```
Hospede
↔
Anfitrião
```

Depois:

```
Hospede
↓
ChatMediator
↓
Anfitrião
```

---

#  Como implementamos

Foi criado:

```text
mediator.py
```
Classe principal:
```python
ChatMediator
```

Ela é responsável por:

* validar comunicação;
* enviar mensagens;
* registrar histórico;
* gerenciar notificações.

Método principal:

```python
def enviar_mensagem(...):

    validar()

    salvar()

    notificar()

    return sucesso
```

---

#  Onde é invocado?

Fluxo:

```
Usuário
↓
Tela de Chat
↓
app.py
↓
ProxyChat
↓
Sistema
↓
ChatMediator
↓
Banco de Dados
↓
Notificações
```

Na rota:

```python
if proxy_chat.pode_enviar_mensagem(...):

    meu_pousala.enviar_mensagem(...)
```

Dentro do sistema:

```python
def enviar_mensagem(...):

    return self.chat_mediator.enviar_mensagem(...)
```

Ou seja, o Sistema apenas delega a responsabilidade ao Mediator.

---

#  Conceitos de POO utilizados

* Baixo acoplamento
* Encapsulamento
* Composição

