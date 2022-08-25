"""
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

================================================================================

Static contact analysis example of a crowned roller pressed against a flat plate.
The roller has the dimensions D = 20mm, L = 20mm.
The crowning profile has the form:
p(x) = (e**(|x|) - |x| - 1) / (e**(L/2) - L/2 - 1) * p_max
Roller and plate are made out of steel. E = 210000N/mm², mue = 0.3

The roller is modeled as a rigid body, so the Emodule of the plate must be halfed.
See https://elib.dlr.de/12219/1/diss_041005_duplex_rgb.pdf page 45, eq. 3.12

The analysis consists of two load steps.
Step 1: Load of 40_000N is applied at center of roller (no tilting)
        Analytic solution:
        p_h = 271 * sqrt(F / (D * L)) 
            = 271 * sqrt(40_000N / (20mm * 20mm)) 
            = 2_710N/mm²
        Due to the crowning, real pressure must be higher.
Step 2: Load of 40_000N is applied 10% (2mm) out of center. So the pressure on one side 
        of the roller is higher.

All bodies are meshed with linear C3D8I elements.
Symmetry of the model is used. So only one half of the roller and plate is modeled

After the analysis has run, the pressure along the roller axis is plotted for both
steps

used model keywords:
Boundary, RigidBody, Material, Elastic, SolidSection
Contact is generated by func make_contact which returns
(SurfaceInteraction, SurfaceBehavior, ContactPair)

used step keywords:
Step, Static, Cload, NodeFile, ElFile, ContactFile

"""

import sys, os
os.chdir(sys.path[0])
sys.path += ['../../', '../../pygccx']

import numpy as np
from matplotlib import pyplot as plt

from pygccx import model as ccx_model
from pygccx import model_keywords as mk
from pygccx import step_keywords as sk
from pygccx import enums

# change this paths to your location of ccx and cgx
CCX_PATH = os.path.join('../../', 'executables', 'calculix_2.19_4win', 'ccx_static.exe')
CGX_PATH = os.path.join('../../', 'executables', 'calculix_2.19_4win', 'cgx_GLUT.exe')

