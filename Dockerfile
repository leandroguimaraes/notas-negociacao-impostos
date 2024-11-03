FROM python:3

WORKDIR /usr/src/app

RUN pip install jsonpickle
RUN pip install git+https://github.com/leandroguimaraes/notas-negociacao.git
