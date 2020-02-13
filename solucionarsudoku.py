#!/usr/bin/env python3.6
# -*- Coding: UTF-8 -*-
"""
Usa algoritmo genético para resolver o sudoku.
"""

import time

from numpy import array, count_nonzero, where, hsplit, concatenate, exp

from pygenec.populacao import Populacao
from pygenec.selecao.torneio import Torneio
from pygenec.cruzamento.embaralhamento import Embaralhamento
from pygenec.mutacao.sequenciareversa import SequenciaReversa
from pygenec.evolucao import Evolucao

from pygenec.tools import bcolors, binarray2int


class SolucionarSudoku:
    """
    SolucionarSudoku: Tenta encontrar a solução do
                      sudoku usando algoritmo genético.

    Entrada:
        sudoku: objeto do tipo Sudoku.
        bits: Número de bits por cromossomo.
        tamanho_populacao: Tamanho da população a ser usada na busca.
    """

    def __init__(self, sudoku, bits, tamanho_populacao):
        """Constrututor da classe."""
        self.sudoku = sudoku
        self.bits = bits
        self.cromossomos = self.sudoku.numero_de_casas_vazias()
        self.tamanho_populacao = tamanho_populacao
        self.populacao = None
        self.cruzamento = None
        self.mutacao = None
        self.evolucao = None

    def inicializar(self, pmut=0.5, pcruz=0.1, epidemia=50, elitista=True):
        """Inicializa o algoritmo genético para."""
        tamanho = int(0.1 * self.tamanho_populacao)
        genes = self.bits * self.cromossomos

        self.populacao = Populacao(self.avaliacao,
                                   genes,
                                   self.tamanho_populacao)

        self.selecao = Torneio(self.populacao, tamanho=tamanho)
        self.cruzamento = Embaralhamento(self.tamanho_populacao)
        self.mutacao = SequenciaReversa(pmut=pmut)

        self.evolucao = Evolucao(self.populacao,
                                 self.selecao,
                                 self.cruzamento,
                                 self.mutacao)

        self.evolucao.nsele = tamanho
        self.evolucao.pcruz = pcruz
        self.evolucao.epidemia = epidemia
        self.evolucao.manter_melhor = elitista

    def valores(self, populacao):
        """Converte cromossomos em números inteiros entre 1 e 9."""
        bx = hsplit(populacao, self.cromossomos)
        const = 2 ** self.bits - 1
        const = (10 - 1) / const
        x = [1 + const * binarray2int(xi) for xi in bx]
        x = concatenate(x).T.astype(int)
        return x

    def avaliacao(self, populacao):
        """Função de Avalização da população."""
        linhas, colunas = where(self.sudoku.sudoku == 0)
        x = self.valores(populacao)

        peso = []
        for k in range(len(populacao)):
            self.sudoku.solucao = self.sudoku.sudoku.copy()
            y = x[k, :].copy()
            data = list(zip(y, linhas, colunas))

            tmp = 10 * sum([self.sudoku.verificar(num, i, j)
                            for num, i, j in data
                            ])

            tmp += 100000 * self.sudoku.perda * self.sudoku.total_ilegais()

            profundidade, ilegais, resposta = self.sudoku.tentar_preencher()
            if profundidade is not None:
                objetivo = (profundidade + ilegais) / \
                    (1e-3 * profundidade + 1.0)
                objetivo += (profundidade + ilegais ** 3) / (ilegais + 1.0)
                tmp += self.sudoku.perda * int(1000 * objetivo)

            peso.append(tmp)

        peso = array(peso)
        return peso

    def _verificar(self):
        """Verifica se já encontrou o ramo correto de solução."""
        self.sudoku.solucao = self.sudoku.sudoku.copy()
        v = self.valores(self.populacao.populacao)[-1]
        linha, coluna = where(self.sudoku.solucao == 0)
        data = list(zip(v, linha, coluna))
        for n, k, j in data:
            self.sudoku.verificar(n, k, j)
        return self.sudoku.tentar_preencher()

    def _exibir_resposta(self, convergencia, ilegais, resposta, valor, vmin):
        """Exibe na tela a resposta atual."""
        print("Geração: {}".format(self.evolucao.geracao))

        print("Para Superficie:{0}, Ilegais:{1}".format(convergencia,
                                                        ilegais))
        if convergencia == 0:
            tmp = resposta.astype(str)
        else:
            tmp = self.sudoku.solucao.astype(str)

        print(self.cromossomos - convergencia, self.cromossomos, valor, vmin)
        linha, coluna = where(self.sudoku.sudoku == 0)

        for k, j in zip(linha, coluna):
            if tmp[k, j] != "0":
                tmp[k, j] = "{0}{1}{2}".format(bcolors.WARNING,
                                               tmp[k, j],
                                               bcolors.ENDC)
        tmp2 = ""

        for l in range(tmp.shape[0]):
            tmp2 += "|" + ", ".join(tmp[l]) + "|\n"
        print(tmp2)
        print("\n")

    def solucionar(self, reiniciar_apos=2000):
        """Realiza a busca pela solução do Sudoku."""
        convergencia = 10000
        sem_mudancas = 0
        ultima_mudanca = -10
        t0 = time.time()
        solucoes_ruins = []

        while convergencia > 0:
            valor, vmin = self.evolucao.evoluir()

            convergencia, ilegais, resposta = self._verificar()

            self._exibir_resposta(convergencia, ilegais, resposta, valor, vmin)


            if len(solucoes_ruins) != 0:
                if self.populacao.populacao[-1].tolist() in solucoes_ruins:
                    print("Repetindo Minimo Local: Reiniciar")
                    self.populacao.gerar_populacao()

            if ultima_mudanca == convergencia:
                sem_mudancas += 1
                if sem_mudancas == reiniciar_apos:
                    print("Minimo Local, Reiniciar")
                    solucoes_ruins.append(
                        self.populacao.populacao[-1].tolist())
                    self.populacao.gerar_populacao()
                    sem_mudancas = 0
            else:
                sem_mudancas = 0

            ultima_mudanca = convergencia


            if convergencia == 0:
                break

        print("Tempo: ", (time.time() - t0) / 60)
        print("\n")
