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
| **Otimização** | Consumo de RAM otimizado para máquinas com desempenho reduzido. | **IMPLEMENTADO** |

-----

### Estrutura do Projeto

```
/growchats
├── app.py                  # Servidor Flask (gerencia tarefas e status)
├── tasks.py                # Define a tarefa Celery que executa a extração
├── extractor.py            # Lógica de extração com Playwright
├── start.py                # ✨ Inicializador unificado (recomendado)
├── docker-compose.yml      # ✨ Configuração simplificada do Redis
├── requirements.txt        # Lista de dependências do projeto
├── templates/
│   └── index.html          # Interface do Usuário (HTML/JS/CSS)
├── utils/                  # ✨ Utilitários opcionais
│   ├── monitor.py          # Monitor de recursos (CPU/RAM)
│   └── README.md           # Documentação dos utilitários
└── venv/                   # Ambiente Virtual
```

-----

### Requisitos de Instalação e Execução

Para rodar a aplicação, é necessário ter Python, Redis e as dependências do projeto instaladas.

1.  **Instalar Python 3.x**.
2.  **Instalar o Redis:** A forma mais simples é utilizando Docker:
    ```bash
    docker run -d -p 6379:6379 redis
    ```
    Ou use o docker-compose (recomendado):
    ```bash
    docker-compose up -d redis
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

-----

### 🚀 Como Executar

#### **Opção 1: Inicialização Automática (Recomendado)**

Ideal para desenvolvimento. Um comando inicia tudo automaticamente:

**Passo 1:** Inicie o Redis
```bash
docker-compose up -d redis
```

**Passo 2:** Inicie o Growchats completo
```bash
# Com o venv ativado
python start.py
```

**Passo 3:** Acesse a aplicação
```
🌐 http://127.0.0.1:5000
```

**Para parar:** Pressione `Ctrl+C` no terminal do `start.py` (todos os serviços param automaticamente)

**Vantagens:**
- ✅ Um único comando
- ✅ Logs unificados
- ✅ Parar tudo com um Ctrl+C
- ✅ Verifica automaticamente se Redis está rodando

---

#### **Opção 2: Modo Manual (Controle Total)**

Para usuários avançados que preferem gerenciar cada processo separadamente:

**Terminal 1 - Redis:**
```bash
docker-compose up -d redis
```

**Terminal 2 - Celery Worker:**
```bash
# Com o venv ativado
celery -A tasks.celery_app worker --loglevel=info -P gevent
```

**Terminal 3 - Flask Server:**
```bash
# Com o venv ativado
python app.py
```

**Acesse:** `http://127.0.0.1:5000`

**Vantagens:**
- ✅ Controle granular de cada componente
- ✅ Logs separados por serviço
- ✅ Útil para debugging avançado

-----

### 🛠️ Utilitários Opcionais

Na pasta `utils/` você encontra ferramentas extras:

#### **Monitor de Recursos**

Monitora em tempo real o uso de CPU/RAM dos processos do Growchats:

```bash
# Instalar dependência (apenas primeira vez)
pip install psutil

# Executar monitor
python utils/monitor.py
```

**Quando usar:**
- Desenvolvimento em máquinas com pouca RAM
- Identificar gargalos de performance
- Debugar problemas de lentidão

Veja mais detalhes em [`utils/README.md`](utils/README.md)

-----

### Plano de Desenvolvimento (Próximos Passos)

Com a arquitetura assíncrona implementada, o projeto está robusto e escalável. Os próximos passos focam em agregar mais valor ao usuário.

1.  **Prioridade 1: Suporte a PDF**: Implementar a conversão do Markdown extraído para o formato PDF, oferecendo um formato de arquivo mais profissional.
2.  **Prioridade 2: Suporte Multi-IA**: Adaptar o `extractor.py` para reconhecer e extrair conversas de outras plataformas (Gemini, Claude).

-----

### 🐛 Solução de Problemas

#### Redis não está rodando
```
❌ Redis não está rodando!

Solução:
docker-compose up -d redis
```

#### Ambiente virtual não ativado
```
⚠️ AVISO: Você não está no ambiente virtual!

Solução (Windows):
.\venv\Scripts\activate
```

#### Erro ao instalar dependências
```bash
# Atualize o pip primeiro
python -m pip install --upgrade pip

# Reinstale as dependências
pip install -r requirements.txt
```

#### Playwright não encontra navegador
```bash
# Reinstale os navegadores
playwright install chromium
```

-----

### 📊 Comparativo: Métodos de Execução

| Aspecto | Manual (3 terminais) | Automático (start.py) |
|---------|---------------------|------------------------|
| Comandos | 3 | 1 |
| Terminais | 3 | 1 |
| Tempo setup | 2-3 min | 30 seg |
| Parar tudo | Ctrl+C em 3 lugares | Ctrl+C uma vez |
| Logs | Separados | Unificados |
| Recomendado para | Debugging avançado | Desenvolvimento diário |

-----

### 🤝 Contribuindo

Contribuições são bem-vindas! Se você criar ferramentas úteis:

1. Adicione em `utils/` se for opcional
2. Documente no `utils/README.md`
3. Atualize este README se for essencial

-----

### 📝 Licença

Este projeto é de código aberto. Consulte o arquivo LICENSE para mais detalhes.

-----

### ✨ Novidades da Versão Atual

**v1.1.0 - Otimizações e Usabilidade**

- ✅ Inicializador unificado (`start.py`)
- ✅ Docker Compose para Redis
- ✅ Otimizações de memória para máquinas com desempenho reduzido
- ✅ Monitor de recursos em tempo real
- ✅ Logs unificados e coloridos
- ✅ Verificações automáticas de dependências