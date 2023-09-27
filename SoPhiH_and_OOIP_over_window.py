# -*- coding: utf-8 -*-
"""
@author: jjcharzynski
"""

import datetime
import lasio
import os
import pandas as pd

def SoPhiH_and_OOIP_over_window(folder, ftabove, ftbelow, A, Bo, phi, sw):
    """
    Read LAS files in a specified folder, calculated OOIP, SoPhiH , and window curves and save a new las file containing them.
    Assumes that all LAS files in the folder have the porosity and sw curves named the same.

    Args:
        folder (str): The folder path containing the LAS files.
        ftabove (int): The distance in feet above.
        ftbelow (int): The distance in feet below.
        A (float): Area, used in OOIP calculation
        Bo (float): Bo parameter for OOIP calculation.
        phi (string): Porosity Curve Name.
        sw (string): Water Saturation Curve Name.
    
    Returns:
        None.
        
    Example Usage:
        SoPhiH_and_OOIP_over_window('folder', ftabove=100, ftbelow=50, A=1, Bo=1.25, phi='PHIT', sw='SW')
    """
    os.chdir(folder)
    lasFolder = os.getcwd()
    starttime = datetime.datetime.now()
    print('Started at', starttime)
    counter = 0
    error = 0

    for filename in os.listdir(lasFolder):
        if filename.endswith(".Las"):
            name, ext = os.path.splitext(filename)
            las = lasio.read(filename)
            step = las.well.STEP.value
            df = las.df()

            try:
                df['SoPhiH'] = step * df[phi] * (1 - df[sw])
            except KeyError:
                print(las.well.UWI, 'does not have the required input logs.')
                error += 1
                counter += 1
                continue

            df['OOIP'] = 7758 * A * df['SoPhiH'] * (1 / Bo)
            indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=int(ftbelow / step))
            aboveSophiH = df['SoPhiH'].rolling(int(ftabove / step)).sum()
            belowSophiH = df['SoPhiH'].rolling(indexer).sum()
            windowfeet = ftabove + ftbelow
            sophihwindowname = 'SoPhiH_' + str(windowfeet) + 'ft_window_' + str(ftabove) + 'ft_up_' + str(ftbelow) + 'ft_down'
            df[sophihwindowname] = aboveSophiH + belowSophiH - df['SoPhiH']
            aboveOOIP = df['OOIP'].rolling(int(ftabove / step)).sum()
            belowOOIP = df['OOIP'].rolling(indexer).sum()
            ooipwindowname = 'OOIP_' + str(windowfeet) + 'ft_window_' + str(ftabove) + 'ft_up_' + str(ftbelow) + 'ft_down'
            df[ooipwindowname] = aboveOOIP + belowOOIP - df['OOIP']

            las.set_data(df)
            las.curves.SoPhiH.unit = 'hydrocarbon ft'
            las.curves.SoPhiH.descr = 'SoPhiH from PHIT and SWT curves'
            las.curves.OOIP.unit = 'bbls/acre'
            las.curves.OOIP.descr = 'barrels per acre using area = 1 and Bo = 1.25'
            las.curves[sophihwindowname].unit = 'hydrocarbon ft'
            las.curves[sophihwindowname].descr = 'rolling sum of SoPhiH over a 150 ft window'
            las.curves[ooipwindowname].unit = 'bbls/acre'
            las.curves[ooipwindowname].descr = 'rolling sum of OOIP over a 150 ft window'

            newfilename = name + '_calculated.Las'
            las.write(newfilename)
            counter += 1
        else:
            continue

    print(counter, 'wells processed with', error, 'errors.')
    runtime = datetime.datetime.now() - starttime
    print('Completed at', datetime.datetime.now(), 'in', runtime)