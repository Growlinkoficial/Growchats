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
    """Verifica se o Docker está rodando e inicia automaticamente se necessário"""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def start_docker_desktop():
    """Inicia o Docker Desktop em segundo plano (multiplataforma)"""
    print_colored("🐳 Docker não está rodando. Iniciando automaticamente...", Colors.WARNING)
    
    import platform
    system = platform.system()
    
    try:
        if system == "Windows":
            # Tenta múltiplos paths comuns no Windows
            docker_paths = [
                "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe",
                "C:\\Program Files (x86)\\Docker\\Docker\\Docker Desktop.exe",
                os.path.expanduser("~\\AppData\\Local\\Docker\\Docker Desktop.exe"),
            ]
            
            # Método 1: Tenta pelos paths conhecidos
            docker_started = False
            for docker_path in docker_paths:
                if os.path.exists(docker_path):
                    print_colored(f"   Encontrado em: {docker_path}", Colors.OKCYAN)
                    subprocess.Popen(
                        [docker_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    docker_started = True
                    break
            
            # Método 2: Se não encontrou, tenta via comando do sistema
            if not docker_started:
                print_colored("   Tentando iniciar via registro do Windows...", Colors.OKCYAN)
                subprocess.Popen(
                    ["powershell", "-Command", "Start-Process 'Docker Desktop'"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        
        elif system == "Darwin":  # macOS
            # macOS: Inicia via comando open
            subprocess.Popen(
                ["open", "-a", "Docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        elif system == "Linux":
            # Linux: Tenta iniciar o serviço systemd
            subprocess.Popen(
                ["sudo", "systemctl", "start", "docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print_colored("⏳ Aguardando Docker inicializar (pode levar 30-60s)...", Colors.OKBLUE)
        
        # Aguarda até 90 segundos para o Docker ficar pronto
        for i in range(90):
            time.sleep(1)
            if check_docker_running():
                print_colored(f"✅ Docker iniciado com sucesso! ({i+1}s)", Colors.OKGREEN)
                return True
            
            # Feedback visual a cada 10 segundos
            if (i + 1) % 10 == 0:
                print_colored(f"   Ainda aguardando... ({i+1}s)", Colors.OKCYAN)
        
        print_colored("❌ Timeout: Docker não iniciou em 90 segundos", Colors.FAIL)
        return False
        
    except Exception as e:
        print_colored(f"❌ Erro ao iniciar Docker: {e}", Colors.FAIL)
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
        # Tenta iniciar o Docker automaticamente
        if not start_docker_desktop():
            print_colored("\n❌ Não foi possível iniciar o Docker!", Colors.FAIL)
            print_colored("Inicie o Docker Desktop manualmente e tente novamente", Colors.FAIL)
            sys.exit(1)
    else:
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
        print_colored("\n💡 Pressione Ctrl+C para parar TUDO (Redis + Docker)\n", Colors.WARNING)
        
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
        print_colored("\n\n🛑 Encerrando TUDO (Redis + Docker + Aplicação)...", Colors.WARNING)
        
        # 1. Encerra aplicação
        for name, proc in processes:
            print_colored(f"  Parando {name}...", Colors.OKBLUE)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        
        # 2. Para Redis
        print_colored("🛑 Parando Redis...", Colors.OKBLUE)
        try:
            subprocess.run(["docker-compose", "down"], timeout=10)
            print_colored("✅ Redis parado", Colors.OKGREEN)
        except:
            print_colored("⚠️  Erro ao parar Redis", Colors.WARNING)
        
        # 3. Para Docker Desktop
        print_colored("🐳 Encerrando Docker Desktop...", Colors.OKBLUE)
        try:
            subprocess.run(
                ["powershell", "-Command", "Stop-Process -Name 'Docker Desktop' -Force -ErrorAction SilentlyContinue"],
                timeout=5
            )
            time.sleep(1)
            print_colored("✅ Docker Desktop encerrado", Colors.OKGREEN)
        except:
            print_colored("⚠️  Docker Desktop já estava fechado", Colors.WARNING)
        
        print_colored("\n✅ Tudo encerrado (Redis + Docker + Aplicação)", Colors.OKGREEN)
        print_colored("💡 Sistema liberado, zero impacto na máquina!", Colors.OKCYAN)
        sys.exit(0)

if __name__ == "__main__":
    main()