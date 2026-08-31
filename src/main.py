import csv
import os

import formatacao as fmt

DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PADRAO = os.path.join(DIR_SCRIPT, "..", "dados", "vendas.csv")


def ler_dados_vendas(caminho_arquivo=CAMINHO_PADRAO):
    """Lê o CSV e já monta os sets de valores únicos de cada coluna."""
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    registros = []
    vendedores = set()
    produtos = set()
    categorias = set()
    formas_pagamento = set()

    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            linha = {chave: valor.strip() for chave, valor in linha.items()}
            registros.append(linha)

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
    """Usa um set pra descartar linhas repetidas (dict não é hashable, por isso a tupla)."""
    vistos = set()
    registros_unicos = []

    for linha in registros:
        chave_linha = tuple(sorted(linha.items()))

        if chave_linha not in vistos:
            vistos.add(chave_linha)
            registros_unicos.append(linha)

    return registros_unicos


def modelar_registros(registros):
    """Converte os tipos (quantidade, valor) e calcula o valor_total de cada venda."""
    registros_tratados = []

    for linha in registros:
        quantidade = int(linha["quantidade"])
        valor_unitario = float(linha["valor_unitario"])
        valor_total = quantidade * valor_unitario

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

        registros_tratados.append(registro_tratado)

    return registros_tratados


def montar_tuplas_id_valor(registros_tratados):
    """Lista de tuplas (id_venda, valor_total) -- par fixo, não devia ser editado depois."""
    return [
        (registro["id_venda"], registro["valor_total"])
        for registro in registros_tratados
    ]


def agrupar_por_categoria(registros_tratados):
    """dict[categoria] -> lista de registros daquela categoria."""
    por_categoria = {}

    for registro in registros_tratados:
        categoria = registro["categoria"]
        por_categoria.setdefault(categoria, []).append(registro)

    return por_categoria


def filtrar_vendas_altas(registros_tratados, limite=1000.0):
    """List comprehension de filtragem: só vendas acima do limite."""
    return [venda for venda in registros_tratados if venda["valor_total"] > limite]


def gerar_descricoes_vendas(registros_tratados):
    """List comprehension de transformação: monta uma frase por venda."""
    return [
        f"{venda['produto'].strip().title()} vendido por {venda['vendedor']} "
        f"em {venda['data']}"
        for venda in registros_tratados
    ]


def mapear_valor_por_venda(registros_tratados):
    """Dict comprehension: id_venda -> valor_total (id é único, então não sobrescreve nada)."""
    return {venda["id_venda"]: venda["valor_total"] for venda in registros_tratados}


def exibir_comprehensions(vendas_altas, descricoes, mapa_valor_por_venda, limite):
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
    """dict[vendedor] -> set de produtos vendidos por ele."""
    produtos_por_vendedor = {}

    for linha in registros:
        vendedor = linha["vendedor"]
        produto = linha["produto"]

        if vendedor not in produtos_por_vendedor:
            produtos_por_vendedor[vendedor] = set()

        produtos_por_vendedor[vendedor].add(produto)

    return produtos_por_vendedor


def comparar_vendedores(produtos_por_vendedor, vendedor_a, vendedor_b):
    """União, interseção e diferença entre os produtos de dois vendedores."""
    set_a = produtos_por_vendedor[vendedor_a]
    set_b = produtos_por_vendedor[vendedor_b]

    return {
        "uniao": set_a | set_b,
        "intersecao": set_a & set_b,
        "diferenca_a_b": set_a - set_b,
        "diferenca_b_a": set_b - set_a,
    }


def consulta_1_faturamento(registros_tratados):
    """Faturamento total e por vendedor, do maior pro menor."""
    faturamento_total = sum(venda["valor_total"] for venda in registros_tratados)

    faturamento_por_vendedor = {}
    for venda in registros_tratados:
        vendedor = venda["vendedor"]
        faturamento_por_vendedor[vendedor] = (
            faturamento_por_vendedor.get(vendedor, 0.0) + venda["valor_total"]
        )

    faturamento_por_vendedor = dict(
        sorted(faturamento_por_vendedor.items(), key=lambda par: par[1], reverse=True)
    )

    return {
        "faturamento_total": faturamento_total,
        "faturamento_por_vendedor": faturamento_por_vendedor,
    }


