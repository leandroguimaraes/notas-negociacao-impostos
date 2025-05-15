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
        mesAtualSomaTributavelVista = 0
        mesAtualSomaTributavelDayTradeVista = 0
        mesAtualSomaTributavelOpcoes = 0
        mesAtualSomaTributavelDayTradeOpcoes = 0
        somaTributavel = 0
        somaTributavelDayTrade = 0
        impostos: list['ImpostoMes'] = []
        print('-'*50)
        for regCarteira in carteira:
            for r in regCarteira.registros:
                if r.resultadoTributavel != 0 or r.resultadoTributavelDayTrade != 0:
                    mes = Util.strToDate(regCarteira.data).strftime('%Y-%m')
                    if (mesAtual == ''):
                        mesAtual = mes

                    if mesAtual != mes:
                        if somaTributavel > 0 or somaTributavelDayTrade > 0:
                            impostos.append(ImpostoMes.__getImpostoMes(
                                mesAtual, somaTributavel, somaTributavelDayTrade))
                            
                            if somaTributavel > 0:
                                somaTributavel = 0

                            if somaTributavelDayTrade > 0:
                                somaTributavelDayTrade = 0

                        print(mesAtual)
                        print(f'{mesAtual}: Ações: R$ {round(mesAtualSomaTributavelVista, 2)} Ações Day Trade: R$ {
                              round(mesAtualSomaTributavelDayTradeVista, 2)}')
                        print(f'{mesAtual}: Opções: R$ {round(mesAtualSomaTributavelOpcoes, 2)} Opções Day Trade: R$ {
                              round(mesAtualSomaTributavelDayTradeOpcoes, 2)}')
                        print('[ACUMULADO]')
                        print(f'Normal: R$ {round(somaTributavel, 2)}')
                        print(f'Day Trade: R$ {round(somaTributavelDayTrade, 2)}')
                        print('-'*10)

                        mesAtualSomaTributavelVista = 0
                        mesAtualSomaTributavelOpcoes = 0
                        mesAtualSomaTributavelDayTradeVista = 0
                        mesAtualSomaTributavelDayTradeOpcoes = 0

                        mesAtual = mes

                    if r.tipoMercado == 'VISTA':
                        mesAtualSomaTributavelVista += r.resultadoTributavel
                        mesAtualSomaTributavelDayTradeVista += r.resultadoTributavelDayTrade
                    elif 'OPCAO' in r.tipoMercado:
                        mesAtualSomaTributavelOpcoes += r.resultadoTributavel
                        mesAtualSomaTributavelDayTradeOpcoes += r.resultadoTributavelDayTrade
                    else:
                        raise Exception(
                            f'tipoMercado não esperado: {r.tipoMercado}')
                    
                somaTributavel += r.resultadoTributavel
                somaTributavelDayTrade += r.resultadoTributavelDayTrade

        if somaTributavel > 0 or somaTributavelDayTrade > 0:
            impostos.append(ImpostoMes.__getImpostoMes(
                mesAtual, somaTributavel, somaTributavelDayTrade))

        print(mesAtual)
        print(f'{mesAtual}: Ações: R$ {round(mesAtualSomaTributavelVista, 2)} Ações Day Trade: R$ {
            round(mesAtualSomaTributavelDayTradeVista, 2)}')
        print(f'{mesAtual}: Opções: R$ {round(mesAtualSomaTributavelOpcoes, 2)} Opções Day Trade: R$ {
            round(mesAtualSomaTributavelDayTradeOpcoes, 2)}')
        print('[ACUMULADO]')
        print(f'Normal: R$ {round(somaTributavel, 2)}')
        print(f'Day Trade: R$ {round(somaTributavelDayTrade, 2)}')
        print('-'*10)

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
