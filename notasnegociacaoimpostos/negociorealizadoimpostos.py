from notasnegociacao.negociorealizado import NegocioRealizado
from notasnegociacao.resumofinanceiro import ResumoFinanceiro
from notasnegociacao.notanegociacao import NotaNegociacao


class NegocioRealizadoImpostos(NegocioRealizado):
    resumoFinanceiro: ResumoFinanceiro

    def __init__(self):
        self.resumoFinanceiro = ResumoFinanceiro()

    @staticmethod
    def calcResumoFinanceiroNegocio(nota: 'NotaNegociacaoNegocioImpostos') -> None:
        valorOperacoes = nota.resumoNegocios.valorOperacoes
        for negocio in nota.negociosRealizados:
            perc = abs(negocio.valorOperacaoAjuste /
                       valorOperacoes)

            negocio.resumoFinanceiro.clearing.taxaLiquidacao = nota.resumoFinanceiro.clearing.taxaLiquidacao * perc
            negocio.resumoFinanceiro.clearing.taxaRegistro = nota.resumoFinanceiro.clearing.taxaRegistro * perc
            negocio.resumoFinanceiro.clearing.totalCBLC = \
                negocio.valorOperacaoAjuste + \
                negocio.resumoFinanceiro.clearing.taxaLiquidacao + \
                negocio.resumoFinanceiro.clearing.taxaRegistro

            negocio.resumoFinanceiro.bolsa.taxaTermoOpcoes = nota.resumoFinanceiro.bolsa.taxaTermoOpcoes * perc
            negocio.resumoFinanceiro.bolsa.taxaANA = nota.resumoFinanceiro.bolsa.taxaANA * perc
            negocio.resumoFinanceiro.bolsa.emolumentos = nota.resumoFinanceiro.bolsa.emolumentos * perc
            negocio.resumoFinanceiro.bolsa.totalBovespaSoma = \
                negocio.resumoFinanceiro.bolsa.taxaTermoOpcoes + \
                negocio.resumoFinanceiro.bolsa.taxaANA + \
                negocio.resumoFinanceiro.bolsa.emolumentos

            negocio.resumoFinanceiro.custosOperacionais.taxaOperacional = nota.resumoFinanceiro.custosOperacionais.taxaOperacional * perc
            negocio.resumoFinanceiro.custosOperacionais.execucao = nota.resumoFinanceiro.custosOperacionais.execucao * perc
            negocio.resumoFinanceiro.custosOperacionais.taxaCustodia = nota.resumoFinanceiro.custosOperacionais.taxaCustodia * perc
            negocio.resumoFinanceiro.custosOperacionais.impostos = nota.resumoFinanceiro.custosOperacionais.impostos * perc
            negocio.resumoFinanceiro.custosOperacionais.outros = nota.resumoFinanceiro.custosOperacionais.outros * perc

            negocio.resumoFinanceiro.custosOperacionais.totalCustosDespesas = \
                negocio.resumoFinanceiro.custosOperacionais.taxaOperacional + \
                negocio.resumoFinanceiro.custosOperacionais.execucao + \
                negocio.resumoFinanceiro.custosOperacionais.taxaCustodia + \
                negocio.resumoFinanceiro.custosOperacionais.impostos + \
                negocio.resumoFinanceiro.custosOperacionais.outros

            if hasattr(nota.resumoFinanceiro.custosOperacionais, 'irrfDayTradeProjecao'):
                negocio.resumoFinanceiro.custosOperacionais.irrfDayTradeProjecao = nota.resumoFinanceiro.custosOperacionais.irrfDayTradeProjecao * perc
                negocio.resumoFinanceiro.custosOperacionais.totalCustosDespesas += negocio.resumoFinanceiro.custosOperacionais.irrfDayTradeProjecao

            if hasattr(nota.resumoFinanceiro.custosOperacionais, 'irrfSOperacoes'):
                negocio.resumoFinanceiro.custosOperacionais.irrfSOperacoes = nota.resumoFinanceiro.custosOperacionais.irrfSOperacoes * perc
                negocio.resumoFinanceiro.custosOperacionais.totalCustosDespesas += negocio.resumoFinanceiro.custosOperacionais.irrfSOperacoes


class NotaNegociacaoNegocioImpostos(NotaNegociacao):
    negociosRealizados: list[NegocioRealizadoImpostos]
