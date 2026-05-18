import re

FICHEIRO = "curador_viral.py"

def ler_temas_atuais():
    """Lê os temas que estão atualmente no ficheiro."""
    with open(FICHEIRO, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Encontra a lista de temas no ficheiro
    match = re.search(r'TEMAS = \[(.*?)\]', conteudo, re.DOTALL)
    if not match:
        print("❌ Não encontrei a lista de temas no ficheiro.")
        return []

    # Extrai os temas da lista
    temas = re.findall(r'"(.*?)"', match.group(1))
    return temas


def atualizar_temas(novos_temas):
    """Substitui os temas no ficheiro pelo novos."""
    with open(FICHEIRO, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Formata a nova lista de temas
    temas_formatados = ",\n    ".join([f'"{t}"' for t in novos_temas])
    nova_lista = f'TEMAS = [\n    {temas_formatados},\n]'

    # Substitui no ficheiro
    novo_conteudo = re.sub(r'TEMAS = \[.*?\]', nova_lista, conteudo, flags=re.DOTALL)

    with open(FICHEIRO, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)


def mostrar_temas(temas):
    """Mostra a lista de temas numerada."""
    print("\n📌 Temas atuais:")
    for i, tema in enumerate(temas, 1):
        print(f"  {i}. {tema}")


# --- Programa principal ---
if __name__ == "__main__":
    print("🎯 Gestor de Temas — Curador Viral")
    print("=" * 40)

    temas = ler_temas_atuais()
    mostrar_temas(temas)

    print("\nO que queres fazer?")
    print("  1. Adicionar tema")
    print("  2. Remover tema")
    print("  3. Substituir todos os temas")
    print("  4. Sair")

    opcao = input("\nEscolhe (1-4): ").strip()

    if opcao == "1":
        novo = input("Novo tema: ").strip()
        if novo:
            temas.append(novo)
            atualizar_temas(temas)
            print(f"✅ Tema '{novo}' adicionado!")
            mostrar_temas(temas)

    elif opcao == "2":
        mostrar_temas(temas)
        num = input("Número do tema a remover: ").strip()
        if num.isdigit() and 1 <= int(num) <= len(temas):
            removido = temas.pop(int(num) - 1)
            atualizar_temas(temas)
            print(f"✅ Tema '{removido}' removido!")
            mostrar_temas(temas)
        else:
            print("❌ Número inválido.")

    elif opcao == "3":
        print("Introduz os novos temas (linha vazia para terminar):")
        novos = []
        while True:
            tema = input("  Tema: ").strip()
            if not tema:
                break
            novos.append(tema)
        if novos:
            atualizar_temas(novos)
            print(f"✅ {len(novos)} temas guardados!")
            mostrar_temas(novos)
        else:
            print("❌ Nenhum tema introduzido.")

    elif opcao == "4":
        print("👋 Até logo!")

    else:
        print("❌ Opção inválida.")
