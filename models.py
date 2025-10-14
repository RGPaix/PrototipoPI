import sqlite3
from ia import recommend_books

def criar_tabelas(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT,
            genero TEXT,
            palavras_chave TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_livros (
            usuario_id INTEGER,
            livro_id INTEGER,
            PRIMARY KEY (usuario_id, livro_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (livro_id) REFERENCES livros(id)
        )
    ''')

    conn.commit()
    conn.close()


class Livro:
    def __init__(self, id, titulo, autor, genero, palavras_chave):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.palavras_chave = palavras_chave


class Usuario:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome
        self.livros_lidos = set()

    def adicionar_livro_lido(self, livro_id):
        self.livros_lidos.add(livro_id)


class Sistema:
    def __init__(self, db_path='leituras.db'):
        self.db_path = db_path
        self.usuarios = {}
        self.livros = {}
        self._carregar_dados()

    def _carregar_dados(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Carregar livros
        cursor.execute("SELECT id, titulo, autor, genero, palavras_chave FROM livros")
        for row in cursor.fetchall():
            livro = Livro(*row)
            self.livros[livro.id] = livro

        # Carregar usuários
        cursor.execute("SELECT id, nome FROM usuarios")
        for row in cursor.fetchall():
            usuario = Usuario(*row)
            self.usuarios[usuario.id] = usuario

        # Carregar leituras
        cursor.execute("SELECT usuario_id, livro_id FROM usuarios_livros")
        for usuario_id, livro_id in cursor.fetchall():
            if usuario_id in self.usuarios:
                self.usuarios[usuario_id].adicionar_livro_lido(livro_id)

        conn.close()

    def adicionar_usuario(self, nome):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome) VALUES (?)", (nome,))
        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()
        novo_usuario = Usuario(usuario_id, nome)
        self.usuarios[usuario_id] = novo_usuario
        return novo_usuario

    def adicionar_livro(self, titulo, autor, genero, palavras_chave):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livros (titulo, autor, genero, palavras_chave) VALUES (?, ?, ?, ?)",
            (titulo, autor, genero, palavras_chave)
        )
        livro_id = cursor.lastrowid
        conn.commit()
        conn.close()
        novo_livro = Livro(livro_id, titulo, autor, genero, palavras_chave)
        self.livros[livro_id] = novo_livro
        return novo_livro

    def registrar_leitura(self, usuario_id, livro_id):
        if usuario_id in self.usuarios and livro_id in self.livros:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO usuarios_livros (usuario_id, livro_id) VALUES (?, ?)",
                               (usuario_id, livro_id))
                conn.commit()
                self.usuarios[usuario_id].adicionar_livro_lido(livro_id)
            except sqlite3.IntegrityError:
                pass  # leitura já registrada
            conn.close()

    def obter_livros_lidos_usuario(self, usuario_id):
        if usuario_id in self.usuarios:
            return [self.livros[livro_id]
                    for livro_id in self.usuarios[usuario_id].livros_lidos
                    if livro_id in self.livros]
        return []

    def gerar_recomendacoes(self, usuario_id, num_recomendacoes=5):
        if usuario_id in self.usuarios:
            livros_lidos = self.obter_livros_lidos_usuario(usuario_id)
            todos_livros = list(self.livros.values())
            recomendacoes_ids = recommend_books(livros_lidos, todos_livros, num_recomendacoes)
            return [self.livros[livro_id] for livro_id in recomendacoes_ids if livro_id in self.livros]
        return []