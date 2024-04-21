from notasnegociacao.notanegociacao import NotaNegociacao
from notasnegociacao.negociorealizadoimpostos import NegocioRealizadoImpostos


class NotaNegociacaoNegocioImpostos(NotaNegociacao):
    negociosRealizados: list[NegocioRealizadoImpostos]
