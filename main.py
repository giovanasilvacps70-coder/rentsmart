"""RentSmart - ponto de entrada.

Execute:  python main.py
"""
import sys

from rentsmart.exportador_csv import ExportadorCSV
from rentsmart.interface import MenuRentSmart


def main() -> int:
    print("=" * 58)
    print("  RentSmart - Orçamento de Locação | R.M Imóveis")
    print("=" * 58)
    try:
        orcamento = MenuRentSmart().montar_orcamento()
    except (KeyboardInterrupt, EOFError):
        print("\nAtendimento cancelado.")
        return 1

    print()
    print(orcamento.resumo())

    caminho = ExportadorCSV("projecao_12_meses.csv").exportar(orcamento)
    print(f"\nProjeção de 12 meses salva em: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
