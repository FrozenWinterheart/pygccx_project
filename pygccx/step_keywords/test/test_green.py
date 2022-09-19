'''
Copyright Matthias Sedlmaier 2022
This file is part of pygccx.

pygccx is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

pygccx is distributed in the hope that it will 
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pygccx.  
If not, see <http://www.gnu.org/licenses/>.
'''

from unittest import TestCase

from pygccx.step_keywords import Green
from pygccx.enums import ESolvers
from pygccx.protocols import IKeyword

class TestGreen(TestCase):

    def test_is_IKeyword(self):
        g = Green()
        self.assertTrue(isinstance(g, IKeyword))

    def test_default(self):
        g = Green()
        known = '*GREEN\n'
        self.assertEqual(str(g), known)

    def test_solver(self):
        g = Green(solver=ESolvers.SPOOLES)
        known = '*GREEN,SOLVER=SPOOLES\n'
        self.assertEqual(str(g), known)

        g = Green(solver=ESolvers.ITERATIVE_SCALING)
        known = '*GREEN,SOLVER=ITERATIVE SCALING\n'
        self.assertEqual(str(g), known)

        g = Green(solver=ESolvers.ITERATIVE_CHOLESKY)
        known = '*GREEN,SOLVER=ITERATIVE CHOLESKY\n'
        self.assertEqual(str(g), known)

        g = Green(solver=ESolvers.PASTIX)
        known = '*GREEN,SOLVER=PASTIX\n'
        self.assertEqual(str(g), known)

    def test_storage(self):
        g = Green(storage=True)
        known = '*GREEN,STORAGE=YES\n'
        self.assertEqual(str(g), known)
