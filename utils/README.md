# 🛠️ Utilitários do Growchats

Esta pasta contém ferramentas opcionais para facilitar o desenvolvimento e monitoramento do Growchats.

---

## 📊 monitor.py

Monitor em tempo real do uso de recursos (CPU/RAM) dos processos do Growchats.

### Instalação

```bash
pip install psutil
```

### Uso

```bash
# Na raiz do projeto
python utils/monitor.py
```

### O que mostra

- **CPU Total do Sistema:** Percentual de uso geral
- **RAM Total:** Memória utilizada vs disponível
- **Processos Individuais:**
  - Flask (servidor web)
  - Celery (processador de tarefas)
  - Redis (banco de dados em memória)
- **Alertas:** Avisa quando a RAM está crítica (>85%)

### Quando usar

- Durante desenvolvimento em máquinas com pouca RAM (4GB)
- Para identificar vazamentos de memória
- Para otimizar performance
- Para debugar problemas de lentidão

### Exemplo de Saída

```
==============================================================
⏰ 14:32:15
==============================================================

💻 SISTEMA:
  CPU Total: 23.5%
  RAM: 2.8 GB / 3.8 GB (73.7%)

🚀 PROCESSOS GROWCHATS:
  Flask    - RAM:     45.2 MB | CPU:   2.1%
  Celery   - RAM:    128.5 MB | CPU:   8.4%
  Redis    - RAM:     12.8 MB | CPU:   0.3%

  TOTAL GROWCHATS: 186.5 MB

📊 STATUS:
  ⚡ ATENÇÃO: RAM em 73.7% - Monitorar uso

==============================================================
Atualizando em 3 segundos... (Ctrl+C para sair)
```

---

## 🔮 Futuras Ferramentas

Esta pasta será expandida com mais utilitários conforme o projeto evolui:

- **backup.py** - Script de backup automático do banco de dados
- **test_extractor.py** - Testes automatizados do extractor
- **cleanup.py** - Limpeza de arquivos temporários
- **benchmark.py** - Testes de performance

---

## 📝 Contribuindo

Se você criar uma ferramenta útil para o Growchats, adicione-a aqui e documente seu uso neste README.