def main():
    with ccx_model.Model(CCX_PATH, CGX_PATH) as model:
        model.jobname = 'crowned_roller'
        gmsh = model.get_gmsh()
        # build geometry and mesh in separate function
        build_mesh_in_gmsh(gmsh) # type: ignore
        # model.show_gmsh_gui()
        model.update_mesh_from_gmsh()
        mesh = model.mesh
        trans_pilot = mesh.add_node((0,10,0))
        rot_pilot = mesh.add_node((0,10,0))

        plate = mesh.get_el_set_by_name('PLATE')
        roller = mesh.get_el_set_by_name('ROLLER')
        target = mesh.get_node_set_by_name('TARGET')
        contact = mesh.get_node_set_by_name('CONTACT')
        fix_z_sym = mesh.get_node_set_by_name('FIX_Z_SYM')
        fix_y = mesh.get_node_set_by_name('FIX_Y')
        fix_x = mesh.get_node_set_by_name('FIX_X')

        model.add_model_keywords(
            mk.RigidBody(roller, trans_pilot, rot_pilot)
        )

        boundary = mk.Boundary(fix_z_sym,3)
        boundary.add_condition(fix_y,2)
        boundary.add_condition(fix_x,1)
        boundary.add_condition(rot_pilot,1,2)
        boundary.add_condition(trans_pilot,1)
        boundary.add_condition(trans_pilot,3)
        model.add_model_keywords(boundary)

        target_surf = mesh.add_surface_from_node_set('TARGET_SURF', target, enums.ESurfTypes.EL_FACE)
        contact_surf = mesh.add_surface_from_node_set('CONTACT_SURF', contact, enums.ESurfTypes.EL_FACE)
        contact_keywords = mk.make_contact('ROLLER_CONTACT', enums.EContactTypes.NODE_TO_SURFACE,
                                            target_surf, contact_surf, 
                                            enums.EPressureOverclosures.LINEAR,
                                            adjust=1e-5,
                                            k=210000*50, sig_inf = .1)

        model.add_model_keywords(*contact_keywords)

        mat = mk.Material('STEEL')
        el = mk.Elastic((210000/2, 0.3))
        sos1 = mk.SolidSection(plate, mat)
        sos2 = mk.SolidSection(roller, mat)
        model.add_model_keywords(mat,el,sos1, sos2)

        step_1 = sk.Step()
        step_1.add_step_keywords(
            sk.Static(init_time_inc=0.01),
            sk.Cload(trans_pilot,2,-20000),
            sk.NodeFile([enums.ENodeFileResults.U]),
            sk.ElFile([enums.EElFileResults.S]),
            sk.ContactFile([enums.EContactFileResults.CDIS]),
                        sk.ContactPrint([enums.EContactPrintResults.CDIS,
                            enums.EContactPrintResults.CELS,
                            enums.EContactPrintResults.CSTR])
        )
        step_2 = sk.Step()
        step_2.add_step_keywords(
            sk.Static(),
            sk.Cload(rot_pilot,3,-20000 * 2), # note cload of step 1 is still active
            sk.NodeFile([enums.ENodeFileResults.U]),
            sk.ElFile([enums.EElFileResults.S]),
            sk.ContactFile([enums.EContactFileResults.CDIS]),
        )
        model.add_steps(step_1, step_2)
        model.show_model_in_cgx()
        model.solve()
        model.show_results_in_cgx()

        # POST PRO
        line_set = mesh.get_node_set_by_name('CONTACT_LINE')
        line_nodes = np.array(mesh.get_nodes_by_ids(*line_set.ids))
        frd_result = model.get_frd_result()
        cont_res_1 = frd_result.get_result_set_by_entity_and_time(enums.EFrdEntities.CONTACT, 1)
        cont_res_2 = frd_result.get_result_set_by_entity_and_time(enums.EFrdEntities.CONTACT, 2)
        if cont_res_1 and cont_res_2:
            pres_1 = cont_res_1.get_values_by_ids(line_set.ids)
            pres_2 = cont_res_2.get_values_by_ids(line_set.ids)

            plt.plot(line_nodes[:,0], pres_1[:,3], '.', label='step 1')
            plt.plot(line_nodes[:,0], pres_2[:,3], '.', label='step 2')
            plt.legend()
            plt.title('Pressure along roller length')
            plt.xlabel('roller length [mm]')
            plt.ylabel('pressure [MPa')
            plt.show()


