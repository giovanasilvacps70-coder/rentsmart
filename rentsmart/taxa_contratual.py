"""Taxa contratual: custo SEPARADO do aluguel mensal."""
from decimal import Decimal

from .moeda import dinheiro


class TaxaContratual:
    VALOR_PADRAO = dinheiro("2000.00")
    MAX_PARCELAS = 5

    def __init__(self, parcelas: int, valor: Decimal = VALOR_PADRAO):
        if not 1 <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(
                f"Parcelas devem estar entre 1 e {self.MAX_PARCELAS}."
            )
        self.parcelas = parcelas
        self.valor = dinheiro(valor)

    def valor_parcela(self) -> Decimal:
        return dinheiro(self.valor / self.parcelas)

    def cronograma(self) -> list:
        """Valor de cada parcela. A última absorve a diferença de centavos,
        garantindo que a soma seja exatamente o valor da taxa."""
        normal = self.valor_parcela()
        lista = [normal] * (self.parcelas - 1)
        lista.append(dinheiro(self.valor - normal * (self.parcelas - 1)))
        return lista

    def parcela_do_mes(self, mes: int) -> Decimal:
        """Parcela devida no mês informado (0 se já quitada)."""
        if 1 <= mes <= self.parcelas:
            return self.cronograma()[mes - 1]
        return dinheiro(0)
