import json
from datetime import datetime
from flask import Flask, jsonify, request, abort, url_for

app = Flask(__name__)

livros_db = {
    1: {
        "id": 1, "titulo": "Clean Architecture", "isbn": "978-0134494166",
        "ano_publicacao": 2017, "disponivel": True, "autor_id": 1
    },
    2: {
        "id": 2, "titulo": "The Pragmatic Programmer", "isbn": "978-0201616224",
        "ano_publicacao": 1999, "disponivel": False, "autor_id": 2
    },
    3: {
        "id": 3, "titulo": "Refactoring", "isbn": "978-0134757599",
        "ano_publicacao": 2018, "disponivel": True, "autor_id": 3
    }
}
autores_db = {
    1: {"id": 1, "nome": "Robert C. Martin"},
    2: {"id": 2, "nome": "Andrew Hunt"},
    3: {"id": 3, "nome": "Martin Fowler"}
}
emprestimos_db = {
    123: {"id": 123, "livro_id": 2, "status": "ATIVO"}
}

# Helpers 

def get_autor_details(autor_id):
    return autores_db.get(autor_id)

def add_hateoas_links(livro):
    livro_id = livro['id']
    livro['_links'] = [
        {"rel": "self", "href": url_for('get_livro', livro_id=livro_id, _external=True), "method": "GET"},
        {"rel": "update", "href": url_for('update_livro', livro_id=livro_id, _external=True), "method": "PUT"},
        {"rel": "delete", "href": url_for('delete_livro', livro_id=livro_id, _external=True), "method": "DELETE"}
    ]
    if livro['disponivel']:
        livro['_links'].append(
            {"rel": "emprestar", "href": "/emprestimos", "method": "POST"}
        )
    else:
        emprestimo_id = next((eid for eid, emp in emprestimos_db.items() if emp['livro_id'] == livro_id and emp['status'] == 'ATIVO'), None)
        if emprestimo_id:
            livro['_links'].append(
                {"rel": "devolver", "href": f"/emprestimos/{emprestimo_id}/devolucao", "method": "PUT"}
            )
    return livro

def expand_livro(livro):
    livro_copy = livro.copy()
    autor_id = livro_copy.pop('autor_id', None)
    if autor_id:
        livro_copy['autor'] = get_autor_details(autor_id)
    return add_hateoas_links(livro_copy)

# Error Handling

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "erro": "Recurso não encontrado", "codigo": 404,
        "timestamp": datetime.utcnow().isoformat() + "Z", "caminho": request.path
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "erro": "Requisição inválida", "mensagem": error.description, "codigo": 400,
        "timestamp": datetime.utcnow().isoformat() + "Z", "caminho": request.path
    }), 400

# Endpoints

@app.route('/livros', methods=['GET'])
def get_livros():
    livros_list = list(livros_db.values())
    autor_nome = request.args.get('autor')
    disponivel_str = request.args.get('disponivel')
    if autor_nome:
        autor_id_match = next((aid for aid, autor in autores_db.items() if autor_nome.lower() in autor['nome'].lower()), None)
        if autor_id_match:
            livros_list = [livro for livro in livros_list if livro['autor_id'] == autor_id_match]
    if disponivel_str is not None:
        disponivel = disponivel_str.lower() == 'true'
        livros_list = [livro for livro in livros_list if livro['disponivel'] == disponivel]
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    if sort_by in ['id', 'titulo', 'ano_publicacao']:
        livros_list.sort(key=lambda x: x[sort_by], reverse=(order == 'desc'))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    start_index = (page - 1) * size
    end_index = start_index + size
    paginated_list = livros_list[start_index:end_index]
    result = [expand_livro(livro) for livro in paginated_list]
    return jsonify(result)

@app.route('/livros/<int:livro_id>', methods=['GET'])
def get_livro(livro_id):
    livro = livros_db.get(livro_id)
    if not livro:
        abort(404)
    return jsonify(expand_livro(livro))

@app.route('/livros', methods=['POST'])
def create_livro():
    data = request.get_json()
    if not data or 'titulo' not in data or 'autor_id' not in data:
        abort(400, description="Dados incompletos. 'titulo' e 'autor_id' são obrigatórios.")
    if data['autor_id'] not in autores_db:
        abort(400, description=f"Autor com id {data['autor_id']} não existe.")
    new_id = max(livros_db.keys()) + 1
    novo_livro = {
        'id': new_id, 'titulo': data['titulo'], 'isbn': data.get('isbn', ''),
        'ano_publicacao': data.get('ano_publicacao'), 'disponivel': data.get('disponivel', True),
        'autor_id': data['autor_id']
    }
    livros_db[new_id] = novo_livro
    return jsonify(expand_livro(novo_livro)), 201

@app.route('/livros/<int:livro_id>', methods=['PUT'])
def update_livro(livro_id):
    if livro_id not in livros_db:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400, description="Nenhum dado fornecido para atualização.")
    if 'autor_id' in data and data['autor_id'] not in autores_db:
         abort(400, description=f"Autor com id {data['autor_id']} não existe.")
    livro = livros_db[livro_id]
    livro.update(data)
    livros_db[livro_id] = livro
    return jsonify(expand_livro(livro))

@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def delete_livro(livro_id):
    if livro_id not in livros_db:
        abort(404)
    del livros_db[livro_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)