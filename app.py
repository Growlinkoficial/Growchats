# app.py - Versão Simplificada Sem Cache

import os
from flask import Flask, request, render_template, send_file
from extractor import extract_conversation # Importa sua função de extração
from io import BytesIO
import json

app = Flask(__name__)

# Rota Principal: Serve o HTML
@app.route('/')
def index():
    return render_template('index.html')

# Rota API: Recebe o link e retorna o arquivo
@app.route('/api/download', methods=['POST'])
def download():
    # 1. Pega o URL do formulário (JSON)
    try:
        data = request.get_json()
        chat_url = data.get('url')
    except Exception:
        return {"error": "Corpo da requisição inválido."}, 400

    if not chat_url:
        return {"error": "URL do chat não fornecida."}, 400

    # 2. Executa a extração
    print(f"[APP] Chamando extractor para: {chat_url}")
    result = extract_conversation(chat_url)

    # 3. Verifica se a extração falhou (retorna uma tupla de erro)
    if isinstance(result, tuple):
        # Result é uma tupla (mensagem_erro, código_http)
        return {"error": result[0]}, result[1]
    
    # 4. Extração bem-sucedida: Prepara o arquivo para download
    markdown_content = result
    
    # 5. Cria um arquivo em memória e o envia
    buffer = BytesIO()
    buffer.write(markdown_content.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='conversa_arquivada.md',
        mimetype='text/markdown'
    )


if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    print("Servidor Flask Simplificado pronto. Acesse http://127.0.0.1:5000/")
    app.run(debug=True)