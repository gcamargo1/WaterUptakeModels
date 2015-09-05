#!/usr/bin/env python
from __future__ import division
from xlrd import open_workbook
import matplotlib.pyplot as plt

def main():
    campbell_book = open_workbook('campbell_output.xls')
    dssat_book =  open_workbook('DSSAT_output.xls')
    apsim_book = open_workbook('APSIM_output.xls')
    feddes_book = open_workbook('feddes_output.xls')
    epic_book = open_workbook('epic_output.xls')
    wofost_book = open_workbook('wofost_output.xls')

    campbell_crop = campbell_book.sheet_by_name('crop')
    dssat_crop = dssat_book.sheet_by_name('crop')
    apsim_crop = apsim_book.sheet_by_name('crop')
    feddes_crop = feddes_book.sheet_by_name('crop')
    epic_crop = epic_book.sheet_by_name('crop')
    wofost_crop = wofost_book.sheet_by_name('crop')

    campbell_soil = campbell_book.sheet_by_name('soil')
    dssat_soil = dssat_book.sheet_by_name('soil')
    apsim_soil = apsim_book.sheet_by_name('soil')
    feddes_soil = feddes_book.sheet_by_name('soil')
    epic_soil = epic_book.sheet_by_name('soil')
    wofost_soil = wofost_book.sheet_by_name('soil')

    doy = []
    rows = range(campbell_crop.nrows)

    # Cumulative transpiration
    cum_transp_campbell = []
    cum_transp_dssat = []
    cum_transp_apsim = []
    cum_transp_feddes = []
    cum_transp_epic = []
    cum_transp_wofost = []

    doy_col = 0
    CUM_TRANSP_COL = 7
    for row in rows:
        cum_transp_campbell.append(campbell_crop.cell(row, CUM_TRANSP_COL).value)
        cum_transp_dssat.append(dssat_crop.cell(row, CUM_TRANSP_COL).value)
        cum_transp_apsim.append(apsim_crop.cell(row, CUM_TRANSP_COL).value)
        cum_transp_feddes.append(feddes_crop.cell(row, CUM_TRANSP_COL).value)
        cum_transp_epic.append(epic_crop.cell(row, CUM_TRANSP_COL).value)
        cum_transp_wofost.append(wofost_crop.cell(row, CUM_TRANSP_COL).value)

        doy.append(campbell_crop.cell(row, doy_col).value)

    transp_ratio_campbell = []
    transp_ratio_dssat = []
    transp_ratio_apsim = []
    transp_ratio_feddes = []
    transp_ratio_epic = []
    transp_ratio_wofost = []

    TRANSP_RATIO_COL = 6
    for row in rows:
        transp_ratio_campbell.append(campbell_crop.cell(row, TRANSP_RATIO_COL).value)
        transp_ratio_dssat.append(dssat_crop.cell(row, TRANSP_RATIO_COL).value)
        transp_ratio_apsim.append(apsim_crop.cell(row, TRANSP_RATIO_COL).value)
        transp_ratio_feddes.append(feddes_crop.cell(row, TRANSP_RATIO_COL).value)
        transp_ratio_epic.append(epic_crop.cell(row, TRANSP_RATIO_COL).value)
        transp_ratio_wofost.append(wofost_crop.cell(row, TRANSP_RATIO_COL).value)

    # Plots
    # Cummulative transpiration
    plt.figure(1)
    plt.subplot(2,1,1).tick_params(axis='both', which='major', labelsize=12)

    plt.plot(doy[1:], cum_transp_apsim[1:], color='k', marker=None, dashes=[5,3,1,3], label='APSIM')
    plt.plot(doy[1:], cum_transp_campbell[1:], color='k', marker=None, dashes=(None,None), label='CropSyst')
    plt.plot(doy[1:], cum_transp_dssat[1:], color='k', marker=None, dashes=[5,5], label='DSSAT')
    plt.plot(doy[1:], cum_transp_epic[1:], color='k', marker=None, dashes=[5,3,1,2,1,10], label='EPIC')
    plt.plot(doy[1:], cum_transp_feddes[1:], color='k', marker=None, dashes=[1,3], label='SWAP')
    plt.plot(doy[1:], cum_transp_wofost[1:], color='k', marker=None, dashes=[5,2,10,5], label='WOFOST')

    plt.ylabel(r'Cumulative $T_{a}$',fontsize=14,labelpad=8)#, fontweight='bold')
    #plt.xlabel('Sim days',fontsize=16,labelpad=8)#, fontweight='bold')
    plt.xlim(0, 60)
    plt.ylim(0, 250)
    plt.legend(loc='best',prop={'size':14},frameon=False)
    #plt.savefig('Cum_T.svg')

    # Transpiration ratio
    plt.subplot(2,1,2).tick_params(axis='both', which='major', labelsize=12)
    plt.plot(doy[1:], transp_ratio_apsim[1:], color='k', marker=None, dashes=[5,3,1,3], label='APSIM')
    plt.plot(doy[1:], transp_ratio_campbell[1:], color='k', marker=None, dashes=(None,None), label='CropSyst')
    plt.plot(doy[1:], transp_ratio_dssat[1:], color='k', marker=None, dashes=[5,5], label='DSSAT')
    plt.plot(doy[1:], transp_ratio_epic[1:], color='k', marker=None, dashes=[5,3,1,2,1,10], label='EPIC')
    plt.plot(doy[1:], transp_ratio_feddes[1:], color='k', marker=None, dashes=[1,3], label='SWAP')
    plt.plot(doy[1:], transp_ratio_wofost[1:], color='k', marker=None, dashes=[5,2,10,5], label='WOFOST')

    plt.ylabel(r'$T_{a}$ / $T_{p}$',fontsize=14,labelpad=8)#,fontweight='bold')
    plt.xlabel('Simulation days',fontsize=14,labelpad=8)#, fontweight='bold')

    plt.xlim(0, 60)
    plt.ylim(0, 1.1)
    plt.setp(plt.subplot(2, 1, 1).get_xticklabels(), visible=False)
    #plt.legend(loc='best',prop={'size':14},frameon=False)
    plt.savefig('Cum_T_T_ratio.svg')

    plt.show()
if __name__ == '__main__':
    main()