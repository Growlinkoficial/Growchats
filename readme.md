## Documentação do Projeto: Growchats

### 1\. Visão Geral do Produto

O **Growchats** é uma ferramenta de utilidade web projetada para resolver o problema de arquivamento e *backup* de conversas importantes geradas em plataformas de inteligência artificial (IAs) como ChatGPT.

  * **Propósito:** Permitir que usuários armazenem suas próprias conversas localmente, fora do ecossistema das plataformas de IA, para fins de documentação e referência offline.
  * **Mecanismo:** O usuário fornece o link de compartilhamento da conversa, e a ferramenta extrai o conteúdo do chat em segundo plano e o baixa.
  * **Categoria:** Aplicativo Web (Web App) de Produtividade/Utilidade.
  * **Desafio de Performance:** O processo de extração exige o lançamento de um navegador virtual (*headless*), o que resulta em um tempo de espera de aproximadamente 30 a 60 segundos por requisição.

-----

### 2\. Status Atual e Especificações Técnicas (Fase 2 Concluída)

O projeto está na **Fase 2 (Aplicativo Web)** e foi totalmente migrado do *script* de linha de comando para uma arquitetura Cliente-Servidor (Frontend/Backend).

| Requisito | Detalhe | Status |
| :--- | :--- | :--- |
| **Plataforma Prioritária** | **ChatGPT** (Links compartilhados). | **CONCLUÍDO** |
| **Formato de Saída** | **Markdown (.md)**. | **CONCLUÍDO** |
| **Arquitetura** | Servidor Python (Flask) + Playwright + Frontend (HTML/JS). | **CONCLUÍDO** |
| **Seletor Estável (ChatGPT)** | `article[data-testid^="conversation-turn-"]` | **VALIDADO** |
| **Otimização de Performance** | Lançamento do Playwright com argumentos leves e *timeouts* ajustados para falha rápida (10-20 segundos). | **IMPLEMENTADO** |
| **Funcionalidade Futura** | Suporte a PDF e outras IAs (Gemini, Claude). | *Próxima Etapa* |

-----

### 3\. Estrutura do Projeto (Fase 2: Web App)

A estrutura do projeto utiliza o Flask para servir o *frontend* e gerenciar a API de extração.

```
/projeto-Growchats
├── app.py                  # Servidor principal Flask e rotas API
├── extractor.py            # Lógica de extração do Playwright (Otimizada)
├── templates/
│   └── index.html          # Interface do Usuário (HTML/JS/CSS)
└── venv/                  # Ambiente Virtual
```

-----

### 4\. Requisitos de Instalação e Execução

Para rodar o Aplicativo Web, é necessário ter um ambiente virtual atualizado com as dependências corretas.

1.  **Instalar Python 3.x**.
2.  **Criar ou Ativar o Ambiente Virtual:**
    ```bash
    .\venv\Scripts\activate  # No Windows
    ```
3.  **Instalar as Dependências:**
    ```bash
    pip install Flask playwright
    ```
4.  **Instalar os Drivers do Navegador (Playwright):**
    ```bash
    playwright install
    ```
5.  **Iniciar o Servidor Flask:**
    ```bash
    python app.py
    ```
6.  Acessar no navegador: `http://127.0.0.1:5000/`.

-----

### 5\. Plano de Desenvolvimento (Próximos Passos)

O projeto está totalmente funcional (MVP). Os próximos passos agregam valor para compensar o tempo de espera da extração.

1.  **Prioridade 1: Compensação (Suporte a PDF)**: Implementar a conversão do Markdown extraído para o formato PDF.
      * **Motivação:** Transforma o *output* em um documento profissional, ideal para arquivamento, compensando a longa espera do usuário.
      * **Tecnologia:** Introduzir a biblioteca `WeasyPrint` ou similar para conversão no *backend*.
2.  **Prioridade 2: Expansão (Suporte Multi-IA)**: Adaptar o `extractor.py` para reconhecer e extrair conversas de outras plataformas (Gemini, Claude).
      * **Motivação:** Amplia a utilidade do produto para o ecossistema completo de IAs.
3.  **Sugestão de Performance Futura:** Investigar a viabilidade da migração para um *backend* assíncrono (ex: Celery/Redis) para mover a extração para segundo plano e responder ao usuário em menos de 1 segundo.