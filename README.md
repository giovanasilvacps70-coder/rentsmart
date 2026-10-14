# RentSmart — Sistema de Orçamento de Locação (R.M Imóveis)

Aplicação em **Python** (somente biblioteca padrão) que recebe as características de uma locação,
aplica automaticamente as regras comerciais da R.M Imóveis, apresenta um orçamento detalhado e
gera um **CSV com a projeção dos 12 primeiros meses** de contrato.

Projeto da disciplina *Algorithmic Thinking & Introduction to Object-Oriented Programming*.

## Requisitos

- Python **3.8 ou superior** (testado em 3.12)
- Nenhuma biblioteca externa

## Como executar

```bash
git clone <URL-DO-SEU-REPOSITORIO>
cd rentsmart
python main.py          # no Linux/macOS pode ser: python3 main.py
```

O programa faz perguntas no terminal, mostra o orçamento e cria o arquivo
`projecao_12_meses.csv` na pasta onde foi executado.

### Executar os testes automatizados

```bash
python -m unittest discover -s tests -v
```

## Regras de negócio implementadas

| Item | Regra |
|---|---|
| Aluguel-base | Apartamento 1 quarto **R$ 700** · Casa 1 quarto **R$ 900** · Estúdio **R$ 1.200** |
| 2 quartos | Apartamento **+ R$ 200** · Casa **+ R$ 250** |
| Garagem (casa/apto) | 1 vaga opcional: **+ R$ 300/mês** |
| Estacionamento (estúdio) | Pacote de 2 vagas **R$ 250** + **R$ 60** por vaga adicional |
| Desconto | Apartamento **sem crianças**: **5%** sobre o aluguel *após* os adicionais |
| Taxa contratual | **R$ 2.000**, em **1 a 5 parcelas**, apresentada **separada** do aluguel |

**Premissas adotadas** (o enunciado deixa em aberto):

- Estúdio com estacionamento: o cliente informa o **total** de vagas (mínimo 2 = pacote inicial, máximo 10). Ex.: 4 vagas = R$ 250 + 2 × R$ 60 = R$ 370.
- Se a taxa não divide em centavos exatos (ex.: 3x), a **última parcela** absorve a diferença (666,67 + 666,67 + 666,66).
- Valores monetários usam `Decimal` (sem erros de ponto flutuante).

## Estrutura do projeto

```
rentsmart/
├── main.py                     # ponto de entrada
├── rentsmart/
│   ├── imoveis.py              # Imovel (abstrata), ImovelResidencial, Apartamento, Casa, Estudio
│   ├── taxa_contratual.py      # TaxaContratual (valor e parcelamento)
│   ├── orcamento.py            # Orcamento + LinhaProjecao (cálculo, projeção, resumo)
│   ├── exportador_csv.py       # ExportadorCSV
│   ├── interface.py            # Entrada (validação) + MenuRentSmart (diálogo)
│   └── moeda.py                # arredondamento e formatação em R$
├── tests/test_rentsmart.py     # 13 testes unitários
├── exemplos/                   # execuções e CSVs de exemplo
└── docs/                       # PDF da parte teórica, fluxogramas e diagrama de classes
```

## Orientação a Objetos na solução

- **Abstração/Herança:** `Imovel` define o cálculo do aluguel uma única vez; `ImovelResidencial` concentra o que casa e apartamento têm em comum.
- **Polimorfismo:** cada tipo sobrescreve só o que muda (`aluguel_base`, `valor_garagem()`, `percentual_desconto()`…). O `Orcamento` não precisa saber qual é o tipo do imóvel.
- **Composição:** `Orcamento` *tem um* `Imovel` e *tem uma* `TaxaContratual`, mantendo aluguel e taxa como custos distintos.
- **Responsabilidade única:** interface, regras, orçamento e exportação ficam em classes/módulos separados.

## Exemplo de saída

Apartamento, 2 quartos, com garagem, sem crianças, taxa em 5x
(ver `exemplos/`):

```
  Aluguel-base (Apartamento 2 quarto(s))             R$ 700,00
  Adicional de 2 quartos                             R$ 200,00
  Vaga de garagem (1)                                R$ 300,00
  Subtotal                                         R$ 1.200,00
  Desconto de 5% (sem crianças)                      -R$ 60,00
  ALUGUEL MENSAL FINAL                             R$ 1.140,00
  Taxa: 5x de R$ 400,00
  TOTAL PREVISTO NO 1º ANO                        R$ 15.680,00
```

O CSV usa `;` como separador e vírgula decimal, abrindo corretamente no Excel em português.
