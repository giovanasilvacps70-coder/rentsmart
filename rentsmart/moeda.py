"""Utilitários monetários.

Todo valor em reais é tratado como Decimal para evitar erros de ponto
flutuante (ex.: 0.1 + 0.2 != 0.3 com float).
"""
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


def dinheiro(valor) -> Decimal:
    """Converte qualquer número/str para Decimal com 2 casas decimais."""
    return Decimal(str(valor)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def formatar_brl(valor: Decimal) -> str:
    """Formata no padrão brasileiro: R$ 1.234,56."""
    texto = f"{dinheiro(valor):,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_csv(valor: Decimal) -> str:
    """Número com vírgula decimal e sem símbolo (ideal p/ Excel pt-BR)."""
    return f"{dinheiro(valor):.2f}".replace(".", ",")
