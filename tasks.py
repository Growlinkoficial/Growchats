# tasks.py
from celery import Celery
from extractor import extract_conversation
import os

# Configura o Celery para usar o Redis como broker e backend de resultados
# A URL do Redis pode ser configurada por variável de ambiente ou hardcoded
# para desenvolvimento local.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# ✨ NOVO: Otimizações para economizar RAM e melhorar performance
celery_app.conf.update(
    worker_prefetch_multiplier=1,      # Processa 1 tarefa por vez (evita sobrecarga)
    worker_max_tasks_per_child=10,     # Reinicia worker após 10 tarefas (evita memory leak)
)

@celery_app.task
def run_extraction_task(url: str):
    """
    Tarefa Celery que executa a extração de conversa.
    Retorna o conteúdo Markdown em caso de sucesso ou uma mensagem de erro.
    """
    print(f"[CELERY TASK] Iniciando extração para: {url}")
    result = extract_conversation(url)
    
    # Se a extração retornar uma tupla de erro, a tratamos
    if isinstance(result, tuple):
        # Lançamos uma exceção para que o Celery marque a tarefa como FALHA
        # e possamos capturar o erro no frontend.
        raise Exception(result[0])
        
    # Se for bem-sucedido, retorna o conteúdo
    return result