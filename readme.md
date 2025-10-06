# Growchats

### Visão Geral do Produto

O **Growchats** é uma ferramenta de utilidade web projetada para resolver o problema de arquivamento e *backup* de conversas importantes geradas em plataformas de inteligência artificial (IAs) como ChatGPT.

-   **Propósito:** Permitir que usuários armazenem suas próprias conversas localmente, fora do ecossistema das plataformas de IA, para fins de documentação e referência offline.
-   **Mecanismo:** O usuário fornece o link de compartilhamento da conversa, e a ferramenta executa a extração do conteúdo em segundo plano, notificando o usuário quando o download está pronto.
-   **Categoria:** Aplicativo Web (Web App) de Produtividade/Utilidade.

-----

### Arquitetura e Especificações Técnicas (Fase 3: Assíncrona)

O projeto evoluiu para uma arquitetura assíncrona para proporcionar uma experiência de usuário superior, eliminando a necessidade de esperar pelo processamento da extração em tempo real.

| Requisito | Detalhe | Status |
| :--- | :--- | :--- |
| **Arquitetura** | **Backend Assíncrono** com Flask, Celery e Redis. | **CONCLUÍDO** |
| **Plataforma Prioritária** | **ChatGPT** (Links compartilhados). | **CONCLUÍDO** |
| **Formato de Saída** | **Markdown (.md)**. | **CONCLUÍDO** |
| **Experiência do Usuário** | Feedback instantâneo com barra de progresso e cronômetro. | **CONCLUÍDO** |
| **Estabilidade** | Timeouts do Playwright ajustados para 90s para garantir a conclusão de extrações longas. | **IMPLEMENTADO** |

-----

### Estrutura do Projeto

/growchats
├── app.py                  # Servidor Flask (gerencia tarefas e status)
├── tasks.py                # Define a tarefa Celery que executa a extração
├── extractor.py            # Lógica de extração com Playwright
├── templates/
│   └── index.html          # Interface do Usuário (HTML/JS/CSS)
├── requirements.txt        # Lista de dependências do projeto
└── venv/                   # Ambiente Virtual

-----

### Requisitos de Instalação e Execução

Para rodar a aplicação, é necessário ter Python, Redis e as dependências do projeto instaladas.

1.  **Instalar Python 3.x**.
2.  **Instalar o Redis:** A forma mais simples é utilizando Docker:
    ```bash
    docker run -d -p 6379:6379 redis
    ```
3.  **Criar e Ativar o Ambiente Virtual:**
    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Instalar as Dependências do Projeto:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Instalar os Drivers do Navegador (Playwright):**
    ```bash
    playwright install
    ```

### Como Executar

A aplicação agora requer **três processos** rodando simultaneamente em **três terminais separados**:

1.  **Terminal 1: Iniciar o Redis** (se ainda não estiver rodando).
    ```bash
    docker start <container_id_do_redis>
    ```

2.  **Terminal 2: Iniciar o Worker do Celery:**
    *Este processo é o "trabalhador" que executa as extrações em segundo plano.*
    ```bash
    # (Com o venv ativado)
    celery -A tasks.celery_app worker --loglevel=info -P gevent
    ```

3.  **Terminal 3: Iniciar o Servidor Flask:**
    *Este processo serve a interface web para o usuário.*
    ```bash
    # (Com o venv ativado)
    python app.py
    ```

4.  **Acessar a Aplicação:** Abra seu navegador e acesse `http://127.0.0.1:5000/`.

-----

### Plano de Desenvolvimento (Próximos Passos)

Com a arquitetura assíncrona implementada, o projeto está robusto e escalável. Os próximos passos focam em agregar mais valor ao usuário.

1.  **Prioridade 1: Suporte a PDF**: Implementar a conversão do Markdown extraído para o formato PDF, oferecendo um formato de arquivo mais profissional.
2.  **Prioridade 2: Suporte Multi-IA**: Adaptar o `extractor.py` para reconhecer e extrair conversas de outras plataformas (Gemini, Claude).