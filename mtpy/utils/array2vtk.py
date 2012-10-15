#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created Oct,2012

@author: Aixa Rivera-Rios, Lars Krieger

Creating and saving (unstructured) grid from a cloud of points.

At the moment only for scalar valued fields !!!!

"""
import numpy as np
from scipy.spatial import Delaunay 
import os, sys, platform

class VTKException(Exception):
    pass


if platform.platform().lower().startswith('linux'):
    try:
        from  tvtk.api import tvtk
    except:
        import vtk as tvtk

elif platform.platform().lower().startswith('win'):
    try:
        from enthought.tvtk.api import tvtk
    except:
        raise VTKException

else:
    sys.exit("system could not be determined")        




class Array2VTK():
    """
    Class for defining and handling a VTK grid.

    Input:
    - array of grid points, shape (n_points, n_dimensions + 1 [or3]) - by default data is interpreted as scalar

    - optional: separated data array, shape (n_points, [1/3])
    - optional: number of spatial dimensions - must be provided, if separate data array is given (for distiguishing between points and data entries) 
    - optional: grid type ['structured'/'unstructured']
    - optional: data type ['scalar'/'vector']
    
    """

    def __init__(self, points_and_data, data_array=None, n_dimensions = None, grid_type='unstructured', data_type='scalar'):


        self.grid_type      = grid_type
        self._original_grid = points_and_data

        if data_array != None:
            self.points    = points_and_data
            self.data      = data_array
        else:
            self.points    = points_and_data[:,:-1]
            self.data      = points_and_data[:,-1]

            
        self.dimension = self.points.shape[1]


        if self.grid_type=='unstructured':

            interp_grid = Delaunay(self.points)
            new_points  = interp_grid.points

            #include dummy dimension for 2D data set
            if self.points.shape[1]==2:
                tmp_points = np.zeros((new_points.shape[0],3))
                tmp_points[:,0] = new_points[:,0]#np.sqrt(new_points[:,0]**2+new_points[:,1]**2)
                tmp_points[:,2] = new_points[:,1]
                new_points = tmp_points
        
            
            new_cells   = interp_grid.vertices
            
            self.grid = tvtk.UnstructuredGrid(points=new_points)
            self.grid.point_data.scalars = self.data
            self.grid.set_cells(tvtk.Tetra().cell_type,new_cells)
            

    def set_variablename(self, name):
        
        self.grid.point_data.scalars.name = name

    
    def save(self, outfilename):

        if self.grid_type=='unstructured':
            out_fn = os.path.abspath(os.path.realpath(outfilename+'.vtu'))
            writer = tvtk.XMLUnstructuredGridWriter(input=self.grid, file_name=out_fn)
            writer.write()   

        elif self.grid_type=='structured':
            out_fn = os.path.abspath(os.path.realpath(outfilename+'.vts'))
            writer = tvtk.XMLStructuredGridWriter(input=self.grid, file_name=out_fn)
            writer.write()

        else:
            sys.exit('cannot save grid -- grid type is undefined')

    
def main(arglist):
    
    """Usage: array2vtk.py <ascii file with grid and data points> <Data variable name> <output file name> [optional <extra file containing data only> <n_dimensions>]"""

    if not len(arglist) in [4,6]:
        print "Usage: \n\n array2vtk.py <ascii file with grid and data points> <Data variable name> <output file name> [optional <extra file containing data only> <n_dimensions>]\n\n"
        sys.exit()

    try:

        local_args = arglist[1:]
        if len(arglist)==6:
            gridfile    = os.path.abspath(local_args[0])
            datafile    = os.path.abspath(local_args[3])
            grid_in_raw = np.loadtxt(gridfile)
            data_in_raw = np.loadtxt(datafile)

            n_points = min(grid_in_raw.shape[0],data_in_raw.shape[0])
            n_dims   = int(float(local_args[4]))
            
            grid_in  = np.zeros((n_points,n_dims))
            data_in  = np.zeros((n_points,1))


            grid_in[:,:n_dims] = grid_in_raw[:n_points,:n_dims]
            data_in   = data_in_raw[:n_points]
                

        elif len(arglist)==4:
            grid_and_datafile = os.path.abspath(local_args[0])
            grid_and_data_raw = np.loadtxt(grid_and_datafile)

            n_dims   = grid_and_data_raw.shape[1]-1
            n_points = grid_and_data_raw.shape[0]

            grid_in  = grid_and_data_raw[:,:n_dims]
            data_in  = grid_and_data_raw[:,-1]


        field_name  = local_args[2]

        outfilename = local_args[3]

    except:
        print 'ERROR: wrong input parameters'
        raise VTKException('Could not digest input parameters!')
    

    vtkgrid2 = Array2VTK(grid_in,data_in)
    vtkgrid2.set_variablename(field_name)
    vtkgrid2.save(outfilename)
    return vtkgrid2

    

if __name__ == "__main__":
    vv = main(sys.argv)

