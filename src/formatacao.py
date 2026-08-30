"""
Módulo de formatação visual para a saída do programa no terminal.

Centralizar aqui garante que o "visual" do projeto seja consistente
em todos os tópicos, do início ao fim, sem repetir código de
impressão em cada função de exibição.
"""

import os

# Habilita suporte a códigos de cor ANSI no cmd do Windows.
# Sem essa linha, o cmd clássico exibiria os códigos como texto bruto
# em vez de aplicar a cor. Não tem efeito em Linux/Mac (já suportam).
if os.name == "nt":
    os.system("")


class Cor:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    CIANO = "\033[36m"
    AMARELO = "\033[33m"
    VERDE = "\033[32m"
    VERMELHO = "\033[31m"
    CINZA = "\033[90m"


LARGURA = 68


def titulo(texto):
    """Cabeçalho principal do programa (usado uma vez, no início)."""
    linha = "═" * LARGURA
    print(f"\n{Cor.CIANO}{Cor.NEGRITO}{linha}")
    print(texto.upper().center(LARGURA))
    print(f"{linha}{Cor.RESET}")


def secao(texto):
    """Cabeçalho de uma seção/etapa do processamento."""
    print(f"\n{Cor.AMARELO}{Cor.NEGRITO}▸ {texto}{Cor.RESET}")
    print(f"{Cor.CINZA}{'-' * LARGURA}{Cor.RESET}")


def item(rotulo, valor, destaque=False):
    """Uma linha do tipo 'rótulo: valor', alinhada."""
    cor = Cor.VERDE if destaque else ""
    print(f"  {rotulo:<30}{cor}{valor}{Cor.RESET}")


def rotulo(texto):
    """Uma linha de rótulo simples, sem valor associado (ex: antes de uma lista)."""
    print(f"  {Cor.NEGRITO}{texto}{Cor.RESET}")


def lista_valores(valores):
    """Imprime uma lista de valores separados por vírgula, indentada."""
    print(f"  {', '.join(str(v) for v in valores)}")


def linha_tabela(colunas, larguras):
    """
    Imprime uma linha de "tabela" alinhada por colunas.

    Parâmetros:
        colunas (list[str]): textos de cada coluna
        larguras (list[int]): largura de cada coluna, na mesma ordem
    """
    partes = [str(texto).ljust(largura) for texto, largura in zip(colunas, larguras)]
    print("  " + " ".join(partes))


def moeda(valor):
    """Formata um número no padrão monetário brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}"
    # troca temporária para inverter separador de milhar e decimal
    texto = texto.replace(",", "@").replace(".", ",").replace("@", ".")
    return f"R$ {texto}"


def rodape(texto=""):
    """Linha de fechamento do programa."""
    linha = "═" * LARGURA
    print(f"\n{Cor.CIANO}{linha}")
    if texto:
        print(texto.center(LARGURA))
    print(f"{linha}{Cor.RESET}\n")