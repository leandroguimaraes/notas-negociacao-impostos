import datetime
from dataclasses import dataclass


@dataclass
class CarteiraRegistro:
    tipoMercado: str
    qnt: int
    descricao: str
    precoMedio: float
    resultadoTributavel: float
    resultadoTributavelDayTrade: float
    prazo: datetime.date

    def __init__(self):
        self.qnt = 0
        self.precoMedio = 0
        self.resultadoTributavel = 0
        self.resultadoTributavelDayTrade = 0
