"""Module prints water content and water potential of soil profiles of the
   different models"""
#!/usr/bin/env python
from __future__ import division
from xlrd import open_workbook
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import numpy as np
def main():
    cwd = os.getcwd()
    cycles_book = open_workbook('campbell_output.xls')
    dssat_book = open_workbook('DSSAT_output.xls')
    apsim_book = open_workbook('APSIM_output.xls')
    feddes_book = open_workbook('feddes_output.xls')
    epic_book = open_workbook('epic_output.xls')
    wofost_book = open_workbook('wofost_output.xls')

    cycles_soil = cycles_book.sheet_by_name('soil')
    dssat_soil = dssat_book.sheet_by_name('soil')
    apsim_soil = apsim_book.sheet_by_name('soil')
    feddes_soil = feddes_book.sheet_by_name('soil')
    epic_soil = epic_book.sheet_by_name('soil')
    wofost_soil = wofost_book.sheet_by_name('soil')

    water_content_colmns = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    water_potential_colmns = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    nrows = cycles_soil.nrows

    water_content_cycles = np.zeros([nrows, len(water_content_colmns)])
    water_content_dssat = np.zeros([nrows, len(water_content_colmns)])
    water_content_apsim = np.zeros([nrows, len(water_content_colmns)])
    water_content_feddes = np.zeros([nrows, len(water_content_colmns)])
    water_content_epic = np.zeros([nrows, len(water_content_colmns)])
    water_content_wofost = np.zeros([nrows, len(water_content_colmns)])

    water_potential_cycles = np.zeros([nrows, len(water_potential_colmns)])
    water_potential_dssat = np.zeros([nrows, len(water_potential_colmns)])
    water_potential_apsim = np.zeros([nrows, len(water_potential_colmns)])
    water_potential_feddes = np.zeros([nrows, len(water_potential_colmns)])
    water_potential_epic = np.zeros([nrows, len(water_potential_colmns)])
    water_potential_wofost = np.zeros([nrows, len(water_potential_colmns)])

    for i, row in enumerate(range(1, nrows)):
        for j, col in enumerate(water_content_colmns):
            water_content_cycles[i, j] = cycles_soil.cell(row, col).value
            water_content_dssat[i, j] = dssat_soil.cell(row, col).value
            water_content_apsim[i, j] = apsim_soil.cell(row, col).value
            water_content_feddes[i, j] = feddes_soil.cell(row, col).value
            water_content_epic[i, j] = epic_soil.cell(row, col).value
            water_content_wofost[i, j] = wofost_soil.cell(row, col).value

    for i, row in enumerate(range(1, nrows)):
        for j, col in enumerate(water_potential_colmns):
            water_potential_cycles[i, j] = cycles_soil.cell(row, col).value
            water_potential_dssat[i, j] = dssat_soil.cell(row, col).value
            water_potential_apsim[i, j] = apsim_soil.cell(row, col).value
            water_potential_feddes[i, j] = feddes_soil.cell(row, col).value
            water_potential_epic[i, j] = epic_soil.cell(row, col).value
            water_potential_wofost[i, j] = wofost_soil.cell(row, col).value
    # Plots
    depths = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    
    # Selected days based on Campbells silt loam: mid-way between start and
    # start drop, start drop, and half between start drop and end
    sim_days = [15, 30, 45]

    # Water potential
    plt.figure(1, figsize=(18, 12))
    plt.subplot(2, 3, 2).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_potential_cycles[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])

    plt.plot(water_potential_cycles[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_potential_cycles[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([-2200, 0])
    #plt.xlabel("Water potential (J/kg)")
    #plt.ylabel("Soil depth (m)", fontsize=14, labelpad=8)
    plt.text(-2110, 0.2, 'CropSyst',path_effects=[pe.withStroke(linewidth=10, foreground='w')],
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    #plt.legend(loc='lower left')

    plt.subplot(2, 3, 3).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_potential_dssat[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_potential_dssat[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_potential_dssat[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([-2200, 0])
    #plt.xlabel(r"Water potential (J kg$^{-1}$)", fontsize=22, labelpad=8)
    #plt.ylabel("Soil depth (m)")
    plt.text(-2110, 0.2, 'DSSAT',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    
    plt.subplot(2, 3, 1).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_potential_apsim[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_potential_apsim[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_potential_apsim[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([-2200, 0])
    #plt.xlabel(r"Water potential (J kg$^{-1}$)", fontsize=22, labelpad=8)
    plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    plt.text(-2110, 0.2, 'APSIM',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    plt.legend(loc='lower left',prop={'size':18})

    plt.subplot(2, 3, 5).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_potential_feddes[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_potential_feddes[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_potential_feddes[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([-2200, 0])
    plt.xlabel(r"Water potential (J kg$^{-1}$)", fontsize=22, labelpad=8)
    #plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    plt.text(-2110, 0.2, 'SWAP',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    #plt.legend()

    plt.subplot(2, 3, 6).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_potential_wofost[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_potential_wofost[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_potential_wofost[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([-2200, 0])
    plt.xlabel(r"Water potential (J kg$^{-1}$)", fontsize=22, labelpad=8)
    #plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    plt.text(-2110, 0.2, 'WOFOST',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)

    plt.subplot(2, 3, 4).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_potential_epic[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_potential_epic[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_potential_epic[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([-2200, 0])
    plt.xlabel(r"Water potential (J kg$^{-1}$)",fontsize=22,labelpad=8)
    plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    plt.text(-2110, 0.2, 'EPIC',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    plt.setp(plt.subplot(2, 3, 1).get_xticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 2).get_xticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 2).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 3).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 5).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 6).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 3).get_xticklabels(), visible=False)


    plt.subplots_adjust(wspace=0.08, hspace=0.05, right=0.9)
    plt.savefig('Fig4_WP.svg')

    # Water content
    plt.figure(2, figsize=(18, 12))
    plt.subplot(2, 3, 2).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_content_cycles[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_content_cycles[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_content_cycles[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([0.05, 0.39])
    #plt.xlabel("Water content (m3/m3)")
    #plt.ylabel("Soil depth (m)", fontsize=16, labelpad=8)
    plt.text(0.28, 0.2, 'CropSyst',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    #plt.legend()

    plt.subplot(2, 3, 3).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_content_dssat[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_content_dssat[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_content_dssat[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([0.05, 0.39])
    #plt.xlabel(r"Water content (m$^{3}$ m$^{-3}$)", fontsize=22, labelpad=8)
    #plt.ylabel("Soil depth (m)")
    plt.text(0.28, 0.2, 'DSSAT', bbox={'facecolor':'white', 'alpha':0, 'pad':10},
             fontsize=22)
    #plt.legend()

    plt.subplot(2, 3, 1).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_content_apsim[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_content_apsim[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_content_apsim[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([0.05, 0.39])
    #plt.xlabel(r"Water content (m$^{3}$ m$^{-3}$)", fontsize=22, labelpad=8)
    plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    plt.text(0.28, 0.2, 'APSIM', bbox={'facecolor':'white', 'alpha':0, 'pad':10},
             fontsize=22)
    plt.legend(loc='lower right', prop={'size':18})

    plt.subplot(2, 3, 5).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_content_feddes[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_content_feddes[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_content_feddes[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([0.05, 0.39])
    plt.xlabel(r"Water content (m$^{3}$ m$^{-3}$)", fontsize=22, labelpad=8)
    #plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    plt.text(0.28, 0.2, 'SWAP',
             bbox={'facecolor':'white', 'alpha':0, 'pad':10}, fontsize=22)
    #plt.legend()

    plt.subplot(2, 3, 4).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_content_epic[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_content_epic[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_content_epic[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([0.05, 0.39])
    plt.xlabel(r"Water content (m$^{-3}$ m$^{-3}$)",fontsize=22,labelpad=8)
    plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    #plt.legend()
    plt.text(0.28, 0.2, 'EPIC', bbox={'facecolor':'white', 'alpha':0, 'pad':10},
             fontsize=22)

    plt.subplot(2, 3, 6).tick_params(axis='both', which='major', labelsize=16)
    plt.plot(water_content_wofost[sim_days[0]], depths, color='k', marker=".",
             dashes=(None, None), label='Day %d'%sim_days[0])
    plt.plot(water_content_wofost[sim_days[1]], depths, color='k', marker=".",
             dashes=[5, 5], label='Day %d'%sim_days[1])
    plt.plot(water_content_wofost[sim_days[2]], depths, color='k', marker=".",
             dashes=[5, 3, 1, 3], label='Day %d'%sim_days[2])
    plt.ylim([0.95, 0.05])
    plt.xlim([0.05, 0.39])
    plt.xlabel(r"Water content (m$^{-3}$ m$^{-3}$)",fontsize=22,labelpad=8)
    #plt.ylabel("Soil depth (m)", fontsize=22, labelpad=8)
    #plt.legend()
    plt.text(0.28, 0.2, 'WOFOST', bbox={'facecolor':'white', 'alpha':0, 'pad':10},
             fontsize=22)

    plt.setp(plt.subplot(2, 3, 1).get_xticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 2).get_xticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 2).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 3).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 5).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 6).get_yticklabels(), visible=False)
    plt.setp(plt.subplot(2, 3, 3).get_xticklabels(), visible=False)

    plt.subplots_adjust(wspace=0.08, hspace=0.05, right=0.9)

    plt.savefig('Fig3_WC.svg')
    plt.show()

if __name__ == '__main__':
    main()