def build_mesh_in_gmsh(gmsh:ccx_model._gmsh):  # type: ignore


    # make the roller
    #----------------------------------------------------------------------
    # x and y coordinates of the crowning profile
    x_p = np.linspace(-10,10,51)
    a_x_p = np.abs(x_p)
    y_p = (np.exp(a_x_p) - a_x_p - 1) / (np.exp(10) - 10 - 1) * 0.015 # type: ignore
    # make points
    spl_pnts = [gmsh.model.geo.addPoint(x,y,0) for x, y in zip(x_p, y_p)]
    pr1 = gmsh.model.geo.addPoint(-10, .5, 0)
    pr2 = gmsh.model.geo.addPoint(10, .5, 0)
    # make lines
    lr1 = gmsh.model.geo.addSpline(spl_pnts)
    lr2 = gmsh.model.geo.addLine(spl_pnts[-1], pr2)
    lr3 = gmsh.model.geo.addLine(pr2, pr1)
    lr4 = gmsh.model.geo.addLine(pr1, spl_pnts[0])
    # make surface
    wr1 = gmsh.model.geo.addCurveLoop([lr1, lr2, lr3, lr4])
    sr1 = gmsh.model.geo.addPlaneSurface([wr1])
    gmsh.model.geo.synchronize()
    # mesh constraint for regular hex mesh
    gmsh.model.geo.mesh.setTransfiniteCurve(lr1, 51, "Bump", 1)
    gmsh.model.geo.mesh.setTransfiniteCurve(lr2, 2)
    gmsh.model.geo.mesh.setTransfiniteCurve(lr3, 51, "Bump", 1)
    gmsh.model.geo.mesh.setTransfiniteCurve(lr4, 2)
    gmsh.model.geo.mesh.setTransfiniteSurface(sr1)
    gmsh.model.geo.mesh.setRecombine(2, sr1)
    # revolved hex mesh 
    # fine mesh in contact area
    out = gmsh.model.geo.revolve([(2,sr1)], -10,10,0, 1,0,0, angle=0.05, numElements=[10], recombine=True)
    # coarse meh with progression
    heights = np.linspace(0,1,30)[1:]**1.6
    gmsh.model.geo.revolve([out[0]], -10,10,0, 1,0,0, angle=np.pi/6-0.05,heights=heights, numElements=np.ones_like(heights), recombine=True)

    # make the plate
    #----------------------------------------------------------------------
    # make points
    ph1 = gmsh.model.geo.addPoint(-15, 0, 0)
    ph2 = gmsh.model.geo.addPoint(-15, 0, -0.5)
    ph3 = gmsh.model.geo.addPoint(-15, -0.5, -0.5)
    ph4 = gmsh.model.geo.addPoint(-15, -0.5, 0)
    ph5 = gmsh.model.geo.addPoint(-15, 0, -5)
    ph6 = gmsh.model.geo.addPoint(-15, -5, -5)
    ph7 = gmsh.model.geo.addPoint(-15, -5, 0)

    # # make lines
    lh1 = gmsh.model.geo.addLine(ph1, ph2)
    lh2 = gmsh.model.geo.addLine(ph2, ph3)
    lh3 = gmsh.model.geo.addLine(ph3, ph4)
    lh4 = gmsh.model.geo.addLine(ph4, ph1)
    lh5 = gmsh.model.geo.addLine(ph2, ph5)
    lh6 = gmsh.model.geo.addLine(ph5, ph6)
    lh7 = gmsh.model.geo.addLine(ph6, ph3)
    lh8 = gmsh.model.geo.addLine(ph6, ph7)
    lh9 = gmsh.model.geo.addLine(ph7, ph4)

    # make surfaces
    wh1 = gmsh.model.geo.addCurveLoop([lh1, lh2, lh3, lh4])
    sh1 = gmsh.model.geo.addPlaneSurface([wh1])
    wh2 = gmsh.model.geo.addCurveLoop([lh5, lh6, lh7, -lh2])
    sh2 = gmsh.model.geo.addPlaneSurface([wh2])
    wh3 = gmsh.model.geo.addCurveLoop([-lh7, lh8, lh9, -lh3])
    sh3 = gmsh.model.geo.addPlaneSurface([wh3])

    gmsh.model.geo.mesh.setTransfiniteCurve(lh1, 10)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh2, 10)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh3, 10)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh4, 10)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh5, 10, coef=1.4)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh6, 10)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh7, 10, coef=1/1.4)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh8, 10)
    gmsh.model.geo.mesh.setTransfiniteCurve(lh9, 10, coef=1/1.4)

    for s in [sh1, sh2, sh3]:
        gmsh.model.geo.mesh.setTransfiniteSurface(s)
        gmsh.model.geo.mesh.setRecombine(2, s)

    heights = np.linspace(0,1,11)**(1/1.3)
    out = gmsh.model.geo.extrude([(2,sh1),(2,sh2),(2,sh3)],5,0,0, 
                            numElements=np.ones_like(heights), 
                            heights=heights[1:], recombine=True)
    out = gmsh.model.geo.extrude(out[::6],20,0,0, 
                            [50], recombine=True)
    heights = (1-heights)[::-1]       
    out = gmsh.model.geo.extrude(out[::6],5,0,0, 
                            numElements=np.ones_like(heights), 
                            heights=heights[1:], recombine=True)

    # physical Groups
    gmsh.model.add_physical_group(3, [1,2], name='ROLLER')
    gmsh.model.add_physical_group(3, range(3,12), name='PLATE')
    gmsh.model.add_physical_group(2, [13,35], name='CONTACT')
    gmsh.model.add_physical_group(2, [60,82,126,148,192,214], name='TARGET')
    gmsh.model.add_physical_group(2, [72,112,138,178,204,244], name='FIX_Z_SYM')
    gmsh.model.add_physical_group(2, [108,174,240], name='FIX_Y')
    gmsh.model.add_physical_group(2, [49,50,51,205,249,227], name='FIX_X')
    gmsh.model.add_physical_group(1, [124], name='CONTACT_LINE')
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)

if __name__ == '__main__':
    main()
    



    