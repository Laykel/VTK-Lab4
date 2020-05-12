#!/usr/bin/env python

"""
Lab: 4-KneeScan
Authors: Claude-André Alves, Luc Wachter
Description: Provide four visualizations of a knee scan.
Date: 12.05.2020
Python version: 3.7.4

https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/
"""

import vtk


def read_slc_file(filename):
    reader = vtk.vtkSLCReader()
    reader.SetFileName(filename)
    reader.Update()

    # Create a mapper.
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object.
    contour_filter = vtk.vtkContourFilter()
    contour_filter.SetInputConnection(reader.GetOutputPort())
    contour_filter.SetValue(0, 72.0)

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader.GetOutputPort())
    outliner.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour_filter.GetOutputPort())
    mapper.SetScalarVisibility(0)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


# Main instructions
def main():
    ren_win = vtk.vtkRenderWindow()
    ren_win.SetWindowName("The good knee")
    ren_win.SetSize(1000, 1000)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Define viewport ranges
    xmins = [0, .5, 0, .5]
    xmaxs = [0.5, 1, 0.5, 1]
    ymins = [0, 0, .5, .5]
    ymaxs = [0.5, 0.5, 1, 1]

    knee = read_slc_file("vw_knee.slc")

    for i in range(4):
        ren = vtk.vtkRenderer()
        ren_win.AddRenderer(ren)

        if i == 0:
            camera = ren.GetActiveCamera()
        else:
            ren.SetActiveCamera(camera)

        ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])

        # Create a mapper and actor
        ren.AddActor(knee)
        ren.ResetCamera()

    ren_win.Render()
    iren.Start()


if __name__ == "__main__":
    main()
