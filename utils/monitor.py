#!/usr/bin/env python3
"""
Growchats - Monitor de Recursos
Exibe uso de CPU/RAM em tempo real dos processos do Growchats

Uso:
    python utils/monitor.py

Requisito:
    pip install psutil
"""
import psutil
import time
import os
import sys

def get_process_info(name):
    """Busca processo por nome e retorna informações"""
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            if name.lower() in proc.info['name'].lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def format_bytes(bytes_value):
    """Formata bytes para MB"""
    return f"{bytes_value / (1024 * 1024):.1f} MB"

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # Verifica se psutil está instalado
    try:
        import psutil
    except ImportError:
        print("❌ Biblioteca 'psutil' não encontrada!")
        print("\nInstale com: pip install psutil")
        sys.exit(1)
    
    print("🔍 Growchats - Monitor de Recursos")
    print("=" * 60)
    print("Monitorando processos... Pressione Ctrl+C para sair\n")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            print("=" * 60)
            print(f"⏰ {time.strftime('%H:%M:%S')}")
            print("=" * 60)
            
            # Informações do Sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            print(f"\n💻 SISTEMA:")
            print(f"  CPU Total: {cpu_percent}%")
            print(f"  RAM: {format_bytes(memory.used)} / {format_bytes(memory.total)} ({memory.percent}%)")
            
            # Processos do Growchats
            print(f"\n🚀 PROCESSOS GROWCHATS:")
            
            processes = {
                'Flask': 'python',
                'Celery': 'celery',
                'Redis': 'redis'
            }
            
            total_mem = 0
            found_any = False
            
            for name, search_term in processes.items():
                proc = get_process_info(search_term)
                if proc:
                    found_any = True
                    mem = proc.info['memory_info'].rss
                    total_mem += mem
                    cpu = proc.cpu_percent()
                    print(f"  {name:8} - RAM: {format_bytes(mem):>10} | CPU: {cpu:>5.1f}%")
                else:
                    print(f"  {name:8} - ❌ Não encontrado")
            
            if found_any:
                print(f"\n  TOTAL GROWCHATS: {format_bytes(total_mem)}")
            else:
                print(f"\n  ⚠️  Nenhum processo do Growchats detectado")
                print(f"  Certifique-se de que a aplicação está rodando")
            
            # Alertas de uso de memória
            print(f"\n📊 STATUS:")
            if memory.percent > 85:
                print(f"  ⚠️  CRÍTICO: RAM em {memory.percent}% - Feche outros programas!")
            elif memory.percent > 70:
                print(f"  ⚡ ATENÇÃO: RAM em {memory.percent}% - Monitorar uso")
            else:
                print(f"  ✅ Normal: RAM em {memory.percent}%")
            
            print("\n" + "=" * 60)
            print("Atualizando em 3 segundos... (Ctrl+C para sair)")
            time.sleep(3)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n✅ Monitor encerrado\n")

if __name__ == "__main__":
    main()