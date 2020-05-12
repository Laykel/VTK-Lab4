import vtk


def main():
    """One render window, multiple viewports"""
    ren_win = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Define viewport ranges
    xmins = [0, .5, 0, .5]
    xmaxs = [0.5, 1, 0.5, 1]
    ymins = [0, 0, .5, .5]
    ymaxs = [0.5, 0.5, 1, 1]

    for i in range(4):
        ren = vtk.vtkRenderer()
        ren_win.AddRenderer(ren)

        if i == 0:
            camera = ren.GetActiveCamera()
        else:
            ren.SetActiveCamera(camera)

        ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])
        # Create a sphere
        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetCenter(0.0, 0.0, 0.0)
        sphere_source.SetRadius(5)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere_source.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        ren.AddActor(actor)
        ren.ResetCamera()

    ren_win.Render()
    ren_win.SetWindowName('RW: Multiple ViewPorts')
    iren.Start()


if __name__ == '__main__':
    main()
