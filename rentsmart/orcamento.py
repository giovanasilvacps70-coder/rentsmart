"""Orçamento: junta o imóvel e a taxa contratual e gera a projeção."""
from dataclasses import dataclass
from decimal import Decimal

from .imoveis import Imovel
from .moeda import dinheiro, formatar_brl
from .taxa_contratual import TaxaContratual


@dataclass(frozen=True)
class LinhaProjecao:
    """Uma linha da projeção mensal."""
    mes: int
    aluguel: Decimal
    parcela_taxa: Decimal

    @property
    def total(self) -> Decimal:
        return dinheiro(self.aluguel + self.parcela_taxa)


class Orcamento:
    MESES_PROJECAO = 12
    LARGURA = 62

    def __init__(self, imovel: Imovel, taxa: TaxaContratual):
        self.imovel = imovel
        self.taxa = taxa

    # ---------- projeção ----------
    def projecao(self) -> list:
        return [
            LinhaProjecao(
                mes=mes,
                aluguel=self.imovel.aluguel_final(),
                parcela_taxa=self.taxa.parcela_do_mes(mes),
            )
            for mes in range(1, self.MESES_PROJECAO + 1)
        ]

    def total_aluguel_ano(self) -> Decimal:
        return dinheiro(sum(l.aluguel for l in self.projecao()))

    def total_taxa_ano(self) -> Decimal:
        return dinheiro(sum(l.parcela_taxa for l in self.projecao()))

    def total_primeiro_ano(self) -> Decimal:
        return dinheiro(self.total_aluguel_ano() + self.total_taxa_ano())

    # ---------- apresentação ----------
    def _linha(self, descricao: str, valor: Decimal, sinal: str = "") -> str:
        v = f"{sinal}{formatar_brl(valor)}"
        return f"  {descricao:<{self.LARGURA - 18}}{v:>16}"

    def resumo(self) -> str:
        im, tx = self.imovel, self.taxa
        sep = "=" * self.LARGURA
        traco = "-" * self.LARGURA
        out = [sep, "ORÇAMENTO DE LOCAÇÃO - R.M IMÓVEIS (RentSmart)".center(self.LARGURA), sep,
               "", "1) ALUGUEL MENSAL", traco]
        for descricao, valor in im.composicao():
            out.append(self._linha(descricao, valor))
        out.append(traco)
        out.append(self._linha("Subtotal", im.aluguel_bruto()))
        if im.percentual_desconto() > 0:
            pct = int(im.percentual_desconto() * 100)
            out.append(self._linha(f"Desconto de {pct}% (sem crianças)",
                                   im.valor_desconto(), "-"))
        out.append(self._linha("ALUGUEL MENSAL FINAL", im.aluguel_final()))
        out += ["", "2) TAXA CONTRATUAL (cobrada à parte do aluguel)", traco,
                self._linha("Valor total da taxa", tx.valor),
                f"  Parcelamento: {tx.parcelas}x de {formatar_brl(tx.valor_parcela())}"
                + (f" (última parcela {formatar_brl(tx.cronograma()[-1])})"
                   if tx.cronograma()[-1] != tx.valor_parcela() else ""),
                "", "3) RESUMO DO PRIMEIRO ANO (12 meses)", traco,
                self._linha("Aluguel (12 x mensal)", self.total_aluguel_ano()),
                self._linha("Taxa contratual", self.total_taxa_ano()),
                traco,
                self._linha("TOTAL PREVISTO NO 1º ANO", self.total_primeiro_ano()),
                sep]
        return "\n".join(out)
