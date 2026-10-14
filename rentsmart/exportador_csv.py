"""Exporta a projeção de 12 meses para CSV (compatível com Excel pt-BR)."""
import csv

from .moeda import formatar_csv
from .orcamento import Orcamento


class ExportadorCSV:
    CABECALHO = ["mes", "aluguel_mensal", "parcela_taxa_contratual", "total_do_mes"]

    def __init__(self, caminho: str = "projecao_12_meses.csv"):
        self.caminho = caminho

    def exportar(self, orcamento: Orcamento) -> str:
        # utf-8-sig + ';' + vírgula decimal: abre direto no Excel brasileiro.
        with open(self.caminho, "w", newline="", encoding="utf-8-sig") as arq:
            escritor = csv.writer(arq, delimiter=";")
            escritor.writerow(self.CABECALHO)
            for linha in orcamento.projecao():
                escritor.writerow([
                    linha.mes,
                    formatar_csv(linha.aluguel),
                    formatar_csv(linha.parcela_taxa),
                    formatar_csv(linha.total),
                ])
            escritor.writerow([
                "TOTAL",
                formatar_csv(orcamento.total_aluguel_ano()),
                formatar_csv(orcamento.total_taxa_ano()),
                formatar_csv(orcamento.total_primeiro_ano()),
            ])
        return self.caminho
