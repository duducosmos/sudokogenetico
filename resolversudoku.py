#!/usr/bin/env python3.6
# -*- Coding: UTF-8 -*-
"""
Usa algoritmo genético para resolver o sudoku.
"""
import sys
from numpy import loadtxt

from sudoku import Sudoku
from solucionarsudoku import SolucionarSudoku

jogo = loadtxt(sys.argv[1], dtype=int, delimiter=",")
sudoku = Sudoku()
sudoku.sudoku = jogo
solucionarsudoku = SolucionarSudoku(sudoku, 32, 500)
solucionarsudoku.inicializar(epidemia=50)
solucionarsudoku.solucionar()
