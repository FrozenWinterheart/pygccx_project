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
from typing import Optional
from enums import ESetTypes
from protocols import IModelFeature, ISet

@dataclass(frozen=True, slots=True)
class SolidSection:
    elset:ISet
    material:IModelFeature
    orientation:Optional[IModelFeature] = None
    name:str = ''
    desc:str = ''
    
    def __post_init__(self):
        if self.elset.type != ESetTypes.ELEMENT:
            raise ValueError(f'set_type of elset must be ELEMENT, got {self.elset.type}')

    def __str__(self):
        s = f'*SOLID SECTION,MATERIAL={self.material.name},ELSET={self.elset.name}'
        s += f',ORIENTATION={self.orientation.name}\n' if self.orientation else '\n'
        return s