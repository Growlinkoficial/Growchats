#!/usr/bin/env python3
"""
Growchats - Inicializador Completo
Inicia Docker + Redis + Celery + Flask
Para tudo junto com Ctrl+C
"""
import subprocess
import sys
import time
import os

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(msg, color):
    print(f"{color}{msg}{Colors.ENDC}")

def check_docker_running():
    """Verifica se o Docker está rodando"""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def check_redis_container():
    """Verifica se o container Redis existe"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=growchats_redis", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "growchats_redis" in result.stdout
    except:
        return False

def start_redis():
    """Inicia o Redis usando docker-compose"""
    print_colored("🐳 Iniciando Docker Redis...", Colors.OKBLUE)
    try:
        subprocess.run(
            ["docker-compose", "up", "-d", "redis"],
            check=True,
            timeout=30
        )
        time.sleep(2)  # Aguarda Redis inicializar
        print_colored("✅ Redis iniciado", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored("❌ Falha ao iniciar Redis", Colors.FAIL)
        return False
    except FileNotFoundError:
        print_colored("❌ docker-compose não encontrado!", Colors.FAIL)
        print_colored("Instale com: pip install docker-compose", Colors.WARNING)
        return False

def stop_redis_and_docker():
    """Para o Redis e o Docker Desktop"""
    print_colored("🛑 Parando Redis...", Colors.OKBLUE)
    try:
        subprocess.run(
            ["docker-compose", "down"],
            timeout=10
        )
        print_colored("✅ Redis parado", Colors.OKGREEN)
    except:
        print_colored("⚠️  Erro ao parar Redis (pode já estar parado)", Colors.WARNING)
    
    # Para o Docker Desktop (Windows)
    print_colored("🐳 Encerrando Docker Desktop...", Colors.OKBLUE)
    try:
        # Windows: Fecha o Docker Desktop
        subprocess.run(
            ["powershell", "-Command", "Stop-Process -Name 'Docker Desktop' -Force -ErrorAction SilentlyContinue"],
            timeout=5
        )
        time.sleep(1)
        print_colored("✅ Docker Desktop encerrado", Colors.OKGREEN)
    except:
        print_colored("⚠️  Docker Desktop já estava fechado ou erro ao fechar", Colors.WARNING)

def check_venv():
    """Verifica se está rodando no venv"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

def main():
    print_colored("\n🚀 Growchats - Inicializador Completo", Colors.HEADER)
    print_colored("=" * 50, Colors.HEADER)
    
    # Verificação 1: Ambiente virtual
    if not check_venv():
        print_colored("\n⚠️  AVISO: Você não está no ambiente virtual!", Colors.WARNING)
        print_colored("Execute primeiro: .\\venv\\Scripts\\activate", Colors.WARNING)
        sys.exit(1)
    
    print_colored("\n✅ Ambiente virtual ativo", Colors.OKGREEN)
    
    # Verificação 2: Docker
    if not check_docker_running():
        print_colored("\n❌ Docker não está rodando!", Colors.FAIL)
        print_colored("Inicie o Docker Desktop primeiro", Colors.FAIL)
        sys.exit(1)
    
    print_colored("✅ Docker rodando", Colors.OKGREEN)
    
    # Iniciar Redis
    if not start_redis():
        sys.exit(1)
    
    print_colored("\n📦 Iniciando aplicação...\n", Colors.OKCYAN)
    
    processes = []
    
    try:
        # 1. Iniciar Celery Worker
        print_colored("[1/2] Iniciando Celery Worker...", Colors.OKBLUE)
        celery_cmd = [
            sys.executable, "-m", "celery",
            "-A", "tasks.celery_app",
            "worker",
            "--loglevel=info",
            "-P", "gevent",
            "--concurrency=2"
        ]
        celery_process = subprocess.Popen(
            celery_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(('Celery', celery_process))
        time.sleep(3)
        
        # 2. Iniciar Flask
        print_colored("[2/2] Iniciando Flask Server...", Colors.OKBLUE)
        flask_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(('Flask', flask_process))
        time.sleep(2)
        
        print_colored("\n" + "=" * 50, Colors.OKGREEN)
        print_colored("✅ Growchats está rodando COMPLETO!", Colors.OKGREEN)
        print_colored("=" * 50, Colors.OKGREEN)
        print_colored("\n🌐 Acesse: http://127.0.0.1:5000", Colors.BOLD)
        print_colored("\n💡 Pressione Ctrl+C para parar TUDO (Redis incluído)\n", Colors.WARNING)
        
        # Monitora processos e exibe logs
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print_colored(f"\n❌ {name} parou inesperadamente!", Colors.FAIL)
                    raise KeyboardInterrupt
                
                # Exibe logs
                line = proc.stdout.readline()
                if line:
                    prefix = f"[{name}] "
                    print(f"{Colors.OKCYAN}{prefix}{Colors.ENDC}{line.strip()}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print_colored("\n\n🛑 Encerrando TUDO (Redis + Aplicação)...", Colors.WARNING)
        
        # 1. Encerra aplicação
        for name, proc in processes:
            print_colored(f"  Parando {name}...", Colors.OKBLUE)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        
        # 2. Encerra Redis
        stop_redis()
        
        print_colored("\n✅ Tudo encerrado (zero impacto no sistema)", Colors.OKGREEN)
        sys.exit(0)

if __name__ == "__main__":
    main()