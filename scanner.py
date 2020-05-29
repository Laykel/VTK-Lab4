#!/usr/bin/env python

"""
Lab: 4-KneeScan
Authors: Claude-André Alves, Luc Wachter
Description: Manipulate a knee scan using different techniques (contouring, clipping, cutting, implicit functions, ...)
Date: 12.05.2020
Python version: 3.7.4
Sources:
https://lorensen.github.io/VTKExamples/site/Python/IO/ReadSLC/
https://lorensen.github.io/VTKExamples/site/Python/Visualization/MultipleViewports/
https://lorensen.github.io/VTKExamples/site/Cxx/PolyData/DistancePolyDataFilter/
https://www.kitware.com/products/books/VTKUsersGuide.pdf
"""

from time import sleep
from os.path import isfile
import vtk

# The time a frame stays on screen (seconds)
FRAMERATE = 0.01
SLC_FILENAME = "vw_knee.slc"


def outline(vtk_reader):
    """Create an actor representing an outline for the object
    :param vtk_reader: The vtk object around which the outline must appear
    :returns: A vtkActor representing an outline around the object
    """
    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(vtk_reader.GetOutputPort())
    outliner.Update()

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outliner.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(0, 0, 0)
    return outline_actor


def contour(vtk_reader, i, j):
    """Take in a reader and return a contour filter object
    :param vtk_reader: The object to apply contouring to
    :param i: Index of the iso-value
    :param j: Iso-value for the contour filter
    :returns: A vtkContourFilter to add to the pipeline
    """
    # Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object
    contourer = vtk.vtkContourFilter()
    contourer.SetInputConnection(vtk_reader.GetOutputPort())
    contourer.SetValue(i, j)

    return contourer


def create_actor(vtk_algo):
    """Create an actor from a vtkObject
    :param vtk_algo: The object for which to create an actor
    :returns: An actor representing the object sent as parameter
    """
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(vtk_algo.GetOutputPort())
    mapper.SetScalarVisibility(False)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def repeated_cuts(vtk_contour, nb_cuts):
    """Cut the given object nb_cuts times using a plane, a cutter and a tube filter
    :param vtk_contour: The object to cut in tubes
    :param nb_cuts: The number of tubes to cut
    :returns: An actor representing the object cut in nb_cuts tubes separated by 10
    """
    plane = vtk.vtkPlane()
    plane.SetOrigin(0, 0, 0)

    plane_cutter = vtk.vtkCutter()
    plane_cutter.SetInputConnection(vtk_contour.GetOutputPort())
    plane_cutter.SetCutFunction(plane)

    for i in range(nb_cuts + 1):
        # Add cut values and separate each cut by a space of 10
        plane_cutter.SetValue(i, i * 10)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(plane_cutter.GetOutputPort())
    stripper.Update()

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputConnection(stripper.GetOutputPort())
    tube_filter.SetRadius(1)
    tube_filter.Update()

    return create_actor(tube_filter)


def create_sphere_clipping(vtk_algo, radius, coordinates):
    """Create a clipping actor between the vtk_object provided and a sphere at the coordinates and of the radius
    :param vtk_algo: The object to clip with the sphere
    :param radius: The radius of the sphere
    :param coordinates: The coordinates of the sphere
    :returns: An actor representing the object clipped with the sphere
    """
    sphere = vtk.vtkSphere()
    sphere.SetRadius(radius)
    sphere.SetCenter(coordinates)

    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(vtk_algo.GetOutputPort())
    clipper.SetClipFunction(sphere)
    clipper.GenerateClippedOutputOn()
    clipper.SetValue(0.5)

    return create_actor(clipper)


def get_sphere_actor(pos, radius):
    """Returns a sphere actor at the position and of the size specified"""
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(pos)
    sphere.SetRadius(radius)
    sphere.SetPhiResolution(30)
    sphere.SetThetaResolution(30)

    return create_actor(sphere)


