# app.py - Versão Segura com Rate Limiting e Validações
import os
from flask import Flask, request, render_template, send_file, jsonify, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tasks import run_extraction_task, celery_app
from celery.result import AsyncResult
from io import BytesIO

app = Flask(__name__)

# Configuração de segurança
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limita upload a 16MB

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Headers de segurança
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Rota Principal: Serve o HTML
@app.route('/')
def index():
    return render_template('index.html')

# Rota API: Inicia a tarefa de extração
@app.route('/api/start-extraction', methods=['POST'])
@limiter.limit("5 per minute")  # Máximo 5 extrações por minuto
def start_extraction():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio."}), 400
            
        chat_url = data.get('url', '').strip()
    except Exception:
        return jsonify({"error": "Corpo da requisição inválido."}), 400

    if not chat_url:
        return jsonify({"error": "URL do chat não fornecida."}), 400
    
    # Validação básica de comprimento
    if len(chat_url) > 2048:
        return jsonify({"error": "URL muito longa."}), 400

    try:
        task = run_extraction_task.delay(chat_url)
        
        return jsonify({
            "task_id": task.id,
            "status_url": url_for('get_task_status', task_id=task.id)
        }), 202
    except Exception as e:
        app.logger.error(f"Erro ao iniciar tarefa: {str(e)}")
        return jsonify({"error": "Erro ao processar requisição."}), 500

# Rota API: Verifica o status de uma tarefa
@app.route('/api/status/<task_id>')
@limiter.limit("30 per minute")  # Permite polling frequente
def get_task_status(task_id):
    # Validação simples do task_id (deve ser UUID)
    if not task_id or len(task_id) > 100:
        return jsonify({"error": "Task ID inválido."}), 400
    
    try:
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
    except Exception as e:
        app.logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({"error": "Erro ao verificar status."}), 500

# Rota API: Faz o download do arquivo quando a tarefa está pronta
@app.route('/api/download/<task_id>')
@limiter.limit("10 per minute")  # Limita downloads
def download_file(task_id):
    # Validação do task_id
    if not task_id or len(task_id) > 100:
        return jsonify({"error": "Task ID inválido."}), 400
    
    try:
        task = AsyncResult(task_id, app=celery_app)
        
        if not task.ready():
            return jsonify({"error": "O arquivo ainda não está pronto."}), 425
        
        if task.failed():
            return jsonify({"error": "A tarefa falhou."}), 404
            
        markdown_content = task.result
        
        if not markdown_content or not isinstance(markdown_content, str):
            return jsonify({"error": "Conteúdo inválido."}), 500
        
        buffer = BytesIO()
        buffer.write(markdown_content.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='conversa_arquivada.md',
            mimetype='text/markdown'
        )
    except Exception as e:
        app.logger.error(f"Erro no download: {str(e)}")
        return jsonify({"error": "Erro ao processar download."}), 500

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Verificar variáveis de ambiente críticas
    if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
        app.logger.warning("⚠️  ATENÇÃO: Usando SECRET_KEY padrão. Configure uma chave segura em produção!")
    
    flask_env = os.getenv('FLASK_ENV', 'production')
    is_debug = flask_env == 'development'
    
    print(f"Servidor Flask iniciando em modo: {flask_env}")
    print(f"Debug: {is_debug}")
    print("Acesse http://127.0.0.1:5000/")
    
    app.run(debug=is_debug, host='0.0.0.0', port=5000)