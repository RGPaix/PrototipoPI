import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def recommend_books(livros_lidos, todos_livros, num_recomendacoes=5):
    if not livros_lidos or not todos_livros:
        return []

    # Criar um DataFrame com todos os livros
    df_livros = pd.DataFrame([{
        'id': livro.id,
        'titulo': livro.titulo,
        'autor': livro.autor,
        'genero': livro.genero,
        'palavras_chave': livro.palavras_chave
    } for livro in todos_livros])

    # Combinar atributos para similaridade de conteúdo
    df_livros['conteudo'] = df_livros['titulo'].fillna('') + ' ' + \
                             df_livros['autor'].fillna('') + ' ' + \
                             df_livros['genero'].fillna('') + ' ' + \
                             df_livros['palavras_chave'].fillna('')

    # Calcular a matriz TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_livros['conteudo'])

    # Calcular a similaridade do cosseno
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Obter os índices dos livros lidos
    indices_livros_lidos = df_livros[df_livros['id'].isin([livro.id for livro in livros_lidos])].index

    # Calcular a similaridade média dos livros lidos com todos os outros livros
    sim_scores = list(enumerate(cosine_sim[indices_livros_lidos].mean(axis=0)))

    # Ordenar os livros por similaridade
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Obter os IDs dos livros recomendados (excluindo os já lidos)
    recomendacoes_ids = []
    for i, score in sim_scores:
        livro_id = df_livros.iloc[i]['id']
        if livro_id not in [livro.id for livro in livros_lidos]:
            recomendacoes_ids.append(livro_id)
        if len(recomendacoes_ids) >= num_recomendacoes:
            break

    return recomendacoes_ids
