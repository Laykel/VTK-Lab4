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
SLC_FILENAME = "vw_knee.slc"


def outline(vtk_object):
    """Create an actor representing an outline for the object
    :param vtk_object: The vtk object around which the outline must appear
    :returns: A vtkActor representing an outline around the object
    """
    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(vtk_object.GetOutputPort())
    outliner.Update()

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outliner.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(0, 0, 0)
    return outline_actor


def contour(vtk_object, i, j):
    """...
    :param vtk_object: The object to apply contouring to
    :param i: ...
    :param j: ...
    :returns: A vtkContourFilter to add to the pipeline
    """
    # Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object.
    contourer = vtk.vtkContourFilter()
    contourer.SetInputConnection(vtk_object.GetOutputPort())
    contourer.SetValue(i, j)

    return contourer


def create_actor(vtk_object):
    """Create an actor from a vtkObject
    :param vtk_object: The object for which to create an actor
    :returns: An actor representing the object sent as parameter
    """
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(vtk_object.GetOutputPort())
    mapper.SetScalarVisibility(False)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


# Main instructions
def main():
    ren_win = vtk.vtkRenderWindow()
    ren_win.SetWindowName("The good knee")
    ren_win.SetSize(1000, 1000)

    # Create an SLC reader
    reader = vtk.vtkSLCReader()
    reader.SetFileName(SLC_FILENAME)
    reader.Update()

    # Create actors
    knee_outline = outline(reader)
    knee_bone = create_actor(contour(reader, 0, 72.0))
    knee_skin = create_actor(contour(reader, 0, 50))

    # Create a transform object for the knee and its outline
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    knee_bone.SetUserTransform(transform)
    knee_outline.SetUserTransform(transform)
    knee_skin.SetUserTransform(transform)

    # Rotate the knee in its initial position
    transform.RotateX(90)

    # Define viewport ranges
    xmins = [0, .5, 0, .5]
    xmaxs = [0.5, 1, 0.5, 1]
    ymins = [0, 0, .5, .5]
    ymaxs = [0.5, 0.5, 1, 1]

    # Renderers for the four viewports
    renderers = [vtk.vtkRenderer() for _ in range(4)]
    # Actors for the four viewports
    actors = [knee_skin, knee_skin, knee_bone, knee_bone]
    # Background colors for the four viewports
    colors = [(0.82, 0.82, 1), (0.82, 0.82, 0.82), (1, 0.82, 0.82), (0.82, 1, 0.82)]

    # Create the viewports and generate the visualizations
    for idx, ren in enumerate(renderers):
        ren_win.AddRenderer(ren)

        ren.SetViewport(xmins[idx], ymins[idx], xmaxs[idx], ymaxs[idx])

        # Create a mapper and actor
        ren.AddActor(actors[idx])
        ren.AddActor(knee_outline)
        ren.SetBackground(colors[idx])
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