def distance_color(data1, data2, filename):
    """Either generates or reads a polydata object colored depending on the distance to another object
    If the filename provided already exists on the file system, the function tries to read it and returns an actor.
    If not, the function generates a distance filter and returns an actor (this takes a long time).
    """
    if isfile(filename):
        dist_polydata = read_from_file(filename)
    else:
        dist_filter = vtk.vtkDistancePolyDataFilter()
        dist_filter.SignedDistanceOff()
        dist_filter.SetInputConnection(0, data1.GetOutputPort())
        dist_filter.SetInputConnection(1, data2.GetOutputPort())
        dist_filter.Update()

        dist_polydata = dist_filter.GetOutput()

        write_to_file(dist_polydata, filename)

    dist_ranges = dist_polydata.GetPointData().GetScalars().GetRange()

    color_mapper = vtk.vtkPolyDataMapper()
    color_mapper.SetInputData(dist_polydata)
    color_mapper.SetScalarRange(dist_ranges[0], dist_ranges[1])

    bone_color = vtk.vtkActor()
    bone_color.SetMapper(color_mapper)

    return bone_color


def write_to_file(data, filename):
    """Write polydata geometry, topology and attributes to file"""
    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData(data)
    writer.SetFileName(filename)
    writer.Write()


def read_from_file(filename):
    """Read polydata geometry, topology and attributes from file"""
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()


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

    # Create actors
    knee_outline = outline(reader)
    knee_bone = create_actor(bone_contour)
    knee_skin = create_actor(skin_contour)
    knee_skin.GetProperty().SetColor(0.9, 0.69, 0.56)

    # Cut knee for top left visualization
    cut_skin = repeated_cuts(skin_contour, 19)
    cut_skin.GetProperty().SetColor(0.9, 0.69, 0.56)

    # Clipped knee for top right and bottom left visualizations
    knee_clipped = create_sphere_clipping(skin_contour, 48, (80, 40, 110))
    knee_clipped.GetProperty().SetColor(0.9, 0.69, 0.56)

    knee_clipped_transparent = create_sphere_clipping(skin_contour, 48, (80, 40, 110))
    knee_clipped_transparent.GetProperty().SetColor(0.9, 0.69, 0.56)
    knee_clipped_transparent.GetProperty().SetOpacity(0.5)

    knee_clipped_backside = create_sphere_clipping(skin_contour, 48, (80, 40, 110))
    knee_clipped_backside.GetProperty().SetColor(0.9, 0.69, 0.56)
    knee_clipped_backside.GetProperty().FrontfaceCullingOn()

    sphere_transparent = get_sphere_actor((80, 40, 110), 48)
    sphere_transparent.GetProperty().SetOpacity(0.4)

    # Colored bone for bottom right visualization
    # This will generate the file if it doesn't exist (computationally expensive)
    bone_color = distance_color(bone_contour, skin_contour, "bone_distance_color.vtk")

    # Set up a single camera for all the viewports
    camera = vtk.vtkCamera()
    camera.SetPosition(0, 0, 100)
    camera.SetFocalPoint(0, 0, 0)
    # Move the camera in the right position
    camera.Elevation(-90)
    camera.OrthogonalizeViewUp()
    camera.Roll(180)

    # Define viewport ranges
    viewports = [(0, 0, 0.5, 0.5), (0.5, 0, 1, 0.5), (0, 0.5, 0.5, 1), (0.5, 0.5, 1, 1)]

    # Actors for the four viewports
    actors_per_viewport = [
        [knee_clipped, sphere_transparent, knee_bone, knee_outline],
        [bone_color, knee_outline],
        [cut_skin, knee_bone, knee_outline],
        [knee_clipped_transparent, knee_clipped_backside, knee_bone, knee_outline]
    ]

    # Background colors for the four viewports
    bg_colors = [(0.82, 0.82, 1), (0.82, 0.82, 0.82), (1, 0.82, 0.82), (0.82, 1, 0.82)]

    # Create the viewports and generate the visualizations
    for idx, actors in enumerate(actors_per_viewport):
        # Set up the renderer for this viewport
        ren = vtk.vtkRenderer()
        ren.SetActiveCamera(camera)
        ren_win.AddRenderer(ren)

        ren.SetViewport(viewports[idx])

        # Add appropriate actors
        for actor in actors:
            ren.AddActor(actor)

        ren.SetBackground(bg_colors[idx])
        ren.ResetCamera()

    # Move the camera around the focal point to turn around the objects
    for _ in range(360):
        camera.Azimuth(1)

        ren_win.Render()
        sleep(FRAMERATE)

    interactor.Start()


if __name__ == "__main__":
    main()
