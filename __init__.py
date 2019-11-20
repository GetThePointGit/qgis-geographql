# -*- coding: utf-8 -*-

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeoGraphQLClass from file GeoGraphQLPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GeoGraphQLPlugin import GeoGraphQLClass
    return GeoGraphQLClass(iface)
