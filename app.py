import urllib.parse
from datetime import datetime
from flask import Flask, render_template, request, session, redirect
from sistema import Sistema, Anfitriao, Hospede
from proxies import ProxyPropriedade, ProxyChat, ProxyAvaliacao, ProxyReserva  # ← NOVO: Importa Proxies 

app = Flask(__name__)
app.secret_key = "chave_pousala_2024"
meu_pousala = Sistema() #abstracao

@app.route('/', methods=['GET', 'POST'])
def index():
    res = []
    erro_data = None
    if request.method == 'POST':
        loc = request.form.get('localizacao')
        cap = int(request.form.get('capacidade'))
        d_in = request.form.get('data_inicio')
        d_out = request.form.get('data_fim')
        
        # VALIDAÇÃO DE DATAS NA BUSCA
        hoje = datetime.now().strftime('%Y-%m-%d')
        if d_in < hoje:
            erro_data = "Ops! Você não pode viajar para o passado."
        elif d_out <= d_in:
            erro_data = "O check-out deve ser pelo menos um dia após o check-in."
        else:
            res = meu_pousala.buscar(loc, cap, d_in, d_out) #abstracao
            
    favs = [p.nome for p in meu_pousala.obter_favoritos_usuario(session.get('usuario_email'))] if 'usuario_email' in session else []
    return render_template('index.html', resultados=res, favs_usuario=favs, erro_data=erro_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        u = meu_pousala.fazer_login(request.form.get('email'), request.form.get('senha')) #abstracao
        if u: 
            session['usuario_nome'] = u['nome']
            session['usuario_email'] = u['email']
            session['usuario_tipo'] = u['tipo']
            return redirect('/')
        else:
            erro = "Ops! Conta não encontrada ou senha incorreta."
            
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect('/')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        n = request.form.get('nome')
        e = request.form.get('email')
        s = request.form.get('senha')
        t = request.form.get('tipo')
        
        if t == 'hospede': 
            meu_pousala.cadastrar_hospede(n, e, s) #abstracao
        else: 
            meu_pousala.cadastrar_anfitriao(n, e, s) #abstracao
        return redirect('/login')
    return render_template('cadastro.html')

@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    if session.get('usuario_tipo') != 'anfitriao': return redirect('/')
    msg = None
    if request.method == 'POST':
        p = meu_pousala.anunciar_propriedade( #abstracao
            Anfitriao(session['usuario_nome'], session['usuario_email'], ""), 
            request.form.get('nome'), 
            request.form.get('localizacao'), 
            int(request.form.get('capacidade')), 
            float(request.form.get('preco'))
        )
        msg = "Sucesso! Anúncio publicado." if p else "Erro: Nome da propriedade já existe."
    return render_template('anunciar.html', mensagem=msg)

@app.route('/reservar/<nome>', methods=['GET', 'POST'])
def reservar(nome):
    if 'usuario_email' not in session: return redirect('/login')
    p = next((x for x in meu_pousala.propriedades if x.nome == urllib.parse.unquote(nome)), None)
    
    erro_reserva = None
    mensagem_reserva = None
    preco_estimado = None
    
    if request.method == 'POST':
        d_in = request.form.get('data_inicio')
        d_out = request.form.get('data_fim')
        tipo_reserva = request.form.get('tipo_reserva', 'basica')
        
        # ============== PROXY: VALIDA RESERVA ==============
        proxy_reserva = ProxyReserva(
            p, 
            Hospede(session['usuario_nome'], session['usuario_email'], ""),
            d_in,
            d_out,
            tipo_reserva=tipo_reserva
        )
        
        if proxy_reserva.pode_reservar():
            # Se validou, faz a reserva
            res = meu_pousala.registrar_reserva(
                Hospede(session['usuario_nome'], session['usuario_email'], ""), 
                p, 
                d_in, 
                d_out,
                tipo_reserva=tipo_reserva
            )
            mensagem_reserva = f"✅ Reserva {res.tipo.upper()} confirmada! Preço total: R${res.preco_final:.2f}"
        else:
            # Se não validou, exibe erro do proxy
            erro_reserva = proxy_reserva.obter_erro()
            # Calcula preço estimado mesmo com erro para mostrar ao usuário
            if d_in and d_out:
                preco_estimado = proxy_reserva.obter_preco_estimado()
            
    return render_template('reserva.html', propriedade=p, erro=erro_reserva, mensagem=mensagem_reserva, preco_estimado=preco_estimado)

@app.route('/avaliar/<nome>', methods=['GET', 'POST'])
def avaliar(nome):
    if 'usuario_email' not in session: return redirect('/login')
    p = next((x for x in meu_pousala.propriedades if x.nome == urllib.parse.unquote(nome)), None)
    
    # ============== PROXY: VALIDA AVALIAÇÃO ==============
    proxy_avaliacao = ProxyAvaliacao(p, session['usuario_email'])
    
    mensagem = None
    erro = None
    
    if request.method == 'POST':
        nota = request.form.get('nota')
        comentario = request.form.get('comentario')
        
        # Proxy valida se pode avaliar
        if proxy_avaliacao.pode_avaliar(nota, comentario):
            # Se validou, registra avaliação
            meu_pousala.registrar_avaliacao(p.nome, session['usuario_nome'], int(nota), comentario)
            mensagem = "Obrigado pela sua avaliação!"
        else:
            # Se não validou, exibe erro do proxy
            erro = proxy_avaliacao.obter_erro()
    
    return render_template('avaliar.html', propriedade=p, mensagem=mensagem, erro=erro)

@app.route('/duvidas/<nome>')
def duvidas(nome):
    p_nome = urllib.parse.unquote(nome)
    p = next((x for x in meu_pousala.propriedades if x.nome == p_nome), None)
    lista_duvidas = meu_pousala.obter_duvidas(p_nome) #abstracao
    return render_template('duvidas.html', propriedade=p, duvidas=lista_duvidas)

@app.route('/chat/<nome>/<h_email>', methods=['GET', 'POST'])
def chat(nome, h_email):
    if 'usuario_email' not in session: return redirect('/login')
    p_nome = urllib.parse.unquote(nome)
    p = next((x for x in meu_pousala.propriedades if x.nome == p_nome), None)
    
    a_e = p.anfitriao.email.strip().lower()
    h_e = h_email.strip().lower()
    log = session['usuario_email'].strip().lower()
    
    # ============== PROXY: VALIDA CHAT ==============
    proxy_chat = ProxyChat(p, h_e, a_e, meu_pousala)
    
    erro_chat = None
    
    # Valida acesso básico
    if log not in [a_e, h_e]:
        return "Acesso negado. Você não pertence a este chat.", 403
    
    if request.method == 'POST':
        texto = request.form.get('texto')
        
        # Proxy valida se pode enviar mensagem
        if proxy_chat.pode_enviar_mensagem(log, texto):
            meu_pousala.enviar_mensagem(p_nome, log, a_e if log == h_e else h_e, texto)
        else:
            erro_chat = proxy_chat.obter_erro()
        
    msgs = meu_pousala.obter_mensagens(p_nome, h_e, a_e)
    return render_template('chat.html', propriedade=p, mensagens=msgs, logado=log, hospede_email=h_e, erro=erro_chat)

@app.route('/painel', methods=['GET', 'POST'])
def painel():
    if session.get('usuario_tipo') != 'anfitriao': return redirect('/')
    e_log = session['usuario_email'].strip().lower()
    
    if request.method == 'POST':
        meu_pousala.registrar_duvida(request.form.get('prop_nome'), request.form.get('pergunta'), request.form.get('resposta'))
        
    anf = Anfitriao(session['usuario_nome'], e_log, "")
    for p in meu_pousala.propriedades:
        if p.anfitriao.email.strip().lower() == e_log: 
            anf.anunciar_propriedade(p)
            
    chats = meu_pousala.obter_chats_usuario(e_log)
    return render_template('painel.html', anfitriao=anf, contatos_chat=chats)

@app.route('/minhas_reservas')
def minhas_reservas():
    if session.get('usuario_tipo') != 'hospede': return redirect('/')
    e_log = session['usuario_email'].strip().lower()
    viagens = []
    
    for p in meu_pousala.propriedades:
        for r in p.reservas:
            if r.hospede.email.strip().lower() == e_log: 
                viagens.append({'propriedade': p.nome, 'localizacao': p.localizacao, 'data_inicio': r.data_inicio, 'data_fim': r.data_fim, 'status': r.status})
                
    chats = meu_pousala.obter_chats_usuario(e_log)
    return render_template('minhas_reservas.html', reservas=viagens, contatos_chat=chats)

@app.route('/favoritar/<nome>', methods=['POST'])
def favoritar(nome):
    if 'usuario_email' not in session: return redirect('/login')
    meu_pousala.toggle_favorito(session['usuario_email'], urllib.parse.unquote(nome))
    return redirect(request.referrer or '/')

@app.route('/meus_favoritos')
def meus_favoritos():
    if 'usuario_email' not in session: return redirect('/')
    f = meu_pousala.obter_favoritos_usuario(session['usuario_email'])
    return render_template('favoritos.html', propriedades=f)

if __name__ == '__main__': 
    app.run(debug=True, use_reloader=False) 