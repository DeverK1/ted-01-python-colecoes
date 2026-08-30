import csv
import os

import formatacao as fmt

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


def modelar_registros(registros):
    """
    Modela os dados brutos (strings) em uma LISTA de DICIONÁRIOS
    tratados, com os tipos corretos e um campo calculado (valor_total).

    Cada registro tratado é um dicionário no formato:
        {
            "id_venda": "V001",
            "vendedor": "Beatriz",
            "produto": "Notebook",
            "categoria": "Informática",
            "quantidade": 1,          # int
            "valor_unitario": 3500.0, # float
            "valor_total": 3500.0,    # float, calculado
            "data": "2026-06-25",
            "pagamento": "Pix",
        }

    Parâmetros:
        registros (list[dict]): registros brutos (já sem duplicados),
            como vêm de ler_dados_vendas() / remover_duplicados()

    Retorna:
        list[dict]: lista de registros tratados (a "coleção" principal)
    """
    registros_tratados = []

    for linha in registros:
        quantidade = int(linha["quantidade"])
        valor_unitario = float(linha["valor_unitario"])
        valor_total = quantidade * valor_unitario

        # DICIONÁRIO: objeto estruturado com chaves e valores nomeados
        registro_tratado = {
            "id_venda": linha["id_venda"],
            "vendedor": linha["vendedor"],
            "produto": linha["produto"],
            "categoria": linha["categoria"],
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "valor_total": valor_total,
            "data": linha["data"],
            "pagamento": linha["pagamento"],
        }

        # LISTA: guarda a sequência de registros tratados, na ordem
        registros_tratados.append(registro_tratado)

    return registros_tratados


def montar_tuplas_id_valor(registros_tratados):
    """
    Cria uma LISTA de TUPLAS (id_venda, valor_total).

    Tupla é usada aqui porque (id_venda, valor_total) é um par que não
    deve ser alterado depois de criado — é um "retrato" fixo da venda,
    diferente do dicionário completo, que ainda pode ser atualizado.

    Parâmetros:
        registros_tratados (list[dict]): saída de modelar_registros()

    Retorna:
        list[tuple]: [(id_venda, valor_total), ...]
    """
    return [
        (registro["id_venda"], registro["valor_total"])
        for registro in registros_tratados
    ]


def agrupar_por_categoria(registros_tratados):
    """
    Cria uma estrutura ANINHADA: um dicionário onde cada chave é uma
    categoria e o valor é a LISTA de DICIONÁRIOS (registros) daquela
    categoria. Ou seja: dict -> list -> dict.

    Parâmetros:
        registros_tratados (list[dict]): saída de modelar_registros()

    Retorna:
        dict[str, list[dict]]: {categoria: [registros da categoria]}
    """
    por_categoria = {}

    for registro in registros_tratados:
        categoria = registro["categoria"]
        por_categoria.setdefault(categoria, []).append(registro)

    return por_categoria


def filtrar_vendas_altas(registros_tratados, limite=1000.0):
    """
    LIST COMPREHENSION #1 — Filtragem.

    Seleciona apenas os registros cujo valor_total ultrapassa um
    limite, sem precisar de um loop explícito com if/append.

    Parâmetros:
        registros_tratados (list[dict]): saída de modelar_registros()
        limite (float): valor mínimo (exclusivo) para considerar
            a venda "de alto valor"

    Retorna:
        list[dict]: apenas os registros com valor_total > limite
    """
    return [venda for venda in registros_tratados if venda["valor_total"] > limite]


def gerar_descricoes_vendas(registros_tratados):
    """
    LIST COMPREHENSION #2 — Transformação.

    Transforma cada registro (dict) numa string de descrição legível,
    aplicando .strip().title() no nome do produto para padronizar a
    capitalização (ex: "notebook" ou "NOTEBOOK" viram "Notebook").

    Parâmetros:
        registros_tratados (list[dict]): saída de modelar_registros()

    Retorna:
        list[str]: uma descrição textual por venda
    """
    return [
        f"{venda['produto'].strip().title()} vendido por {venda['vendedor']} "
        f"em {venda['data']}"
        for venda in registros_tratados
    ]


def mapear_valor_por_venda(registros_tratados):
    """
    DICT COMPREHENSION — Agrupamento/transformação em dicionário.

    Mapeia cada id_venda (chave única) ao seu valor_total. Usei
    id_venda como chave em vez de vendedor de propósito: como um
    dicionário não pode ter chaves repetidas, um comprehension como
    {venda["vendedor"]: venda["valor_total"] for venda in registros}
    faria cada vendedor repetido SOBRESCREVER o valor anterior,
    sobrando só o valor da última venda dele. Como id_venda é único
    por linha, esse problema não acontece aqui.

    Parâmetros:
        registros_tratados (list[dict]): saída de modelar_registros()

    Retorna:
        dict[str, float]: {id_venda: valor_total}
    """
    return {venda["id_venda"]: venda["valor_total"] for venda in registros_tratados}


