"""Hierarquia de imóveis da R.M Imóveis.

Imovel (abstrata)
├── ImovelResidencial (abstrata)  -> regras comuns a casa e apartamento
│   ├── Apartamento               -> + desconto de 5% sem crianças
│   └── Casa
└── Estudio                       -> regra própria de estacionamento

Cada subclasse sobrescreve apenas o que muda (polimorfismo), e o
cálculo geral do aluguel fica escrito uma única vez na classe base.
"""
from abc import ABC, abstractmethod
from decimal import Decimal

from .moeda import dinheiro


class Imovel(ABC):
    """Classe base: define o 'esqueleto' do cálculo do aluguel mensal."""

    NOME = ""
    QUARTOS_PERMITIDOS: tuple = ()

    def __init__(self, quartos: int, vagas: int = 0):
        self.quartos = quartos
        self.vagas = vagas
        self._validar()

    # ---------- validação ----------
    def _validar(self) -> None:
        if self.quartos not in self.QUARTOS_PERMITIDOS:
            raise ValueError(
                f"{self.NOME}: número de quartos inválido ({self.quartos}). "
                f"Permitido: {self.QUARTOS_PERMITIDOS}"
            )
        self._validar_vagas()

    @abstractmethod
    def _validar_vagas(self) -> None:
        """Cada tipo de imóvel tem sua própria regra de vagas."""

    # ---------- regras que variam por tipo ----------
    @property
    @abstractmethod
    def aluguel_base(self) -> Decimal:
        """Aluguel-base da categoria."""

    @abstractmethod
    def valor_garagem(self) -> Decimal:
        """Acréscimo mensal de estacionamento."""

    @abstractmethod
    def descricao_garagem(self) -> str:
        """Texto descrevendo o estacionamento contratado."""

    def adicional_quartos(self) -> Decimal:
        """Acréscimo por quartos extras (padrão: nenhum)."""
        return dinheiro(0)

    def percentual_desconto(self) -> Decimal:
        """Percentual de desconto aplicável (padrão: nenhum)."""
        return Decimal("0")

    def descricao_curta(self) -> str:
        return self.NOME

    # ---------- cálculo (escrito uma única vez) ----------
    def aluguel_bruto(self) -> Decimal:
        """Base + adicionais, antes de qualquer desconto."""
        return dinheiro(
            self.aluguel_base + self.adicional_quartos() + self.valor_garagem()
        )

    def valor_desconto(self) -> Decimal:
        return dinheiro(self.aluguel_bruto() * self.percentual_desconto())

    def aluguel_final(self) -> Decimal:
        """Aluguel mensal = bruto - desconto."""
        return dinheiro(self.aluguel_bruto() - self.valor_desconto())

    def composicao(self) -> list:
        """Lista (descrição, valor) mostrando como o aluguel foi formado."""
        linhas = [(f"Aluguel-base ({self.descricao_curta()})", self.aluguel_base)]
        if self.adicional_quartos() > 0:
            linhas.append((f"Adicional de {self.quartos} quartos",
                           self.adicional_quartos()))
        if self.valor_garagem() > 0:
            linhas.append((self.descricao_garagem(), self.valor_garagem()))
        return linhas


class ImovelResidencial(Imovel):
    """Regras compartilhadas por casas e apartamentos."""

    QUARTOS_PERMITIDOS = (1, 2)
    ADICIONAL_QUARTOS: dict = {}          # preenchido nas subclasses
    VALOR_VAGA = dinheiro("300.00")
    MAX_VAGAS = 1

    def _validar_vagas(self) -> None:
        if not 0 <= self.vagas <= self.MAX_VAGAS:
            raise ValueError(
                f"{self.NOME}: permitido de 0 a {self.MAX_VAGAS} vaga(s)."
            )

    def adicional_quartos(self) -> Decimal:
        return dinheiro(self.ADICIONAL_QUARTOS.get(self.quartos, 0))

    def valor_garagem(self) -> Decimal:
        return dinheiro(self.VALOR_VAGA * self.vagas)

    def descricao_garagem(self) -> str:
        return f"Vaga de garagem ({self.vagas})"

    def descricao_curta(self) -> str:
        return f"{self.NOME} {self.quartos} quarto(s)"


class Apartamento(ImovelResidencial):
    NOME = "Apartamento"
    ADICIONAL_QUARTOS = {1: 0, 2: 200}
    DESCONTO_SEM_CRIANCAS = Decimal("0.05")

    def __init__(self, quartos: int, vagas: int = 0, possui_criancas: bool = True):
        self.possui_criancas = possui_criancas
        super().__init__(quartos, vagas)

    @property
    def aluguel_base(self) -> Decimal:
        return dinheiro("700.00")

    def percentual_desconto(self) -> Decimal:
        # Desconto incide sobre o aluguel já com adicionais.
        return Decimal("0") if self.possui_criancas else self.DESCONTO_SEM_CRIANCAS


class Casa(ImovelResidencial):
    NOME = "Casa"
    ADICIONAL_QUARTOS = {1: 0, 2: 250}

    @property
    def aluguel_base(self) -> Decimal:
        return dinheiro("900.00")


class Estudio(Imovel):
    """Estúdio: sem quartos extras; estacionamento em pacote de 2 vagas."""

    NOME = "Estúdio"
    QUARTOS_PERMITIDOS = (0,)
    PACOTE_VAGAS = 2
    VALOR_PACOTE = dinheiro("250.00")
    VALOR_VAGA_ADICIONAL = dinheiro("60.00")
    MAX_VAGAS = 10

    def __init__(self, vagas: int = 0):
        super().__init__(quartos=0, vagas=vagas)

    @property
    def aluguel_base(self) -> Decimal:
        return dinheiro("1200.00")

    def _validar_vagas(self) -> None:
        # 0 = sem estacionamento; caso contrário, mínimo é o pacote inicial.
        if self.vagas != 0 and not self.PACOTE_VAGAS <= self.vagas <= self.MAX_VAGAS:
            raise ValueError(
                f"Estúdio: informe 0 (sem vaga) ou de {self.PACOTE_VAGAS} "
                f"a {self.MAX_VAGAS} vagas."
            )

    def vagas_adicionais(self) -> int:
        return max(0, self.vagas - self.PACOTE_VAGAS)

    def valor_garagem(self) -> Decimal:
        if self.vagas == 0:
            return dinheiro(0)
        return dinheiro(
            self.VALOR_PACOTE + self.VALOR_VAGA_ADICIONAL * self.vagas_adicionais()
        )

    def descricao_garagem(self) -> str:
        texto = f"Estacionamento (pacote {self.PACOTE_VAGAS} vagas"
        if self.vagas_adicionais():
            texto += f" + {self.vagas_adicionais()} extra(s)"
        return texto + ")"
