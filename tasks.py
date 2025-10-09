# tasks.py - Versão com Segurança e Logging Melhorado
from celery import Celery
from extractor import extract_conversation
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configura o Celery para usar o Redis como broker e backend de resultados
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# Configurações de segurança do Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutos máximo por tarefa
    task_soft_time_limit=270,  # Aviso após 4.5 minutos
    worker_max_tasks_per_child=50,  # Reinicia worker após 50 tarefas (previne memory leaks)
)

@celery_app.task(bind=True, max_retries=2)
def run_extraction_task(self, url: str):
    """
    Tarefa Celery que executa a extração de conversa.
    Retorna o conteúdo Markdown em caso de sucesso ou uma mensagem de erro.
    
    Args:
        url: URL da conversa a ser extraída
        
    Returns:
        str: Conteúdo da conversa em Markdown
        
    Raises:
        Exception: Se a extração falhar
    """
    try:
        logger.info(f"[CELERY TASK {self.request.id}] Iniciando extração para: {url}")
        
        result = extract_conversation(url)
        
        # Se a extração retornar uma tupla de erro, a tratamos
        if isinstance(result, tuple):
            error_message = result[0]
            logger.error(f"[CELERY TASK {self.request.id}] Erro na extração: {error_message}")
            # Lançamos uma exceção para que o Celery marque a tarefa como FALHA
            raise Exception(error_message)
        
        # Validar resultado
        if not result or not isinstance(result, str):
            raise Exception("Resultado da extração inválido")
        
        if len(result) < 50:  # Muito curto para ser uma conversa real
            raise Exception("Conversa extraída está muito curta. Verifique a URL.")
        
        logger.info(f"[CELERY TASK {self.request.id}] Extração concluída com sucesso. Tamanho: {len(result)} caracteres")
        return result
        
    except Exception as e:
        logger.error(f"[CELERY TASK {self.request.id}] Erro fatal: {str(e)}")
        # Tentar novamente em caso de erro transitório
        if self.request.retries < self.max_retries:
            logger.info(f"[CELERY TASK {self.request.id}] Tentando novamente... (tentativa {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=30)  # Espera 30s antes de tentar novamente
        raise