def exibir_comprehensions(vendas_altas, descricoes, mapa_valor_por_venda, limite):
    """Exibe o resultado das comprehensions aplicadas."""
    fmt.secao(f"List Comprehension — Filtragem (valor > {fmt.moeda(limite)})")
    fmt.item("Vendas encontradas", len(vendas_altas), destaque=True)
    larguras = [7, 10, 10, 13, 14]
    fmt.linha_tabela(
        ["ID", "Vendedor", "Produto", "Categoria", "Valor total"], larguras
    )
    for venda in vendas_altas[:5]:
        fmt.linha_tabela(
            [
                venda["id_venda"],
                venda["vendedor"],
                venda["produto"],
                venda["categoria"],
                fmt.moeda(venda["valor_total"]),
            ],
            larguras,
        )
    if len(vendas_altas) > 5:
        print(f"  ... e mais {len(vendas_altas) - 5} venda(s)")

    fmt.secao("List Comprehension — Transformação (descrição textual)")
    for descricao in descricoes[:5]:
        print(f"  - {descricao}")

    fmt.secao("Dict Comprehension — id_venda → valor_total")
    for id_venda, valor in list(mapa_valor_por_venda.items())[:5]:
        fmt.item(id_venda, fmt.moeda(valor))


def exibir_modelagem(registros_tratados, tuplas_id_valor, por_categoria):
    """Exibe uma amostra das estruturas montadas, para conferência."""
    fmt.secao("Amostra de registros tratados (list[dict])")
    larguras = [7, 10, 10, 13, 14]
    fmt.linha_tabela(
        ["ID", "Vendedor", "Produto", "Categoria", "Valor total"], larguras
    )
    for registro in registros_tratados[:3]:
        fmt.linha_tabela(
            [
                registro["id_venda"],
                registro["vendedor"],
                registro["produto"],
                registro["categoria"],
                fmt.moeda(registro["valor_total"]),
            ],
            larguras,
        )

    fmt.secao("Amostra de tuplas (id_venda, valor_total)")
    for id_venda, valor_total in tuplas_id_valor[:5]:
        print(f"  ({id_venda}, {fmt.moeda(valor_total)})")

    fmt.secao("Totais por categoria (dict[str, list[dict]])")
    larguras_cat = [15, 12, 16]
    fmt.linha_tabela(["Categoria", "Vendas", "Valor total"], larguras_cat)
    for categoria, itens in por_categoria.items():
        total_categoria = sum(item["valor_total"] for item in itens)
        fmt.linha_tabela(
            [categoria, len(itens), fmt.moeda(total_categoria)], larguras_cat
        )


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
    fmt.secao(f"Operações de conjunto: {vendedor_a} × {vendedor_b}")
    fmt.rotulo("União (A | B)")
    fmt.lista_valores(sorted(resultado["uniao"]))
    fmt.rotulo("Interseção (A & B)")
    fmt.lista_valores(sorted(resultado["intersecao"]))
    fmt.rotulo(f"Só {vendedor_a} (A - B)")
    fmt.lista_valores(sorted(resultado["diferenca_a_b"]))
    fmt.rotulo(f"Só {vendedor_b} (B - A)")
    fmt.lista_valores(sorted(resultado["diferenca_b_a"]))


def exibir_resumo(dados, qtd_duplicados, total_final):
    """Exibe o resumo da leitura e limpeza da base."""
    conjuntos = dados["conjuntos"]

    fmt.secao("Leitura e limpeza da base")
    fmt.item("Registros lidos", len(dados["registros"]))
    fmt.item("Duplicados removidos", qtd_duplicados)
    fmt.item("Total após remoção", total_final, destaque=True)

    fmt.secao("Valores únicos por coluna (set)")
    rotulos = {
        "vendedores": "Vendedores",
        "produtos": "Produtos",
        "categorias": "Categorias",
        "formas_pagamento": "Formas de pagamento",
    }
    for chave, rotulo in rotulos.items():
        conjunto = conjuntos[chave]
        fmt.rotulo(f"{rotulo} ({len(conjunto)})")
        fmt.lista_valores(sorted(conjunto))


if __name__ == "__main__":
    fmt.titulo("Análise de Vendas — Tratamento e Modelagem de Dados")

    dados = ler_dados_vendas()

    registros_sem_duplicados = remover_duplicados(dados["registros"])
    qtd_duplicados = len(dados["registros"]) - len(registros_sem_duplicados)

    exibir_resumo(dados, qtd_duplicados, len(registros_sem_duplicados))

    # Operações de conjuntos: comparando produtos entre dois vendedores
    produtos_por_vendedor = agrupar_produtos_por_vendedor(registros_sem_duplicados)
    resultado = comparar_vendedores(produtos_por_vendedor, "Beatriz", "Carlos")
    exibir_comparacao("Beatriz", "Carlos", resultado)

    # Modelagem dos dados com coleções avançadas (list, tuple, dict)
    registros_tratados = modelar_registros(registros_sem_duplicados)
    tuplas_id_valor = montar_tuplas_id_valor(registros_tratados)
    por_categoria = agrupar_por_categoria(registros_tratados)
    exibir_modelagem(registros_tratados, tuplas_id_valor, por_categoria)

    # Comprehensions: 2 list comprehensions + 1 dict comprehension
    limite_valor_alto = 1000.0
    vendas_altas = filtrar_vendas_altas(registros_tratados, limite_valor_alto)
    descricoes_vendas = gerar_descricoes_vendas(registros_tratados)
    mapa_valor_por_venda = mapear_valor_por_venda(registros_tratados)
    exibir_comprehensions(
        vendas_altas, descricoes_vendas, mapa_valor_por_venda, limite_valor_alto
    )

    fmt.rodape("Processamento concluído")