def consulta_2_maior_volume(registros_tratados):
    """Produto e categoria mais vendidos em QUANTIDADE (não em R$)."""
    volume_por_produto = {}
    volume_por_categoria = {}

    for venda in registros_tratados:
        produto = venda["produto"]
        categoria = venda["categoria"]
        volume_por_produto[produto] = (
            volume_por_produto.get(produto, 0) + venda["quantidade"]
        )
        volume_por_categoria[categoria] = (
            volume_por_categoria.get(categoria, 0) + venda["quantidade"]
        )

    volume_por_produto = dict(
        sorted(volume_por_produto.items(), key=lambda par: par[1], reverse=True)
    )
    volume_por_categoria = dict(
        sorted(volume_por_categoria.items(), key=lambda par: par[1], reverse=True)
    )

    produto_top = next(iter(volume_por_produto.items()))
    categoria_top = next(iter(volume_por_categoria.items()))

    return {
        "volume_por_produto": volume_por_produto,
        "volume_por_categoria": volume_por_categoria,
        "produto_top": produto_top,
        "categoria_top": categoria_top,
    }


def consulta_3_comparar_portfolio(registros_tratados, vendedor_a, vendedor_b):
    """Reaproveita as funções de set pra comparar o portfólio de dois vendedores."""
    produtos_por_vendedor = agrupar_produtos_por_vendedor(registros_tratados)
    return comparar_vendedores(produtos_por_vendedor, vendedor_a, vendedor_b)


def exibir_consulta_1(resultado):
    fmt.secao("Consulta 1 — Faturamento total e por vendedor")
    fmt.item("Faturamento total", fmt.moeda(resultado["faturamento_total"]), destaque=True)
    print()
    larguras = [20, 16]
    fmt.linha_tabela(["Vendedor", "Faturamento"], larguras)
    for vendedor, valor in resultado["faturamento_por_vendedor"].items():
        fmt.linha_tabela([vendedor, fmt.moeda(valor)], larguras)


def exibir_consulta_2(resultado):
    fmt.secao("Consulta 2 — Maior volume de vendas (produtos e categorias)")

    produto_nome, produto_qtd = resultado["produto_top"]
    categoria_nome, categoria_qtd = resultado["categoria_top"]
    fmt.item("Produto mais vendido", f"{produto_nome} ({produto_qtd} un.)", destaque=True)
    fmt.item(
        "Categoria mais vendida", f"{categoria_nome} ({categoria_qtd} un.)", destaque=True
    )

    print()
    larguras = [20, 16]
    fmt.rotulo("Ranking por produto (unidades vendidas)")
    fmt.linha_tabela(["Produto", "Unidades"], larguras)
    for produto, qtd in resultado["volume_por_produto"].items():
        fmt.linha_tabela([produto, qtd], larguras)

    print()
    fmt.rotulo("Ranking por categoria (unidades vendidas)")
    fmt.linha_tabela(["Categoria", "Unidades"], larguras)
    for categoria, qtd in resultado["volume_por_categoria"].items():
        fmt.linha_tabela([categoria, qtd], larguras)


def exibir_consulta_3(vendedor_a, vendedor_b, resultado):
    fmt.secao(f"Consulta 3 — Portfólio de produtos: {vendedor_a} × {vendedor_b}")
    fmt.rotulo("União (A | B) — todos os produtos vendidos por algum dos dois")
    fmt.lista_valores(sorted(resultado["uniao"]))
    fmt.rotulo("Interseção (A & B) — produtos que ambos venderam")
    fmt.lista_valores(sorted(resultado["intersecao"]))
    fmt.rotulo(f"Diferença — só {vendedor_a} vendeu")
    fmt.lista_valores(sorted(resultado["diferenca_a_b"]))
    fmt.rotulo(f"Diferença — só {vendedor_b} vendeu")
    fmt.lista_valores(sorted(resultado["diferenca_b_a"]))


def exibir_comparacao(vendedor_a, vendedor_b, resultado):
    fmt.secao(f"Operações de conjunto: {vendedor_a} × {vendedor_b}")
    fmt.rotulo("União (A | B)")
    fmt.lista_valores(sorted(resultado["uniao"]))
    fmt.rotulo("Interseção (A & B)")
    fmt.lista_valores(sorted(resultado["intersecao"]))
    fmt.rotulo(f"Só {vendedor_a} (A - B)")
    fmt.lista_valores(sorted(resultado["diferenca_a_b"]))
    fmt.rotulo(f"Só {vendedor_b} (B - A)")
    fmt.lista_valores(sorted(resultado["diferenca_b_a"]))


