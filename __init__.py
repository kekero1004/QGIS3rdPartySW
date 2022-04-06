# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name			 	 : DaumApi Tool
Description          : Use Daum API like roadView, geocoding and juso search
Date                 : 02/April/21
copyright            : (C) 2021 by J.D.M.P.E
email                : 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # loads DaumAPI Class from DaumAPI Library
    from .daumAPI import daumAPI
    return daumAPI(iface)


