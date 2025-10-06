# app.py - Versão Corrigida para Conexão com Backend
import os
from flask import Flask, request, render_template, send_file, jsonify, url_for
# --- ALTERAÇÃO 1: Importe também o celery_app ---
from tasks import run_extraction_task, celery_app
from celery.result import AsyncResult
from io import BytesIO

app = Flask(__name__)

# Rota Principal: Serve o HTML
@app.route('/')
def index():
    return render_template('index.html')

# Rota API: Inicia a tarefa de extração
@app.route('/api/start-extraction', methods=['POST'])
def start_extraction():
    try:
        data = request.get_json()
        chat_url = data.get('url')
    except Exception:
        return jsonify({"error": "Corpo da requisição inválido."}), 400

    if not chat_url:
        return jsonify({"error": "URL do chat não fornecida."}), 400

    task = run_extraction_task.delay(chat_url)
    
    return jsonify({
        "task_id": task.id,
        "status_url": url_for('get_task_status', task_id=task.id)
    }), 202

# Rota API: Verifica o status de uma tarefa
@app.route('/api/status/<task_id>')
def get_task_status(task_id):
    # --- ALTERAÇÃO 2: Passe o app para o AsyncResult ---
    task = AsyncResult(task_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pendente...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': 'Processando...'}
        if task.state == 'SUCCESS':
            response['status'] = 'Concluído!'
            response['download_url'] = url_for('download_file', task_id=task.id)
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

# Rota API: Faz o download do arquivo quando a tarefa está pronta
@app.route('/api/download/<task_id>')
def download_file(task_id):
    # --- ALTERAÇÃO 3: Passe o app aqui também para consistência ---
    task = AsyncResult(task_id, app=celery_app)
    if not task.ready() or task.failed():
        return jsonify({"error": "O arquivo não está pronto ou a tarefa falhou."}), 404
        
    markdown_content = task.result
    
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
        
    print("Servidor Flask Assíncrono pronto. Acesse http://127.0.0.1:5000/")
    app.run(debug=True)