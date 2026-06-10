
from flask import Flask, render_code, request, jsonify, redirect, url_for, session

app = Flask(__name__)
# Chave secreta necessária para usar sessões de usuário de forma segura
app.secret_key = 'chave_secreta_super_segura_roomify'

# Usuário de demonstração padrão
USER_DEMO = {
    "email": "professor@teste.com",
    "senha": "123456"
}

@app.route('/')
def home():
    # Se o usuário já estiver logado, exibe a página
    # O controle de esconder/mostrar os painéis será feito via JavaScript ou Jinja2
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    
    if email == USER_DEMO['email'] and senha == USER_DEMO['senha']:
        session['user'] = email
        return jsonify({"success": True, "message": "Login realizado com sucesso!"}), 200
    
    return jsonify({"success": False, "message": "E-mail ou senha incorretos."}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
