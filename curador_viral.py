import os
import json
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# --- Configurações ---
PAIS = "PT"
MAXIMO_VIDEOS = 10  # Por pesquisa

# Define os temas que queres pesquisar
TEMAS = [
    "desporto viral",
    "motorsport crash highlights",
    "instant karma compilation",
    "Karen payback",
]


def buscar_videos_por_tema(youtube, tema):
    """Pesquisa vídeos virais por palavra-chave."""
    resposta = youtube.search().list(
        part="snippet",
        q=tema,
        type="video",
        order="viewCount",        # Ordena pelos mais vistos
        publishedAfter="2026-05-11T00:00:00Z",  # Última semana
        maxResults=MAXIMO_VIDEOS,
        regionCode=PAIS,
        relevanceLanguage="pt",
    ).execute()
    return resposta.get("items", [])


def buscar_estatisticas(youtube, video_ids):
    """Vai buscar as estatísticas dos vídeos (views, likes)."""
    resposta = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids)
    ).execute()
    return {v["id"]: v for v in resposta.get("items", [])}


def formatar_numero(n):
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def mostrar_e_guardar(todos_videos):
    hoje = datetime.now().strftime("%Y-%m-%d")
    resultados = []

    print(f"\n🔥 VÍDEOS VIRAIS POR TEMA — {hoje}")
    print("=" * 60)

    for tema, videos in todos_videos.items():
        print(f"\n📌 Tema: {tema.upper()}")
        print("-" * 40)

        for i, video in enumerate(videos, 1):
            snippet = video["snippet"]
            stats = video.get("statistics", {})
            video_id = video["id"]

            titulo = snippet["title"]
            canal = snippet["channelTitle"]
            views = formatar_numero(stats.get("viewCount", 0))
            likes = formatar_numero(stats.get("likeCount", 0))
            url = f"https://youtube.com/watch?v={video_id}"

            print(f"\n  #{i} {titulo}")
            print(f"     📺 Canal: {canal}")
            print(f"     👁️  Views: {views}  |  👍 Likes: {likes}")
            print(f"     🔗 {url}")

            resultados.append({
                "tema": tema,
                "posicao": i,
                "titulo": titulo,
                "canal": canal,
                "views": stats.get("viewCount", "0"),
                "likes": stats.get("likeCount", "0"),
                "url": url,
                "data": hoje,
            })

    # Guarda tudo num ficheiro JSON
    nome_ficheiro = f"tendencias_{hoje}.json"
    with open(nome_ficheiro, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Guardado em: {nome_ficheiro} ({len(resultados)} vídeos)")


# --- Programa principal ---
if __name__ == "__main__":
    print("🔍 A pesquisar vídeos virais por tema...")
    youtube = build("youtube", "v3", developerKey=API_KEY)

    todos_videos = {}

    for tema in TEMAS:
        print(f"  🔎 A pesquisar: {tema}")
        itens = buscar_videos_por_tema(youtube, tema)

        if not itens:
            continue

        # Vai buscar estatísticas detalhadas
        ids = [item["id"]["videoId"] for item in itens]
        stats = buscar_estatisticas(youtube, ids)

        # Junta tudo
        videos_completos = []
        for item in itens:
            vid_id = item["id"]["videoId"]
            if vid_id in stats:
                videos_completos.append(stats[vid_id])

        todos_videos[tema] = videos_completos

    mostrar_e_guardar(todos_videos)
