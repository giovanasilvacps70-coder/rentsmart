import csv
import os
import tempfile
import unittest
from decimal import Decimal

from rentsmart.exportador_csv import ExportadorCSV
from rentsmart.imoveis import Apartamento, Casa, Estudio
from rentsmart.orcamento import Orcamento
from rentsmart.taxa_contratual import TaxaContratual

D = Decimal


class TestAluguel(unittest.TestCase):
    def test_bases(self):
        self.assertEqual(Apartamento(1).aluguel_final(), D("700.00"))
        self.assertEqual(Casa(1).aluguel_final(), D("900.00"))
        self.assertEqual(Estudio().aluguel_final(), D("1200.00"))

    def test_adicional_dois_quartos(self):
        self.assertEqual(Apartamento(2).aluguel_final(), D("900.00"))
        self.assertEqual(Casa(2).aluguel_final(), D("1150.00"))

    def test_garagem_casa_e_apartamento(self):
        self.assertEqual(Apartamento(1, 1).aluguel_final(), D("1000.00"))
        self.assertEqual(Casa(1, 1).aluguel_final(), D("1200.00"))

    def test_estudio_estacionamento(self):
        self.assertEqual(Estudio(2).aluguel_final(), D("1450.00"))
        self.assertEqual(Estudio(3).aluguel_final(), D("1510.00"))
        self.assertEqual(Estudio(4).aluguel_final(), D("1570.00"))

    def test_desconto_apartamento_sem_criancas(self):
        self.assertEqual(Apartamento(1, 0, possui_criancas=False).aluguel_final(), D("665.00"))
        # desconto incide após adicionais: (700+200+300) * 0,95
        self.assertEqual(Apartamento(2, 1, possui_criancas=False).aluguel_final(), D("1140.00"))
        self.assertEqual(Apartamento(2, 1, possui_criancas=True).aluguel_final(), D("1200.00"))

    def test_casa_nunca_tem_desconto(self):
        self.assertEqual(Casa(2, 1).aluguel_final(), D("1450.00"))


class TestValidacao(unittest.TestCase):
    def test_quartos_invalidos(self):
        with self.assertRaises(ValueError):
            Apartamento(3)
        with self.assertRaises(ValueError):
            Casa(0)

    def test_vagas_invalidas(self):
        with self.assertRaises(ValueError):
            Casa(1, 2)
        with self.assertRaises(ValueError):
            Estudio(1)
        with self.assertRaises(ValueError):
            Estudio(11)

    def test_parcelas_invalidas(self):
        for p in (0, 6, -1):
            with self.assertRaises(ValueError):
                TaxaContratual(p)


class TestTaxa(unittest.TestCase):
    def test_soma_das_parcelas_e_exata(self):
        for p in range(1, 6):
            self.assertEqual(sum(TaxaContratual(p).cronograma()), D("2000.00"))

    def test_ajuste_de_centavos(self):
        self.assertEqual(TaxaContratual(3).cronograma(),
                         [D("666.67"), D("666.67"), D("666.66")])


class TestProjecaoCSV(unittest.TestCase):
    def setUp(self):
        self.orc = Orcamento(Apartamento(2, 1, possui_criancas=False), TaxaContratual(5))

    def test_projecao(self):
        proj = self.orc.projecao()
        self.assertEqual(len(proj), 12)
        self.assertEqual(proj[0].total, D("1540.00"))
        self.assertEqual(proj[5].total, D("1140.00"))
        self.assertEqual(self.orc.total_primeiro_ano(), D("15680.00"))

    def test_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = ExportadorCSV(os.path.join(pasta, "p.csv")).exportar(self.orc)
            with open(caminho, encoding="utf-8-sig", newline="") as f:
                linhas = list(csv.reader(f, delimiter=";"))
        self.assertEqual(len(linhas), 14)  # cabeçalho + 12 meses + total
        self.assertEqual(linhas[1], ["1", "1140,00", "400,00", "1540,00"])
        self.assertEqual(linhas[-1], ["TOTAL", "13680,00", "2000,00", "15680,00"])


if __name__ == "__main__":
    unittest.main()
