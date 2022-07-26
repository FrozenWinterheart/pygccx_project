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

from dataclasses import dataclass

number = int|float
@dataclass(frozen=True, slots=True)
class Friction:

    """
    Class to define the friction behavior of a surface interaction 

    Args:
        mue: Friction coefficient > 0
        lam: Stick-slope in force/volume > 0
        name: Optional. Name of this instance
        desc: Optional. A short description of this instance. This is written to 
                the ccx input file.
    """
    mue:number
    """Friction coefficient > 0"""
    lam:number
    """Stick-slope in force/volume > 0"""
    name:str = ''
    """Name of this instance"""
    desc:str = ''
    """A short description of this instance. This is written to the ccx input file."""

    def __post_init__(self):
        if self.mue <= 0:
            raise ValueError(f'mue must be greater than 0, got {self.mue}')
        if self.lam <= 0:
            raise ValueError(f'lam must be greater than 0, got {self.lam}')

    def __str__(self):
        s = '*FRICTION\n'
        s += f'{self.mue},{self.lam}\n'
        return s