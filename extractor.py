# extractor.py - Versão Corrigida

import sys
# A linha abaixo foi corrigida para remover o espaço extra
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÕES DE EXTRAÇÃO ---
TARGET_PLATFORM_URL = "chatgpt.com"
TARGET_PLATFORM_NAME = "ChatGPT" 
MESSAGE_CONTAINER_SELECTOR = 'article[data-testid^="conversation-turn-"]' 
STABLE_WAIT_SELECTOR = '.flex.h-full.flex-col'

# --- TIMEOUTS AUMENTADOS PARA ESTABILIDADE ---
NAV_TIMEOUT = 90000  # 90 segundos para navegação inicial
STABLE_WAIT = 90000  # 90 segundos para a interface carregar
MESSAGE_WAIT = 90000 # 90 segundos para as mensagens aparecerem

# --- Função para bloquear requisições ---
def block_unnecessary_requests(route):
    """Intercepta e bloqueia requisições de rede desnecessárias."""
    if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
        route.abort()
    else:
        route.continue_()

def format_conversation_data(messages: list) -> str:
    """
    Formata uma lista de dicionários {emissor: str, conteudo: str} para Markdown.
    """
    markdown_output = f"# Conversa Arquivada - {TARGET_PLATFORM_NAME}\n\n"
    markdown_output += "---\n\n"
    
    for msg in messages:
        markdown_output += f"## {msg['emissor']}:\n"
        content = msg['conteudo'].strip()
        formatted_content = content.replace('\n', '\n> ')
        markdown_output += f"> {formatted_content}\n\n"
        
    return markdown_output

def extract_conversation(url: str):
    """
    Navega, extrai todos os turnos e retorna o conteúdo formatado em Markdown.
    Retorna (markdown_string) ou (error_message, http_status_code).
    """
    if TARGET_PLATFORM_URL not in url:
        return f"Erro: O link não parece ser de um chat compartilhado do {TARGET_PLATFORM_NAME}.", 400

    print(f"[EXTRACTOR] Iniciando extração do link: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--blink-settings=imagesEnabled=false'
            ]
        ) 
        page = browser.new_page()

        try:
            page.route("**/*", block_unnecessary_requests)

            print("[EXTRACTOR] Navegando...")
            page.goto(url, timeout=NAV_TIMEOUT)

            print("[EXTRACTOR] Aguardando carregamento estável...")
            page.wait_for_selector(STABLE_WAIT_SELECTOR, state="visible", timeout=STABLE_WAIT)
            page.wait_for_load_state("domcontentloaded")
            
            print("[EXTRACTOR] Forçando rolagem para renderizar...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            print("[EXTRACTOR] Tentando localizar turnos de conversa...")
            page.wait_for_selector(MESSAGE_CONTAINER_SELECTOR, state="visible", timeout=MESSAGE_WAIT)

            message_elements = page.locator(MESSAGE_CONTAINER_SELECTOR).all()
            conversation_data = []

            for element in message_elements:
                data_turn_attribute = element.get_attribute("data-turn")
                emissor = "Usuário" if data_turn_attribute == "user" else "Assistente"
                message_text = ""
                try:
                    message_text = element.locator('.whitespace-pre-wrap').inner_text()
                except:
                    try:
                        message_text = element.locator('.markdown.prose').inner_text()
                    except:
                         message_text = element.inner_text()
                
                if message_text and message_text.strip(): 
                    conversation_data.append({
                        "emissor": emissor,
                        "conteudo": message_text
                    })
            
            markdown_output = format_conversation_data(conversation_data)
            
            browser.close()
            return markdown_output 
            
        except Exception as e:
            error_message = f"Falha na extração ou Timeout ({MESSAGE_WAIT/1000}s excedidos). A página de origem pode estar lenta ou bloqueando o acesso. Tente novamente."
            print(f"[EXTRACTOR ERROR] {error_message} - Detalhe: {e}")
            browser.close()
            return error_message, 500