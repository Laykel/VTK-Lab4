#!/usr/bin/env python

"""
Lab: 4-KneeScan
Authors: Claude-André Alves, Luc Wachter
Description: Provide four visualizations of a knee scan.
Date: 12.05.2020
Python version: 3.7.4

https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/
"""

from time import sleep
import vtk


# The time a frame stays on screen (seconds)
FRAMERATE = 0.01


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

    # Create an actor from the SLC file
    knee = read_slc_file("vw_knee.slc")

    transform = vtk.vtkTransform()
    transform.PostMultiply()
    knee.SetUserTransform(transform)

    # Rotate the knee in its initial position
    transform.RotateX(90)

    # Define viewport ranges
    xmins = [0, .5, 0, .5]
    xmaxs = [0.5, 1, 0.5, 1]
    ymins = [0, 0, .5, .5]
    ymaxs = [0.5, 0.5, 1, 1]

    renderers = [vtk.vtkRenderer(), vtk.vtkRenderer(), vtk.vtkRenderer(), vtk.vtkRenderer()]

    # Create the viewports and generate the visualizations
    for i in range(4):
        ren = renderers[i]
        ren_win.AddRenderer(ren)

        ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])

        # Create a mapper and actor
        ren.AddActor(knee)
        ren.SetBackground(0.5, 0.5, 0.5)
        ren.GetActiveCamera().Elevation(180)
        ren.ResetCamera()

    # Rotate all objects to have a 360 view
    for _ in range(360):
        for ren in renderers:
            ren.GetActiveCamera().Azimuth(1)

        ren_win.Render()
        sleep(FRAMERATE)

    sleep(2)


if __name__ == "__main__":
    main()
