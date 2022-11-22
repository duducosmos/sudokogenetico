#!/usr/bin/env python3.6
# -*- Coding: UTF-8 -*-
"""
Usa algoritmo genético para resolver o sudoku.
"""
import sys
from numpy import loadtxt

from sudoku import Sudoku
from solucionarsudoku import SolucionarSudoku

jg = sys.argv[1]
jogo = loadtxt(jg, dtype=int, delimiter=",")
sudoku = Sudoku()
sudoku.sudoku = jogo
solucionarsudoku = SolucionarSudoku(sudoku, 32, 300)
solucionarsudoku.inicializar(pmut=0.01, pcruz=0.6, epidemia=500)
solucionarsudoku.solucionar()
