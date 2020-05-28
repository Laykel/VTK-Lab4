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
    :param i: TODO
    :param j: TODO
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


def create_sphere_clipping(vtk_object, radius, coordinates):
    sphere = vtk.vtkSphere()
    sphere.SetRadius(radius)
    sphere.SetCenter(coordinates)

    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(vtk_object.GetOutputPort())
    clipper.SetClipFunction(sphere)
    clipper.GenerateClippedOutputOn()
    clipper.SetValue(0.5)

    clip_mapper = vtk.vtkPolyDataMapper()
    clip_mapper.SetInputConnection(clipper.GetOutputPort())
    clip_mapper.SetScalarVisibility(False)

    clipped = vtk.vtkActor()
    clipped.SetMapper(clip_mapper)

    return clipped


# Main instructions
def main():
    ren_win = vtk.vtkRenderWindow()
    ren_win.SetWindowName("The good knee")
    ren_win.SetSize(1000, 1000)

    # Watch for events
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(ren_win)

    # Set the interactor style
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    # Create an SLC reader
    reader = vtk.vtkSLCReader()
    reader.SetFileName(SLC_FILENAME)
    reader.Update()

    # Create contours
    bone_contour = contour(reader, 0, 72.0)
    skin_contour = contour(reader, 0, 50)

    # -------------------------------------------------------------------- SPHERE
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetCenter(80, 40, 110)
    sphere_source.SetRadius(48)
    sphere_source.SetPhiResolution(15)
    sphere_source.SetThetaResolution(15)

    sphere_mapper = vtk.vtkPolyDataMapper()
    sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

    sphere_transparent = vtk.vtkActor()
    sphere_transparent.SetMapper(sphere_mapper)
    sphere_transparent.GetProperty().SetOpacity(0.2)
    # -------------------------------------------------------------------- SPHERE
    # -------------------------------------------------------------------- DISTANCE
    clean1 = vtk.vtkCleanPolyData()
    clean1.SetInputData(bone_contour.GetOutput())
    clean2 = vtk.vtkCleanPolyData()
    clean2.SetInputData(skin_contour.GetOutput())

    distance_filter = vtk.vtkDistancePolyDataFilter()
    distance_filter.SignedDistanceOff()
    # distance_filter.SetInputConnection(0, clean1.GetOutputPort())
    # distance_filter.SetInputConnection(1, clean2.GetOutputPort())
    distance_filter.Update()

    color_mapper = vtk.vtkPolyDataMapper()
    color_mapper.SetInputConnection(distance_filter.GetOutputPort())

    bone_color = vtk.vtkActor()
    bone_color.SetMapper(color_mapper)
    # -------------------------------------------------------------------- DISTANCE

    # Create actors
    knee_outline = outline(reader)
    knee_bone = create_actor(bone_contour)
    knee_skin = create_actor(skin_contour)
    knee_skin.GetProperty().SetColor(0.9, 0.69, 0.56)

    knee_clipped = create_sphere_clipping(skin_contour, 48, (80, 40, 110))
    knee_clipped.GetProperty().SetColor(0.9, 0.69, 0.56)

    # TODO Make it not transparent on the back
    knee_clipped_transparent = create_sphere_clipping(skin_contour, 48, (80, 40, 110))
    knee_clipped_transparent.GetProperty().SetColor(0.9, 0.69, 0.56)
    knee_clipped_transparent.GetProperty().SetOpacity(0.5)

    # Define viewport ranges
    xmins = [0, .5, 0, .5]
    xmaxs = [0.5, 1, 0.5, 1]
    ymins = [0, 0, .5, .5]
    ymaxs = [0.5, 0.5, 1, 1]

    # Set up a single camera for all the viewports
    camera = vtk.vtkCamera()
    camera.SetPosition(0, 0, 100)
    camera.SetFocalPoint(0, 0, 0)
    # Move the camera in the right position
    camera.Elevation(-90)
    camera.OrthogonalizeViewUp()
    camera.Roll(180)

    # Actors for the four viewports
    actors_per_viewport = [
        [knee_clipped, sphere_transparent, knee_bone, knee_outline],
        [bone_color, knee_outline],
        [knee_skin, knee_bone, knee_outline],
        [knee_clipped_transparent, knee_bone, knee_outline]
    ]
    # Background colors for the four viewports
    colors = [(0.82, 0.82, 1), (0.82, 0.82, 0.82), (1, 0.82, 0.82), (0.82, 1, 0.82)]

    # Create the viewports and generate the visualizations
    for idx, actors in enumerate(actors_per_viewport):
        ren = vtk.vtkRenderer()
        ren.SetActiveCamera(camera)
        ren_win.AddRenderer(ren)

        ren.SetViewport(xmins[idx], ymins[idx], xmaxs[idx], ymaxs[idx])

        for actor in actors:
            ren.AddActor(actor)

        ren.SetBackground(colors[idx])
        ren.ResetCamera()

    # Rotate all objects to have a 360 view
    for _ in range(360):
        camera.Azimuth(1)

        ren_win.Render()
        sleep(FRAMERATE)

    interactor.Start()


if __name__ == "__main__":
    main()
