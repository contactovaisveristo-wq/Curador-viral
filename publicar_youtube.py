import os
import json
import glob
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Configurações ---
CLIENT_SECRETS = "client_secrets.json"
TOKEN_FILE = "token_youtube.json"  # Guarda a sessão para não pedir login sempre
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def autenticar():
    """Faz login no YouTube. Na primeira vez abre o browser."""
    creds = None

    # Se já temos um token guardado, usa-o
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Se não temos token ou expirou, pede login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)

        # Guarda o token para a próxima vez
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def buscar_shorts_hoje():
    """Encontra os shorts criados hoje."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    pasta = f"shorts_{hoje}"

    if not os.path.exists(pasta):
        print(f"❌ Pasta {pasta} não encontrada. Corre primeiro o curador_completo.py")
        exit(1)

    shorts = sorted(glob.glob(f"{pasta}/short_*.mp4"))

    if not shorts:
        print(f"❌ Nenhum short encontrado em {pasta}")
        exit(1)

    return shorts, hoje


def carregar_tendencias_hoje(hoje):
    """Lê os títulos dos vídeos originais para usar como referência."""
    ficheiro = f"tendencias_{hoje}.json"
    if os.path.exists(ficheiro):
        with open(ficheiro, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def publicar_short(youtube, ficheiro_video, titulo, descricao):
    """Faz upload de um short para o YouTube."""
    print(f"  📤 A publicar: {os.path.basename(ficheiro_video)}")

    body = {
        "snippet": {
            "title": titulo[:100],         # YouTube limita a 100 chars
            "description": descricao,
            "tags": ["shorts", "viral", "desporto", "motorsport", "karma"],
            "categoryId": "17",            # Categoria Desporto
        },
        "status": {
            "privacyStatus": "private",    # Começa como privado — muda para "public" quando quiseres
        }
    }

    media = MediaFileUpload(ficheiro_video, mimetype="video/mp4", resumable=True)

    resposta = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    ).execute()

    video_id = resposta["id"]
    print(f"  ✅ Publicado! https://youtube.com/watch?v={video_id}")
    return video_id


# --- Programa principal ---
if __name__ == "__main__":
    print("📺 A publicar Shorts no YouTube...")
    print("=" * 50)

    # Autentica
    youtube = autenticar()

    # Encontra os shorts de hoje
    shorts, hoje = buscar_shorts_hoje()
    tendencias = carregar_tendencias_hoje(hoje)

    print(f"🎬 {len(shorts)} shorts encontrados\n")

    for i, ficheiro in enumerate(shorts):
        # Usa o título da tendência ou um genérico
        if i < len(tendencias):
            tema = tendencias[i].get("tema", "viral")
            titulo_original = tendencias[i].get("titulo", "")
            titulo = f"#{tema.split()[0].capitalize()} viral 🔥 #shorts"
            descricao = f"Conteúdo inspirado em tendências virais de {tema}.\n\n#shorts #viral #desporto"
        else:
            titulo = f"Short viral #{i+1} 🔥 #shorts"
            descricao = "Conteúdo viral do dia! #shorts #viral"

        publicar_short(youtube, ficheiro, titulo, descricao)

    print(f"\n🎉 Todos os shorts publicados como PRIVADOS.")
    print("Vai ao YouTube Studio para os rever e tornar públicos.")
