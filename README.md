# TED 01 — Processamento e Análise de Dados com Coleções em Python

## Integrantes
* **Luiz Fernando Carvalho da Costa** — Matrícula: 26.1.13589
* **Kawê Victor Lima de Oliveira** — Matrícula: 26.1.16277
* **Joacy Arruda de Assis Junior** — Matrícula: 25.1.08341

---

## Cenário
* **Cenário Escolhido:** Cenário 01 — Gestão e Monitoramento do Desempenho de Vendas
* **Descrição:** A base bruta contém o histórico detalhado de vendas de uma loja. O desafio consiste em tratar inconsistências e dados duplicados na origem para viabilizar o cálculo exato do faturamento global, a medição do volume de itens vendidos por categoria e o mapeamento comparativo de portfólios individuais entre vendedores.

---

## Descrição da Solução
O programa foi desenvolvido em Python puro para ler, higienizar e analisar dados de vendas sem o uso de bibliotecas externas. A solução lê o arquivo de dados brutos na pasta `dados/`, remove os registros duplicados e organiza as informações em memória usando coleções nativas. Em seguida, processa os relatórios solicitados e exibe os resultados formatados no terminal.

---

## Estruturas de Dados Utilizadas
* **Conjuntos (`set`):** Utilizados para eliminar os registros duplicados durante a leitura e para comparar o portfólio de produtos entre vendedores (operadores de diferença/interseção).
* **Listas (`list`):** Utilizadas para armazenar a coleção de vendas limpas e processar iterações sequenciais.
* **Dicionários (`dict`):** Utilizados para estruturar cada registro de venda como um objeto (mapeando chaves como `vendedor`, `produto`, `valor`) e para agrupar faturamentos.
* **Tuplas (`tuple`):** Utilizadas para armazenar dados imutáveis, como pares `(vendedor, faturamento)` ordenados.
* **List Comprehension:** Aplicada para filtrar vendas acima de determinado valor e extrair/sanitizar nomes de produtos únicos.
* **Dict Comprehension:** Aplicada para transformar a lista de vendas em um dicionário de faturamento acumulado por categoria/vendedor.

---

## Principais Análises Realizadas

1. **Faturamento Global e Desempenho Financeiro por Vendedor:**
   - **Método:** Mapeamento via *Dict Comprehension* e agrupamento por chave de vendedor, ordenando o resultado final em tuplas com a função `sorted()`.
   - **Resultado:** Apresenta o faturamento total da loja, o ticket médio e a lista formatada do ranking de vendas por colaborador.

2. **Métricas de Volume por Produto e Categoria:**
   - **Método:** Processamento de contagem acumulada em dicionários para calcular o volume de unidades vendidas e o montante arrecadado por segmento.
   - **Resultado:** Exibição dos itens "campeões de vendas" e a distribuição percentual de cada categoria no faturamento global.

3. **Análise de Exclusividade de Portfólio (Teoria dos Conjuntos):**
   - **Método:** Aplicação das operações de **diferença (`set.difference` ou `-`)** e **interseção (`set.intersection` ou `&`)** sobre os conjuntos de produtos comercializados por cada vendedor.
   - **Resultado:** Identificação de itens vendidos exclusivamente por um determinado vendedor e verificação de produtos compartilhados por toda a equipe.

---

## Instruções de Execução
1. Certifique-se de ter o **Python 3.10+** instalado em sua máquina.
2. Abra o terminal na raiz do projeto (`ted-01-python-colecoes`).
3. Execute o comando:
   ```bash
   python src/main.py