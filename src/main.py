import csv
import os

# Diretório onde este script (.py) está salvo
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível (sai de src/) e entra em dados/
CAMINHO_PADRAO = os.path.join(DIR_SCRIPT, "..", "dados", "vendas.csv")


def ler_dados_vendas(caminho_arquivo=CAMINHO_PADRAO):
    """
    Lê o arquivo CSV de vendas e faz o tratamento inicial dos dados
    utilizando conjuntos (set) para identificar valores únicos.

    Parâmetros:
        caminho_arquivo (str): caminho para o arquivo .csv

    Retorna:
        dict com duas chaves:
            "registros": lista de dicionários, um por linha do CSV
            "conjuntos": dicionário com os sets de valores únicos
                         encontrados em cada coluna categórica
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    registros = []

    # Conjuntos para armazenar os valores únicos de cada categoria
    vendedores = set()
    produtos = set()
    categorias = set()
    formas_pagamento = set()

    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            # Pequeno tratamento: remove espaços em branco extras
            linha = {chave: valor.strip() for chave, valor in linha.items()}

            registros.append(linha)

            # Alimenta os conjuntos com os valores da linha atual
            vendedores.add(linha["vendedor"])
            produtos.add(linha["produto"])
            categorias.add(linha["categoria"])
            formas_pagamento.add(linha["pagamento"])

    conjuntos = {
        "vendedores": vendedores,
        "produtos": produtos,
        "categorias": categorias,
        "formas_pagamento": formas_pagamento,
    }

    return {"registros": registros, "conjuntos": conjuntos}


def remover_duplicados(registros):
    """
    Remove registros duplicados da base bruta utilizando set.

    Como dicionários não são "hashable" (não podem entrar diretamente
    em um set), cada registro é convertido para uma tupla de pares
    (chave, valor) antes de ser inserido no conjunto. Isso permite que
    o set identifique e descarte automaticamente as linhas repetidas.

    Parâmetros:
        registros (list[dict]): lista de registros lidos do CSV

    Retorna:
        list[dict]: lista de registros únicos, na ordem em que
                    apareceram pela primeira vez
    """
    vistos = set()
    registros_unicos = []

    for linha in registros:
        # tuple(sorted(...)) garante uma representação estável e
        # hashable do dicionário, independente da ordem das chaves
        chave_linha = tuple(sorted(linha.items()))

        if chave_linha not in vistos:
            vistos.add(chave_linha)
            registros_unicos.append(linha)

    return registros_unicos


def agrupar_produtos_por_vendedor(registros):
    """
    Monta um dicionário onde cada chave é um vendedor e o valor é o
    set de produtos distintos que esse vendedor vendeu.

    Parâmetros:
        registros (list[dict]): lista de registros (já sem duplicados)

    Retorna:
        dict[str, set[str]]: {vendedor: {produtos vendidos}}
    """
    produtos_por_vendedor = {}

    for linha in registros:
        vendedor = linha["vendedor"]
        produto = linha["produto"]

        if vendedor not in produtos_por_vendedor:
            produtos_por_vendedor[vendedor] = set()

        produtos_por_vendedor[vendedor].add(produto)

    return produtos_por_vendedor


def comparar_vendedores(produtos_por_vendedor, vendedor_a, vendedor_b):
    """
    Aplica as três operações clássicas de conjuntos entre os produtos
    vendidos por dois vendedores.

    Parâmetros:
        produtos_por_vendedor (dict[str, set[str]]): saída de
            agrupar_produtos_por_vendedor()
        vendedor_a, vendedor_b (str): nomes dos vendedores a comparar

    Retorna:
        dict com as chaves "uniao", "intersecao", "diferenca_a_b"
        e "diferenca_b_a"
    """
    set_a = produtos_por_vendedor[vendedor_a]
    set_b = produtos_por_vendedor[vendedor_b]

    return {
        # Todos os produtos vendidos por A ou por B (sem repetir)
        "uniao": set_a | set_b,
        # Produtos que os dois venderam em comum
        "intersecao": set_a & set_b,
        # Produtos que A vendeu mas B nunca vendeu
        "diferenca_a_b": set_a - set_b,
        # Produtos que B vendeu mas A nunca vendeu
        "diferenca_b_a": set_b - set_a,
    }


def exibir_comparacao(vendedor_a, vendedor_b, resultado):
    """Exibe de forma legível o resultado de comparar_vendedores()."""
    print(f"Comparando produtos vendidos por {vendedor_a} e {vendedor_b}\n")
    print(f"União (A | B) — todos os produtos vendidos por algum dos dois:")
    print(sorted(resultado["uniao"]))
    print()
    print(f"Interseção (A & B) — produtos que ambos venderam:")
    print(sorted(resultado["intersecao"]))
    print()
    print(f"Diferença (A - B) — produtos só de {vendedor_a}:")
    print(sorted(resultado["diferenca_a_b"]))
    print()
    print(f"Diferença (B - A) — produtos só de {vendedor_b}:")
    print(sorted(resultado["diferenca_b_a"]))
    print()


def exibir_resumo(dados):
    """Exibe um resumo simples dos conjuntos encontrados."""
    conjuntos = dados["conjuntos"]

    print(f"Total de registros lidos: {len(dados['registros'])}\n")

    for nome, conjunto in conjuntos.items():
        print(f"{nome} ({len(conjunto)} valores únicos):")
        print(sorted(conjunto))
        print()


if __name__ == "__main__":
    dados = ler_dados_vendas()

    registros_sem_duplicados = remover_duplicados(dados["registros"])
    qtd_duplicados = len(dados["registros"]) - len(registros_sem_duplicados)

    exibir_resumo(dados)
    print(f"Registros duplicados removidos: {qtd_duplicados}")
    print(f"Total após remoção: {len(registros_sem_duplicados)}\n")

    # Operações de conjuntos: comparando produtos entre dois vendedores
    produtos_por_vendedor = agrupar_produtos_por_vendedor(registros_sem_duplicados)
    resultado = comparar_vendedores(produtos_por_vendedor, "Beatriz", "Carlos")
    exibir_comparacao("Beatriz", "Carlos", resultado)