from flask import Flask, render_template, request, redirect, url_for
from database import criar_tabelas
from models import Sistema

app = Flask(__name__)
DB_PATH = 'leituras.db'
criar_tabelas(DB_PATH)
sistema = Sistema(DB_PATH)

@app.route('/')
def index():
    usuarios = sistema.usuarios.values()
    return render_template('index.html', usuarios=usuarios)

@app.route('/usuario/<int:usuario_id>')
def dashboard_usuario(usuario_id):
    usuario = sistema.usuarios.get(usuario_id)
    if usuario:
        livros_lidos = sistema.obter_livros_lidos_usuario(usuario_id)
        return render_template('dashboard.html', usuario=usuario, livros_lidos=livros_lidos)
    return "Usuário não encontrado", 404

@app.route('/adicionar_usuario', methods=['POST'])
def adicionar_usuario():
    nome = request.form['nome']
    sistema.adicionar_usuario(nome)
    return redirect(url_for('index'))

@app.route('/adicionar_leitura', methods=['POST'])
def adicionar_leitura():
    usuario_id = int(request.form.get('usuario_id', 0))
    if usuario_id not in sistema.usuarios:
        return "Usuário inválido", 400

    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    genero = request.form.get('genero', '')
    palavras_chave = request.form.get('palavras_chave', '')

    # Tenta encontrar livro existente
    livro_existente = None
    for livro in sistema.livros.values():
        if livro.titulo.lower() == titulo.lower() and livro.autor.lower() == autor.lower():
            livro_existente = livro
            break

    # Se não existe, cria
    if not livro_existente:
        livro_existente = sistema.adicionar_livro(titulo, autor, genero, palavras_chave)

    # Registra a leitura para o usuário
    sistema.registrar_leitura(usuario_id, livro_existente.id)

    return redirect(url_for('dashboard_usuario', usuario_id=usuario_id))


@app.route('/recomendar/<int:usuario_id>')
def recomendar_leituras(usuario_id):
    usuario = sistema.usuarios.get(usuario_id)
    if usuario:
        recomendacoes = sistema.gerar_recomendacoes(usuario_id)
        return render_template('recommendations.html', usuario=usuario, recomendacoes=recomendacoes)
    return "Usuário não encontrado", 404

if __name__ == '__main__':
    app.run(debug=True)
