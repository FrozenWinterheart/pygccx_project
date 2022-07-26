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

@dataclass(frozen=True, slots=True)
class SurfaceInteraction:

    """
    Class to define the start of a surface interaction

    Args:
        name: Name of this surface interaction up to 80 characters
        desc: Optional. A short description of this instance. This is written to 
                the ccx input file.
    """
    name:str
    desc:str = ''

    def __post_init__(self):
        if len(self.name) > 80:
            raise ValueError(f'name can only contain up to 80 characters, got {len(self.name)}')


    def __str__(self):
        return f'*SURFACE INTERACTION,NAME={self.name}\n'