def exibir_resumo(total_lido, qtd_duplicados, total_final, conjuntos):
    fmt.secao("Leitura e limpeza da base")
    fmt.item("Registros lidos", total_lido)
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


def funcao_1_carregar_e_limpar_dados(caminho_arquivo=CAMINHO_PADRAO):
    """Lê o CSV, tira duplicata e converte os tipos. É a única função que mexe no disco."""
    dados_brutos = ler_dados_vendas(caminho_arquivo)
    registros_sem_duplicados = remover_duplicados(dados_brutos["registros"])
    qtd_duplicados = len(dados_brutos["registros"]) - len(registros_sem_duplicados)
    registros_tratados = modelar_registros(registros_sem_duplicados)

    return {
        "registros_tratados": registros_tratados,
        "total_lido": len(dados_brutos["registros"]),
        "qtd_duplicados": qtd_duplicados,
    }


def funcao_2_processar_analises(dados_carregados, limite_valor_alto=1000.0):
    """Roda todas as análises (sets, comprehensions, consultas). Só calcula, não imprime."""
    registros_tratados = dados_carregados["registros_tratados"]

    conjuntos = {
        "vendedores": {r["vendedor"] for r in registros_tratados},
        "produtos": {r["produto"] for r in registros_tratados},
        "categorias": {r["categoria"] for r in registros_tratados},
        "formas_pagamento": {r["pagamento"] for r in registros_tratados},
    }

    vendedor_a, vendedor_b = "Beatriz", "Carlos"
    produtos_por_vendedor = agrupar_produtos_por_vendedor(registros_tratados)
    comparacao_vendedores = comparar_vendedores(
        produtos_por_vendedor, vendedor_a, vendedor_b
    )

    tuplas_id_valor = montar_tuplas_id_valor(registros_tratados)
    por_categoria = agrupar_por_categoria(registros_tratados)

    vendas_altas = filtrar_vendas_altas(registros_tratados, limite_valor_alto)
    descricoes_vendas = gerar_descricoes_vendas(registros_tratados)
    mapa_valor_por_venda = mapear_valor_por_venda(registros_tratados)

    resultado_consulta_1 = consulta_1_faturamento(registros_tratados)
    resultado_consulta_2 = consulta_2_maior_volume(registros_tratados)
    resultado_consulta_3 = consulta_3_comparar_portfolio(
        registros_tratados, vendedor_a, vendedor_b
    )

    return {
        "total_lido": dados_carregados["total_lido"],
        "qtd_duplicados": dados_carregados["qtd_duplicados"],
        "registros_tratados": registros_tratados,
        "conjuntos": conjuntos,
        "vendedor_a": vendedor_a,
        "vendedor_b": vendedor_b,
        "comparacao_vendedores": comparacao_vendedores,
        "tuplas_id_valor": tuplas_id_valor,
        "por_categoria": por_categoria,
        "limite_valor_alto": limite_valor_alto,
        "vendas_altas": vendas_altas,
        "descricoes_vendas": descricoes_vendas,
        "mapa_valor_por_venda": mapa_valor_por_venda,
        "resultado_consulta_1": resultado_consulta_1,
        "resultado_consulta_2": resultado_consulta_2,
        "resultado_consulta_3": resultado_consulta_3,
    }


def funcao_3_exibir_relatorio(analises):
    """Imprime tudo formatado. É a única função que faz print()."""
    fmt.titulo("Análise de Vendas — Relatório Completo")

    exibir_resumo(
        analises["total_lido"],
        analises["qtd_duplicados"],
        len(analises["registros_tratados"]),
        analises["conjuntos"],
    )

    exibir_comparacao(
        analises["vendedor_a"], analises["vendedor_b"], analises["comparacao_vendedores"]
    )

    exibir_modelagem(
        analises["registros_tratados"],
        analises["tuplas_id_valor"],
        analises["por_categoria"],
    )

    exibir_comprehensions(
        analises["vendas_altas"],
        analises["descricoes_vendas"],
        analises["mapa_valor_por_venda"],
        analises["limite_valor_alto"],
    )

    exibir_consulta_1(analises["resultado_consulta_1"])
    exibir_consulta_2(analises["resultado_consulta_2"])
    exibir_consulta_3(
        analises["vendedor_a"], analises["vendedor_b"], analises["resultado_consulta_3"]
    )

    fmt.rodape("Processamento concluído")


if __name__ == "__main__":
    dados_carregados = funcao_1_carregar_e_limpar_dados()
    analises = funcao_2_processar_analises(dados_carregados)
    funcao_3_exibir_relatorio(analises)