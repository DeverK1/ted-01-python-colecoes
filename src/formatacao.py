import os

# ativa cor no cmd do Windows (sem isso aparece código bruto tipo \033[36m)
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
    linha = "═" * LARGURA
    print(f"\n{Cor.CIANO}{Cor.NEGRITO}{linha}")
    print(texto.upper().center(LARGURA))
    print(f"{linha}{Cor.RESET}")


def secao(texto):
    print(f"\n{Cor.AMARELO}{Cor.NEGRITO}▸ {texto}{Cor.RESET}")
    print(f"{Cor.CINZA}{'-' * LARGURA}{Cor.RESET}")


def item(rotulo, valor, destaque=False):
    cor = Cor.VERDE if destaque else ""
    print(f"  {rotulo:<30}{cor}{valor}{Cor.RESET}")


def rotulo(texto):
    print(f"  {Cor.NEGRITO}{texto}{Cor.RESET}")


def lista_valores(valores):
    print(f"  {', '.join(str(v) for v in valores)}")


def linha_tabela(colunas, larguras):
    partes = [str(texto).ljust(largura) for texto, largura in zip(colunas, larguras)]
    print("  " + " ".join(partes))


def moeda(valor):
    """Formata pro padrão brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "@").replace(".", ",").replace("@", ".")
    return f"R$ {texto}"


def rodape(texto=""):
    linha = "═" * LARGURA
    print(f"\n{Cor.CIANO}{linha}")
    if texto:
        print(texto.center(LARGURA))
    print(f"{linha}{Cor.RESET}\n")