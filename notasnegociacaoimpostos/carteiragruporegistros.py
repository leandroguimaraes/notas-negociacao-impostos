from notasnegociacaoimpostos.carteiraregistro import CarteiraRegistro
from notasnegociacaoimpostos.negociorealizadoimpostos import NegocioRealizadoImpostos, NotaNegociacaoNegocioImpostos
import datetime
import copy


class CarteiraGrupoRegistros:
    data: datetime.date
    registros: list[CarteiraRegistro]

    def __init__(self):
        self.registros = []

    @staticmethod
    def getCarteiraGrupoRegistros(notasNegociacao: list[NotaNegociacaoNegocioImpostos], notasExtras: list[NotaNegociacaoNegocioImpostos] = []) -> list['CarteiraGrupoRegistros']:
        notasNegociacao = notasNegociacao + notasExtras
        notasNegociacao.sort(key=lambda n: n.dataPregao)

        carteira: list[CarteiraGrupoRegistros] = []
        for nota in notasNegociacao:
            carteira = CarteiraGrupoRegistros.__atualizarPosicoesOpcoes(
                carteira, nota.dataPregao)
            grupo = next((grupo for grupo in carteira if CarteiraGrupoRegistros.__strToDate(grupo.data) ==
                          CarteiraGrupoRegistros.__strToDate(nota.dataPregao)), CarteiraGrupoRegistros())

            if (not hasattr(grupo, 'data')):
                grupo.data = CarteiraGrupoRegistros.__strToDate(
                    nota.dataPregao)

                if (len(carteira) > 0):
                    grupo.registros = copy.deepcopy(carteira[-1].registros)
                    registrosAtualizados: list[CarteiraRegistro] = []
                    for r in grupo.registros:
                        if r.qnt != 0:
                            r.resultadoTributavel = 0
                            r.resultadoTributavelDayTrade = 0

                            registrosAtualizados.append(r)

                    grupo.registros = registrosAtualizados

                carteira.append(grupo)

            grupoData = CarteiraGrupoRegistros.__strToDate(grupo.data)
            grupo.registros = [r for r in grupo.registros if (not hasattr(
                r, 'prazo')) or (hasattr(r, 'prazo') and r.prazo >= grupoData)]

            # TODO: consolidar nota.negociosRealizados melhora?
            for i, n in enumerate(nota.negociosRealizados):
                especificacaoTitulo = CarteiraGrupoRegistros.__getEspecificacaoNormalizada(
                    n)

                registro = next((registro for registro in grupo.registros if registro.descricao ==
                                especificacaoTitulo), CarteiraRegistro())

                # TODO: melhorar identificação de day-trade
                isDayTrade = False
                if len(list(filter(lambda nr: CarteiraGrupoRegistros.__getEspecificacaoNormalizada(nr) == CarteiraGrupoRegistros.__getEspecificacaoNormalizada(n) and nr.compraVenda != n.compraVenda, nota.negociosRealizados))) > 0:
                    isDayTrade = True

                if (not hasattr(registro, 'descricao')):
                    registro.descricao = especificacaoTitulo
                    grupo.registros.append(registro)

                if (n.tipoMercado in ['EXERC OPC COMPRA', 'EXERC OPC VENDA']):
                    registro.tipoMercado = 'VISTA'
                else:
                    registro.tipoMercado = n.tipoMercado

                if (n.tipoMercado in ['OPCAO DE COMPRA', 'OPCAO DE VENDA']):
                    registro.prazo = CarteiraGrupoRegistros.__convertPrazoToDate(
                        n.prazo)

                qnt = n.quantidade if n.debitoCredito == 'D' else n.quantidade * -1

                if CarteiraGrupoRegistros.__isReducaoPosicao(registro.qnt, qnt):
                    resultadoTributavel = (
                        registro.precoMedio * qnt * -1) + CarteiraGrupoRegistros.__getValorLiquido(n)

                    if isDayTrade:
                        registro.resultadoTributavelDayTrade += resultadoTributavel
                    else:
                        registro.resultadoTributavel += resultadoTributavel

                qntTotal = registro.qnt + qnt
                if (qntTotal != 0) and (not CarteiraGrupoRegistros.__isReducaoPosicao(registro.qnt, qnt)):
                    if (n.valorOperacaoAjuste == 0):
                        registro.precoMedio = (
                            (registro.precoMedio * registro.qnt) + (n.precoAjuste * n.quantidade)) / qntTotal
                    else:
                        registro.precoMedio = (
                            (registro.precoMedio * registro.qnt) + CarteiraGrupoRegistros.__getValorLiquido(n)) / qntTotal

                registro.qnt += qnt

        return carteira

    @staticmethod
    def __atualizarPosicoesOpcoes(carteira: list['CarteiraGrupoRegistros'], dataRef: datetime.date) -> list['CarteiraGrupoRegistros']:
        dataRef = CarteiraGrupoRegistros.__strToDate(dataRef)

        if (len(carteira) > 0):
            hasOpcoesVencidasCheck = False
            for registro in carteira[-1].registros:
                if CarteiraGrupoRegistros.__hasOpcoesVencidas(registro, dataRef):
                    hasOpcoesVencidasCheck = True
                    break

            if (hasOpcoesVencidasCheck):
                vencidaEm: datetime.datetime.date
                grupo = copy.deepcopy(carteira[-1])
                for registro in grupo.registros:
                    if CarteiraGrupoRegistros.__hasOpcoesVencidas(registro, dataRef):
                        if hasattr(registro, 'prazo'):
                            # opções vencidas
                            vencidaEm = CarteiraGrupoRegistros.__strToDate(
                                registro.prazo)
                        else:
                            # opções exercidas
                            vencidaEm = dataRef

                        # TODO: verificar se é day trade
                        registro.resultadoTributavel = registro.qnt * registro.precoMedio

                        registro.qnt = 0

                grupo.data = CarteiraGrupoRegistros.__strToDate(vencidaEm)
                if carteira[-1].data != grupo.data:
                    carteira.append(grupo)
                else:
                    carteira[-1] = grupo

        return carteira

    @staticmethod
    def __getEspecificacaoNormalizada(n: NegocioRealizadoImpostos) -> str:
        especificacaoTitulo = n.especificacaoTitulo
        if (n.tipoMercado == 'VISTA'):
            especificacaoTitulo = CarteiraGrupoRegistros.__normalizarEspecificacaoTitulo(
                n.especificacaoTitulo)
        elif (n.tipoMercado in ['OPCAO DE COMPRA', 'OPCAO DE VENDA']):
            especificacaoTitulo = CarteiraGrupoRegistros.__normalizarEspecificacaoOpcao(
                n.especificacaoTitulo)
        elif (n.tipoMercado in ['EXERC OPC COMPRA', 'EXERC OPC VENDA']):
            especificacaoTitulo = CarteiraGrupoRegistros.__converteDescOpcaoAcao(
                n.especificacaoTitulo)

        return especificacaoTitulo

    @staticmethod
    def __normalizarEspecificacaoTitulo(especificacaoTitulo: str) -> str:
        if (especificacaoTitulo[-7:] == ' CI ERS'):
            especificacaoTitulo = especificacaoTitulo[:len(
                especificacaoTitulo) - 7]

        if (especificacaoTitulo[-6:] == ' CI ER'):
            especificacaoTitulo = especificacaoTitulo[:len(
                especificacaoTitulo) - 6]

        if (especificacaoTitulo[-3:] in [' N1', ' N2', ' NM']):
            especificacaoTitulo = especificacaoTitulo[:len(
                especificacaoTitulo) - 3]

        if (especificacaoTitulo[-3:] in [' EJ', ' ED']):
            especificacaoTitulo = especificacaoTitulo[:len(
                especificacaoTitulo) - 3]

        return especificacaoTitulo

    @staticmethod
    def __normalizarEspecificacaoOpcao(especificacaoOpcao: str) -> str:
        result = especificacaoOpcao.split()
        if len(result) == 5:
            result = result[:-1]
        elif len(result) > 5:
            raise ValueError(f'Especificação de opção não esperada: {
                             especificacaoOpcao}')

        return ' '.join(result)

    @staticmethod
    def __converteDescOpcaoAcao(descOpcao: str) -> str:
        convertDict = {
            'ITSA': 'ITAUSA PN',
            'PETR': 'PETROBRAS PN',
            'RENT': 'LOCALIZA ON',
            'VALE': 'VALE ON',
            'WEGE': 'WEG ON'
        }

        if (descOpcao[:4] not in convertDict):
            raise ValueError(f'Descrição de opção não esperada: {descOpcao}')

        return convertDict[descOpcao[:4]]

    @staticmethod
    def __convertPrazoToDate(prazo: str) -> datetime.date:
        data = datetime.datetime.strptime(prazo, "%m/%y").date()

        # o 15o é o mais baixo terceiro dia do mês
        terceiro = datetime.date(int(data.strftime('%Y')),
                                 int(data.strftime('%m')), 15)
        # qual dia da semana é o 15o?
        w = terceiro.weekday()

        # até ABR/21 o vencimento de opções acontecia na terceira segunda-feira do mês
        # de MAI/21 em diante, passou a acontecer na terceira sexta-feira
        diaProcurado = 0
        if (data.strftime('%Y%m') <= '202104'):
            # terceira segunda
            diaProcurado = 0
        else:
            # terceira sexta
            diaProcurado = 4

        if (w != diaProcurado):
            terceiro = terceiro.replace(day=(15 + (diaProcurado - w) % 7))

        return terceiro

    @staticmethod
    def __isReducaoPosicao(qntAtual: int, qntNova: int) -> bool:
        return (qntAtual > 0 and qntNova < 0) or (qntAtual < 0 and qntNova > 0)

    @staticmethod
    def __getValorLiquido(n: NegocioRealizadoImpostos) -> float:
        return n.resumoFinanceiro.clearing.totalCBLC + n.resumoFinanceiro.bolsa.totalBovespaSoma + n.resumoFinanceiro.custosOperacionais.totalCustosDespesas

    @staticmethod
    def __hasOpcoesVencidas(registro: CarteiraRegistro, dataRef: datetime.date) -> bool:
        return (registro.tipoMercado in ['EXERC OPC COMPRA', 'EXERC OPC VENDA']) \
            or (registro.tipoMercado in ['OPCAO DE COMPRA', 'OPCAO DE VENDA'] and registro.qnt != 0 and dataRef >= registro.prazo)

    @staticmethod
    def __strToDate(date) -> datetime.date:
        if (type(date) is str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        return date
