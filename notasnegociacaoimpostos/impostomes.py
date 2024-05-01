from notasnegociacaoimpostos.carteiragruporegistros import CarteiraGrupoRegistros
from notasnegociacaoimpostos.util import Util
import calendar
import datetime


class ImpostoMes:
    data: datetime.date
    operacoesComuns: float
    operacoesDayTrade: float

    def __init__(self, data: datetime.date):
        ultimoDia = calendar.monthrange(data.year, data.month)[1]
        self.data = datetime.date(data.year, data.month, ultimoDia)

        self.operacoesComuns = 0
        self.operacoesDayTrade = 0

    @staticmethod
    def getImpostos(carteira: list[CarteiraGrupoRegistros]) -> list['ImpostoMes']:
        mesAtual = ''
        mesAtualSomaTributavel = 0
        mesAtualSomaTributavelDayTrade = 0
        somaTributavel = 0
        somaTributavelDayTrade = 0
        impostos: list['ImpostoMes'] = []
        for regCarteira in carteira:
            for r in regCarteira.registros:
                somaTributavel += r.resultadoTributavel
                somaTributavelDayTrade += r.resultadoTributavelDayTrade

                if r.resultadoTributavel != 0 or r.resultadoTributavelDayTrade != 0:
                    mes = Util.strToDate(regCarteira.data).strftime('%Y-%m')
                    if mesAtual != mes:
                        if mesAtualSomaTributavel > 0 or mesAtualSomaTributavelDayTrade > 0:
                            impostos.append(ImpostoMes.__getImpostoMes(
                                mesAtual, mesAtualSomaTributavel, mesAtualSomaTributavelDayTrade))

                        if mesAtualSomaTributavel > 0:
                            mesAtualSomaTributavel = 0

                        if mesAtualSomaTributavelDayTrade > 0:
                            mesAtualSomaTributavelDayTrade = 0

                        mesAtual = mes

                    mesAtualSomaTributavel += r.resultadoTributavel
                    mesAtualSomaTributavelDayTrade += r.resultadoTributavelDayTrade

        if mesAtualSomaTributavel > 0 or mesAtualSomaTributavelDayTrade > 0:
            impostos.append(ImpostoMes.__getImpostoMes(
                mesAtual, mesAtualSomaTributavel, mesAtualSomaTributavelDayTrade))

        return impostos

    @staticmethod
    def __getImpostoMes(mesAtual: str, mesAtualSomaTributavel: float, mesAtualSomaTributavelDayTrade: float) -> 'ImpostoMes':
        ano = int(mesAtual[:4])
        mes = int(mesAtual[-2:])

        # define dataImposto como o mês seguinte
        dataImposto = datetime.datetime(ano + int(mes / 12), (mes % 12) + 1, 1)

        imposto = ImpostoMes(dataImposto)

        if mesAtualSomaTributavel > 0:
            imposto.operacoesComuns = mesAtualSomaTributavel * .15

        if mesAtualSomaTributavelDayTrade > 0:
            imposto.operacoesDayTrade = mesAtualSomaTributavelDayTrade * .2

        return imposto
