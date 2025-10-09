# Growchats

### Visão Geral do Produto

O **Growchats** é uma ferramenta de utilidade web projetada para resolver o problema de arquivamento e *backup* de conversas importantes geradas em plataformas de inteligência artificial (IAs) como ChatGPT.

-   **Propósito:** Permitir que usuários armazenem suas próprias conversas localmente, fora do ecossistema das plataformas de IA, para fins de documentação e referência offline.
-   **Mecanismo:** O usuário fornece o link de compartilhamento da conversa, e a ferramenta executa a extração do conteúdo em segundo plano, notificando o usuário quando o download está pronto.
-   **Categoria:** Aplicativo Web (Web App) de Produtividade/Utilidade.

-----

### 🔒 Segurança

Esta versão inclui melhorias importantes de segurança:

- ✅ Rate limiting (proteção contra abuso)
- ✅ Validação rigorosa de URLs
- ✅ Headers de segurança HTTP
- ✅ Variáveis de ambiente para credenciais
- ✅ Sanitização de inputs
- ✅ Logging de erros (sem expor dados sensíveis)
- ✅ Retry logic para falhas transitórias
- ✅ Timeouts configurados para prevenir travamentos

-----

### Arquitetura e Especificações Técnicas

O projeto utiliza uma arquitetura assíncrona para proporcionar uma experiência de usuário superior, eliminando a necessidade de esperar pelo processamento da extração em tempo real.

| Requisito | Detalhe | Status |
| :--- | :--- | :--- |
| **Arquitetura** | **Backend Assíncrono** com Flask, Celery e Redis. | **✅ CONCLUÍDO** |
| **Plataforma Prioritária** | **ChatGPT** (Links compartilhados). | **✅ CONCLUÍDO** |
| **Formato de Saída** | **Markdown (.md)**. | **✅ CONCLUÍDO** |
| **Experiência do Usuário** | Feedback instantâneo com barra de progresso e cronômetro. | **✅ CONCLUÍDO** |
| **Estabilidade** | Timeouts do Playwright ajustados para 90s. | **✅ IMPLEMENTADO** |
| **Segurança** | Rate limiting, validação de URLs, headers seguros. | **✅ IMPLEMENTADO** |

-----

### Estrutura do Projeto

```
/growchats
├── app.py                  # Servidor Flask (gerencia tarefas e status)
├── tasks.py                # Define a tarefa Celery que executa a extração
├── extractor.py            # Lógica de extração com Playwright
├── templates/
│   └── index.html          # Interface do Usuário (HTML/JS/CSS)
├── requirements.txt        # Lista de dependências do projeto
├── .env.example            # Exemplo de variáveis de ambiente
├── .env                    # Suas configurações (NÃO COMMITAR!)
├── .gitignore              # Arquivos a ignorar no Git
├── readme.md               # Este arquivo
└── venv/                   # Ambiente Virtual
```

-----

### Requisitos de Instalação e Execução

Para rodar a aplicação, é necessário ter Python, Redis e as dependências do projeto instaladas.

#### 1. Instalar Python 3.x
Versão 3.8 ou superior recomendada.

#### 2. Instalar o Redis
A forma mais simples é utilizando Docker:
```bash
docker run -d -p 6379:6379 redis
```

