import subprocess
import sys

PYTHON = sys.executable  # Usa automaticamente o Python correto onde quer que corra

print("🚀 Curador Viral — Pipeline Completo")
print("=" * 50)

# Passo 1 — Pesquisa de tendências
print("\n📡 PASSO 1: A pesquisar tendências...")
if subprocess.run([PYTHON, "curador_viral.py"]).returncode != 0:
    print("❌ Erro na pesquisa. A parar.")
    sys.exit(1)

# Passo 2 — Corte automático
print("\n✂️  PASSO 2: A criar shorts...")
if subprocess.run([PYTHON, "curador_auto.py"]).returncode != 0:
    print("❌ Erro ao criar shorts. A parar.")
    sys.exit(1)

# Passo 3 — Publicar no YouTube
print("\n📺 PASSO 3: A publicar no YouTube...")
if subprocess.run([PYTHON, "publicar_youtube.py"]).returncode != 0:
    print("❌ Erro ao publicar. A parar.")
    sys.exit(1)

print("\n✅ Pipeline completo! Vai ao YouTube Studio rever os shorts.")
