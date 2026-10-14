"""Interface de terminal: coleta e valida as entradas do atendente."""
from .imoveis import Apartamento, Casa, Estudio, Imovel
from .orcamento import Orcamento
from .taxa_contratual import TaxaContratual


class Entrada:
    """Funções de leitura com validação (repetem até a resposta ser válida)."""

    @staticmethod
    def opcao(pergunta: str, validas: dict) -> str:
        """validas: {'1': 'Rótulo', ...}. Retorna a chave escolhida."""
        print(pergunta)
        for chave, rotulo in validas.items():
            print(f"  [{chave}] {rotulo}")
        while True:
            resposta = input("> ").strip()
            if resposta in validas:
                return resposta
            print(f"  Opção inválida. Escolha entre: {', '.join(validas)}.")

    @staticmethod
    def inteiro(pergunta: str, minimo: int, maximo: int) -> int:
        while True:
            resposta = input(f"{pergunta} ({minimo}-{maximo}): ").strip()
            if resposta.isdigit() and minimo <= int(resposta) <= maximo:
                return int(resposta)
            print(f"  Valor inválido. Digite um número inteiro de {minimo} a {maximo}.")

    @staticmethod
    def sim_nao(pergunta: str) -> bool:
        while True:
            resposta = input(f"{pergunta} (s/n): ").strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("  Resposta inválida. Digite 's' ou 'n'.")


class MenuRentSmart:
    """Conduz o diálogo e devolve um Orcamento pronto."""

    TIPOS = {"1": "Apartamento", "2": "Casa", "3": "Estúdio"}

    def montar_imovel(self) -> Imovel:
        tipo = Entrada.opcao("\nQual o tipo de imóvel?", self.TIPOS)
        if tipo == "3":
            return self._montar_estudio()
        return self._montar_residencial(apartamento=(tipo == "1"))

    def _montar_residencial(self, apartamento: bool) -> Imovel:
        quartos = int(Entrada.opcao("\nQuantos quartos?", {"1": "1 quarto", "2": "2 quartos"}))
        vagas = 1 if Entrada.sim_nao("\nDeseja vaga de garagem (+ R$ 300,00/mês)?") else 0
        if apartamento:
            criancas = Entrada.sim_nao("O cliente possui crianças?")
            return Apartamento(quartos, vagas, possui_criancas=criancas)
        return Casa(quartos, vagas)

    def _montar_estudio(self) -> Imovel:
        vagas = 0
        if Entrada.sim_nao("\nDeseja estacionamento? (pacote de 2 vagas por R$ 250,00; "
                           "vaga adicional R$ 60,00)"):
            vagas = Entrada.inteiro("Total de vagas desejadas",
                                    Estudio.PACOTE_VAGAS, Estudio.MAX_VAGAS)
        return Estudio(vagas)

    def montar_taxa(self) -> TaxaContratual:
        print(f"\nTaxa contratual: R$ 2.000,00 (parcelável em até "
              f"{TaxaContratual.MAX_PARCELAS}x).")
        parcelas = Entrada.inteiro("Em quantas parcelas?", 1, TaxaContratual.MAX_PARCELAS)
        return TaxaContratual(parcelas)

    def montar_orcamento(self) -> Orcamento:
        return Orcamento(self.montar_imovel(), self.montar_taxa())