Ou instale localmente:
- **Windows:** [Download Redis](https://redis.io/download)
- **Linux:** `sudo apt-get install redis-server`
- **Mac:** `brew install redis`

#### 3. Criar e Ativar o Ambiente Virtual

**No Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**No Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. Instalar as Dependências do Projeto
```bash
pip install -r requirements.txt
```

#### 5. Instalar os Drivers do Navegador (Playwright)
```bash
playwright install
```

**No Linux, pode ser necessário instalar dependências adicionais:**
```bash
playwright install-deps
```

#### 6. Configurar Variáveis de Ambiente

**Copiar o arquivo de exemplo:**
```bash
# No Windows
copy .env.example .env

# No Linux/Mac
cp .env.example .env
```

**Editar o arquivo .env e configurar:**

```bash
# Configurações do Redis
REDIS_URL=redis://localhost:6379/0

# Configurações do Flask
FLASK_ENV=development
SECRET_KEY=GERE_UMA_CHAVE_SEGURA_AQUI

# Rate Limiting
MAX_EXTRACTIONS_PER_HOUR=10
```

**Para gerar uma SECRET_KEY segura, execute em Python:**
```python
import secrets
print(secrets.token_hex(32))
```

Copie o resultado e cole no arquivo `.env` substituindo `GERE_UMA_CHAVE_SEGURA_AQUI`.

-----

### Como Executar

A aplicação requer **três processos** rodando simultaneamente em **três terminais separados**:

#### Terminal 1: Iniciar o Redis

**Se estiver usando Docker:**
```bash
docker start <container_id_do_redis>
```

**Se instalou localmente:**
```bash
redis-server
```

#### Terminal 2: Iniciar o Worker do Celery

Este processo é o "trabalhador" que executa as extrações em segundo plano.

```bash
# Certifique-se de que o venv está ativado
celery -A tasks.celery_app worker --loglevel=info -P gevent
```

**Você verá algo como:**
```
[2025-01-10 14:30:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-01-10 14:30:00,001: INFO/MainProcess] celery@hostname ready.
```

#### Terminal 3: Iniciar o Servidor Flask

Este processo serve a interface web para o usuário.

```bash
# Certifique-se de que o venv está ativado
python app.py
```

**Você verá algo como:**
```
Servidor Flask iniciando em modo: development
Debug: True
Acesse http://127.0.0.1:5000/
```

#### 4. Acessar a Aplicação

Abra seu navegador e acesse: **http://127.0.0.1:5000/**

-----

### 🚀 Deploy em Produção

**ATENÇÃO:** Antes de fazer deploy em produção, certifique-se de:

#### Checklist de Segurança Obrigatório

- [ ] Configurar `FLASK_ENV=production` no arquivo `.env`
- [ ] Gerar e configurar uma `SECRET_KEY` forte e única (64 caracteres)
- [ ] Configurar Redis com senha: `REDIS_URL=redis://:senha_forte@host:6379/0`
- [ ] Usar HTTPS obrigatoriamente (Let's Encrypt gratuito)
- [ ] Configurar firewall para proteger Redis (apenas localhost ou VPC)
- [ ] Limitar acesso ao Redis apenas para IPs confiáveis
- [ ] Configurar backup automático do Redis
- [ ] Monitorar logs de erro e rate limiting
- [ ] Desativar modo debug: `app.run(debug=False)`
- [ ] Usar servidor WSGI em produção (Gunicorn ou uWSGI)

#### Exemplo de Configuração para Produção

**Arquivo .env (produção):**
```bash
REDIS_URL=redis://:SuaSenhaForte123!@localhost:6379/0
FLASK_ENV=production
SECRET_KEY=a1b2c3d4e5f6...64_caracteres_aleatorios
MAX_EXTRACTIONS_PER_HOUR=50
```

**Iniciar com Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Recomendações de Hospedagem

| Plataforma | Melhor Para | Custo Estimado |
|------------|-------------|----------------|
| **Railway** | Deploy rápido e simples | $5-20/mês |
| **Render** | Deploy gratuito inicial | $0-25/mês |
| **DigitalOcean** | Mais controle e flexibilidade | $12-50/mês |
| **AWS EC2** | Escalabilidade empresarial | $20-100/mês |
| **Heroku** | Simplicidade máxima | $7-25/mês |

**Para Redis gerenciado:**
- **Redis Cloud** (gratuito até 30MB)
- **AWS ElastiCache**
- **Upstash** (serverless Redis)

-----

### 🛡️ Limites de Rate Limiting

Para proteger contra abuso, a aplicação implementa os seguintes limites por endereço IP:

| Endpoint | Limite |
|----------|--------|
| **Geral** | 200 requisições/dia, 50/hora |
| **Extração (`/api/start-extraction`)** | 5 extrações por minuto |
| **Status (`/api/status/<task_id>`)** | 30 verificações por minuto |
| **Download (`/api/download/<task_id>`)** | 10 downloads por minuto |

**Se você atingir esses limites:**
- Aguarde alguns minutos antes de tentar novamente
- Em desenvolvimento, você pode ajustar os limites em `app.py`

-----

### 🐛 Troubleshooting

#### Erro "Task ID inválido"
**Causa:** Redis não está rodando ou Celery worker não está ativo.

**Solução:**
```bash
# Verificar se Redis está rodando
docker ps  # ou redis-cli ping

# Verificar se Celery worker está rodando
# Você deve ver o processo no Terminal 2
```

#### Erro "Rate limit exceeded"
**Causa:** Você excedeu o número máximo de requisições permitidas.

**Solução:**
- Aguarde alguns minutos e tente novamente
- Verifique se não há scripts fazendo requisições em loop

#### Erro de conexão com Redis
**Causa:** Redis não está acessível ou URL está incorreta.

**Solução:**
```bash
# Verificar se Redis está rodando
docker ps

# Testar conexão
redis-cli ping
# Deve retornar: PONG

# Verificar a variável REDIS_URL no .env
cat .env | grep REDIS_URL
```

#### Playwright não encontra o navegador
**Causa:** Drivers do navegador não foram instalados.

**Solução:**
```bash
# Reinstalar navegadores
playwright install

# No Linux, instalar dependências do sistema
playwright install-deps
```

#### Erro "ModuleNotFoundError: No module named 'flask_limiter'"
**Causa:** Dependência não instalada.

**Solução:**
```bash
pip install Flask-Limiter==3.5.0
# ou
pip install -r requirements.txt
```

#### Celery worker não inicia (Windows)
**Causa:** Celery tem problemas com Windows em algumas versões.

**Solução:**
```bash
# Use eventlet ao invés de gevent
pip install eventlet
celery -A tasks.celery_app worker --loglevel=info -P eventlet
```

#### Extração falha com timeout
**Causa:** Conversa muito longa ou ChatGPT está lento.

**Solução:**
- Tente novamente (o sistema faz 2 tentativas automáticas)
- Verifique se a URL está correta
- Aumente os timeouts em `extractor.py` se necessário

-----

### 📊 Plano de Desenvolvimento (Próximos Passos)

Com a arquitetura assíncrona e segurança implementadas, os próximos passos são:

#### Fase 1: Melhorias de Funcionalidade
1. **Suporte a PDF**: Converter Markdown para PDF profissional
2. **Suporte Multi-IA**: Adaptar para Gemini, Claude, Perplexity
3. **Histórico de Extrações**: Salvar URLs extraídas localmente

#### Fase 2: Sistema de Contas
4. **Autenticação**: Sistema de login/cadastro
5. **Dashboard**: Gerenciar conversas extraídas
6. **Cloud Storage**: Salvar conversas na nuvem

#### Fase 3: Features Avançadas
7. **Busca**: Pesquisar dentro das conversas arquivadas
8. **Tags**: Organizar conversas por categorias
9. **Compartilhamento**: Gerar links para compartilhar conversas
10. **API Pública**: Permitir integrações externas

-----

### 📝 Contribuindo

Pull requests são bem-vindos! Para mudanças importantes:

1. Abra uma issue primeiro para discutir a mudança proposta
2. Siga as boas práticas de segurança (nunca commite credenciais)
3. Adicione testes quando aplicável
4. Atualize a documentação conforme necessário
5. Siga o padrão de código existente (PEP 8 para Python)

#### Como Contribuir

```bash
# 1. Fork o repositório
# 2. Clone seu fork
git clone https://github.com/seu-usuario/growchats.git

# 3. Crie uma branch para sua feature
git checkout -b feature/minha-feature

# 4. Faça suas mudanças e commit
git commit -m "feat: adiciona suporte a PDF"

# 5. Push para seu fork
git push origin feature/minha-feature

# 6. Abra um Pull Request
```

### 🔗 Links Úteis

#### Documentação das Tecnologias
- [Documentação do Flask](https://flask.palletsprojects.com/)
- [Documentação do Celery](https://docs.celeryproject.org/)
- [Documentação do Playwright](https://playwright.dev/python/)
- [Documentação do Redis](https://redis.io/documentation)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)

#### Tutoriais Relacionados
- [Deploy Flask no Railway](https://docs.railway.app/deploy/deployments)
- [Celery + Redis Tutorial](https://docs.celeryproject.org/en/stable/getting-started/first-steps-with-celery.html)
- [Web Scraping com Playwright](https://playwright.dev/python/docs/intro)

-----

### ⚠️ Avisos Legais

- **Uso Pessoal:** Esta ferramenta é destinada para uso pessoal e arquivamento de suas próprias conversas
- **Termos de Serviço:** Respeite os termos de serviço das plataformas de IA (ChatGPT, etc)
- **Direitos Autorais:** Não use para scraping em massa ou violação de direitos autorais
- **Responsabilidade:** O desenvolvedor não se responsabiliza pelo uso indevido da ferramenta
- **Privacidade:** Suas conversas permanecem privadas e não são armazenadas em nossos servidores

#### Uso Ético

✅ **Permitido:**
- Arquivar suas próprias conversas
- Fazer backup de conteúdo gerado por você
- Documentar projetos pessoais
- Compartilhar conhecimento (respeitando direitos autorais)

❌ **Não Permitido:**
- Scraping automatizado em massa
- Violar termos de serviço das plataformas
- Redistribuir conteúdo protegido por direitos autorais
- Usar para spam ou atividades maliciosas

-----

### 📧 Suporte e Contato

#### Reportar Bugs
Para reportar bugs ou problemas técnicos, [abra uma issue](https://github.com/seu-usuario/growchats/issues) no GitHub com:
- Descrição detalhada do problema
- Passos para reproduzir
- Mensagens de erro (se houver)
- Versão do Python e sistema operacional

#### Sugerir Melhorias
Para sugerir novas funcionalidades, [abra uma issue](https://github.com/seu-usuario/growchats/issues) com a tag `enhancement` e descreva:
- Qual problema a feature resolve
- Como você imagina que funcionaria
- Exemplos de uso


### 🙏 Agradecimentos

Este projeto utiliza tecnologias incríveis desenvolvidas pela comunidade open-source:

- **Flask** - Framework web minimalista e poderoso
- **Celery** - Sistema de filas de tarefas distribuído
- **Playwright** - Automação de navegadores de última geração
- **Redis** - Banco de dados in-memory ultrarrápido

Agradecimentos especiais a todos os contribuidores e usuários que ajudam a melhorar o Growchats!