from GeoGraphQL.src.tool_windows.query_builder_widget import QueryBuilderWidget
from qgis.PyQt.QtCore import Qt


class QueryBuilderTool:
    """Docket window with GeoGraphQl query builder"""

    def __init__(self, iface):
        """
            Constructor.

            iface(QgsInterface): An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        """
        self.iface = iface

        self.icon_path = ':/plugins/GeoGraphQLPlugin/icon.png'
        self.menu_text = u'query builder'

        self.dock_widget = None

    def on_unload(self):
        """ """

        if self.dock_widget is not None:
            self.dock_widget.close()

    def on_close_widget(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # close widget
        self.dock_widget.closingWidget.disconnect(self.on_close_widget)

        self.dock_widget = None

    def run(self):
        """ this constructions makes sure only one instance is opened at a time"""

        if self.dock_widget is None:
            self.dock_widget = QueryBuilderWidget(
                parent=self.iface.mainWindow(),
                iface=self.iface,
            )
            # connect cleanup on closing of dockwidget
            self.dock_widget.closingWidget.connect(self.on_close_widget)

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        self.dock_widget.show()
