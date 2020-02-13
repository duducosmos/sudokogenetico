from numpy import zeros, array, split, hsplit, where, count_nonzero, concatenate
from numpy import isin
from numpy.random import randint, choice, shuffle
import random


class Sudoku:
    def __init__(self):

        self._sudoku = None
        self.solucao = None
        self._possiveis = array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        self._quadrante_linha = {0:0, 1:3, 2:6}
        self._quadrante_coluna = {0:0, 1:3, 2:6}
        self._quadrantes = [[0,0], [0,1], [0, 2],
                            [1,0], [1,1], [1, 2],
                            [2,0], [2,1], [2, 2]
                            ]
        self._perda = -1
        self._bonus = 1

    @property
    def perda(self):
        return self._perda

    @property
    def bonus(self):
        return self._bonus

    def _get_sudoku(self):
        return self._sudoku

    def _set_sudoku(self, sudoku):
        self._sudoku = sudoku
        self.solucao = sudoku.copy()

    def numero_de_casas_vazias(self):
        return count_nonzero(self.solucao == 0)

    def quadrante(self, x, y):
        tmp = split(self.solucao, 3)
        quad = []

        for sub in tmp:
            sub2 = split(sub, 3, axis=1)
            tmp2 = []
            for sub3 in sub2:
                tmp2.append(sub3.tolist())
            quad.append(tmp2)

        quad = array(quad)
        subquad = quad[x, y]
        return subquad

    def _numeros_no_quadrante(self, x, y):
        quadrante = self.quadrante(x, y)
        l0 = self._quadrante_linha[x]
        c0 = self._quadrante_coluna[y]

        linhas, colunas = where(quadrante == 0)
        if linhas.size != 0:
            linhas = linhas + l0
            colunas = colunas + c0
            testar = self._possiveis[~isin(self._possiveis, quadrante)]

            ij = list(zip(linhas, colunas))
            return testar, ij
        return None, None

    def ilegal_no_quadrante(self, x, y):
        """
        Verifica se em algum quadrante existe posição vazia que não pode ser
        preenchida por um número.
        """
        testar, ij = self._numeros_no_quadrante(x, y)
        if testar is not None:

            invalidas = 0

            for i, j in ij:
                tmp = 0
                for numero in testar:
                    a = count_nonzero(self.solucao[i, :] == numero)
                    b = count_nonzero(self.solucao[:, j] == numero)
                    if a != 0 or b != 0:
                        tmp += 1

                if tmp == testar.size:
                    invalidas += 1

            return invalidas
        return 0

    def total_ilegais(self):
        ilegais = sum([self.ilegal_no_quadrante(xy[0], xy[1])
                       for xy in self._quadrantes])
        return ilegais

    def verificar(self, numero, linha, coluna):
        if numero < 1 or numero > 9:
            return -1000000000

        valorlc = self._perda * count_nonzero(self.solucao[linha,:] == numero)
        valorlc += self._perda * count_nonzero(self.solucao[:,coluna] == numero)
        valorlc += self.verificar_repeticoes(numero, linha, coluna, valorlc)

        if valorlc > 0:
            self.solucao[linha, coluna] = numero
            return self._bonus
        return valorlc

    def verificar_repeticoes(self, numero, linha, coluna, valorlc):

        x, y = (int(linha / 3), int(coluna / 3))
        subquad = self.quadrante(x, y)
        repeticoes = count_nonzero(subquad == numero)
        nzeros = count_nonzero(subquad == 0)

        if repeticoes != 0:
            return self._perda * 3

        if valorlc < 0:
            sudo_linha = count_nonzero(self.sudoku[linha,:] == numero)
            sudo_coluna = count_nonzero(self.sudoku[:,coluna] == numero)

            if sudo_linha != 0 or sudo_coluna != 0:
                return self._perda * 3
            return self._perda

        return self._bonus

    def tentar_preencher(self, backtracking=False):
        if self.solucao is not None:
            original = self.solucao.copy()
            linha, coluna = where(self.solucao==0)
            licol = list(zip(linha, coluna))
            n = len(licol)
            l = 0
            while l < n:
                encaixou = 0
                i, j = licol[l][0], licol[l][1]
                inicio = self.solucao[i, j]
                self.solucao[i, j] = 0
                for numero in range(inicio + 1,10):
                    encaixou = self.verificar(numero, i, j)
                    if encaixou > 0:
                        break
                if encaixou > 0:
                    l = l + 1
                else:
                    if backtracking is True:
                        l = l -1
                    else:
                        break

            tilegais =  self.total_ilegais()
            self.solucao, original = original, self.solucao
            return n - l, tilegais, original
        return None, None, None

    sudoku = property(_get_sudoku, _set_sudoku)
