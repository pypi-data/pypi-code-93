from cryoloBM import helper_image,helper_GUI,boxmanager_controller

try:
    QT = 4
    import PyQt4
    from matplotlib.backends.backend_qt4agg import (
        NavigationToolbar2QT as NavigationToolbar,
    )
except ImportError:
    QT = 5
    import PyQt5
    from matplotlib.backends.backend_qt5agg import (
        NavigationToolbar2QT as NavigationToolbar,
    )


class Boxmanager_Toolbar(NavigationToolbar):
    def __init__(self,  controller:boxmanager_controller)->None:
        self.controller=controller
        self.dozoom = False
        NavigationToolbar.__init__(self, self.controller.view.plot.canvas, self.controller.view.plot)
        self.start_point_zoom = None

    def press_zoom(self, event:helper_GUI.plt_qtbackend)->None:
        self.start_point_zoom = [event.xdata ,event.ydata ]
        super(Boxmanager_Toolbar, self).press_zoom(event)


    def zoom(self, *args)->None:
        super(Boxmanager_Toolbar, self).zoom(args)

    def home(self, *args)->None:
        helper_image.delete_all_patches(controller=self.controller)
        if self.controller.view.background_current:
            self.controller.view.fig.canvas.restore_region(self.controller.view.background_current)
        self.controller.view.background_current = self.controller.view.fig.canvas.copy_from_bbox(self.controller.view.ax.bbox)

        self.controller.model.rectangles = self.controller.model.box_dictionary.get_sketches(
            f=self.controller.get_current_filename(with_extension=False),
            n=self.controller.model.index_tomo, is_3D=self.controller.model.has_3d,  is_tracing = False)
        helper_image.draw_all_patches(controller=self.controller)
        super(Boxmanager_Toolbar, self).home(args)

    def release_zoom(self, event:helper_GUI.plt_qtbackend)->None:
        self.dozoom = False

        lastx = self.start_point_zoom[0]
        lasty = self.start_point_zoom[1]
        # ignore singular clicks - 5 pixels is a threshold
        if not (abs(event.x - lastx) < 5 or abs(event.y - lasty) < 5):
            self.dozoom = True
            helper_image.delete_all_patches(controller=self.controller)
            if self.controller.view.background_current:
                self.controller.view.fig.canvas.restore_region(self.controller.view.background_current)
            self.controller.view.zoom_update = True

        super(Boxmanager_Toolbar, self).release_zoom(event)
        self.start_point_zoom = None


    def pan(self, *args)->None:
        super(Boxmanager_Toolbar, self).pan(args)

    def drag_pan(self, event:helper_GUI.plt_qtbackend)->None:
        super(Boxmanager_Toolbar, self).drag_pan(event)
        helper_image.delete_all_patches(controller=self.controller)
        if self.controller.view.background_current:
            self.controller.view.fig.canvas.restore_region(self.controller.view.background_current)
        self.controller.view.background_current = self.controller.view.fig.canvas.copy_from_bbox(self.controller.view.ax.bbox)
        self.controller.view.zoom_update = True
