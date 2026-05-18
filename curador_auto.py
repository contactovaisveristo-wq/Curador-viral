import subprocess
import json
import os
from datetime import datetime

# --- Configurações ---
TOP_VIDEOS = 3          # Quantos vídeos processar
INICIO_CORTE = "00:00:05"  # Salta os primeiros 5s (evita intros)
DURACAO_CORTE = "00:00:50" # 50 segundos de conteúdo


def carregar_tendencias():
    """Lê o ficheiro de tendências de hoje."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    ficheiro = f"tendencias_{hoje}.json"

    if not os.path.exists(ficheiro):
        print(f"❌ Ficheiro {ficheiro} não encontrado. Corre primeiro o curador_viral.py")
        exit(1)

    with open(ficheiro, "r", encoding="utf-8") as f:
        videos = json.load(f)

    print(f"✅ {len(videos)} vídeos carregados de {ficheiro}")
    return videos[:TOP_VIDEOS]  # Devolve só o top N


def criar_pasta_saida():
    """Cria uma pasta com a data de hoje para guardar os shorts."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    pasta = f"shorts_{hoje}"
    os.makedirs(pasta, exist_ok=True)
    return pasta


def descarregar_video(url, ficheiro_saida):
    """Descarrega o vídeo do YouTube."""
    print(f"  ⬇️  A descarregar...")
    subprocess.run([
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "--merge-output-format", "mp4",
        "-o", ficheiro_saida,
        url
    ], check=True, capture_output=True)


def cortar_para_short(video_entrada, video_saida):
    """Corta e converte para formato vertical 9:16."""
    print(f"  ✂️  A cortar para Short...")
    subprocess.run([
        "ffmpeg",
        "-ss", INICIO_CORTE,
        "-i", video_entrada,
        "-t", DURACAO_CORTE,
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",  # Formato vertical
        "-c:v", "libx264",
        "-c:a", "aac",
        "-y",
        video_saida
    ], check=True, capture_output=True)


def processar_videos(videos, pasta_saida):
    """Processa cada vídeo: descarrega, corta e guarda."""
    resultados = []

    for i, video in enumerate(videos, 1):
        titulo = video["titulo"][:50]  # Limita o título a 50 chars
        url = video["url"]
        views = video["views"]

        print(f"\n🎬 [{i}/{len(videos)}] {titulo}")
        print(f"  👁️  Views: {views}")

        # Nomes dos ficheiros temporário e final
        temp = f"temp_video_{i}.mp4"
        saida = os.path.join(pasta_saida, f"short_{i:02d}.mp4")

        try:
            descarregar_video(url, temp)
            cortar_para_short(temp, saida)

            # Apaga o ficheiro temporário para poupar espaço
            os.remove(temp)

            print(f"  ✅ Guardado em: {saida}")
            resultados.append({"titulo": titulo, "url": url, "short": saida, "status": "ok"})

        except subprocess.CalledProcessError as e:
            print(f"  ❌ Erro neste vídeo, a saltar...")
            resultados.append({"titulo": titulo, "url": url, "status": "erro"})

    return resultados


def mostrar_resumo(resultados, pasta_saida):
    """Mostra o resumo no final."""
    ok = [r for r in resultados if r["status"] == "ok"]
    erros = [r for r in resultados if r["status"] == "erro"]

    print(f"\n{'='*50}")
    print(f"✅ {len(ok)} shorts criados em: {pasta_saida}/")
    if erros:
        print(f"⚠️  {len(erros)} vídeos com erro (podem ter restrições de download)")
    print(f"{'='*50}")


# --- Programa principal ---
if __name__ == "__main__":
    print("🚀 Curador Viral — Modo Automático")
    print("="*50)

    videos = carregar_tendencias()
    pasta_saida = criar_pasta_saida()

    print(f"\n📁 A criar shorts em: {pasta_saida}/")
    print(f"🎯 A processar top {TOP_VIDEOS} vídeos...\n")

    resultados = processar_videos(videos, pasta_saida)
    mostrar_resumo(resultados, pasta_saida)
