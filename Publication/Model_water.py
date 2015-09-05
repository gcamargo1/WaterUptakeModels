'''Framework to compare water uptake and water stress algorithms for the
    APSIM, CropSyst, DSSAT, EPIC, SWAP and WOFOST simulation models '''
#!/usr/bin/env python
from __future__ import division
from xlrd import open_workbook
from Crop_class import Crop
from Soil_class import Soil
from Print_class import PrintOutput


def main():
    # Control initialization
    book = open_workbook('sim_data.xls') # Input data
    sheet_inputs = book.sheet_by_name('inputs')
    start_day = int(sheet_inputs.cell(2, 1).value)
    end_day = int(sheet_inputs.cell(3, 1).value)
    start_year = int(sheet_inputs.cell(4, 1).value)
    end_year = int(sheet_inputs.cell(5, 1).value)
    sim_length = 366 - start_day + (end_year - start_year) * 366

    # Soil initialization
    soil_campbell = Soil(book)
    soil_dssat = Soil(book)
    soil_apsim = Soil(book)
    soil_feddes = Soil(book)
    soil_epic = Soil(book)
    soil_wofost = Soil(book)

    # Crops initialization
    crop_campbell = Crop(1, sim_length, book, soil_campbell)
    crop_dssat = Crop(1, sim_length, book, soil_dssat)
    crop_apsim = Crop(1, sim_length, book, soil_apsim)
    crop_feddes = Crop(1, sim_length, book, soil_feddes)
    crop_epic = Crop(1, sim_length, book, soil_epic)
    crop_wofost = Crop(1, sim_length, book, soil_wofost)
    crop_list = [crop_campbell, crop_dssat, crop_apsim, crop_feddes, crop_epic,
                 crop_wofost]

    # Print initialization
    print_outputs_campbell = PrintOutput(soil_campbell)
    print_outputs_dssat = PrintOutput(soil_dssat)
    print_outputs_apsim = PrintOutput(soil_apsim)
    print_outputs_feddes = PrintOutput(soil_feddes)
    print_outputs_epic = PrintOutput(soil_epic)
    print_outputs_wofost = PrintOutput(soil_wofost)

    # Start simulation
    new_year = start_year
    day_of_year = start_day
    sim_day = 1


    # All solar radiation intercepted by canopy
    crop_campbell.light_intercpt = 1
    crop_dssat.light_intercpt = 1
    crop_apsim.light_intercpt = 1
    crop_feddes.light_intercpt = 1
    crop_epic.light_intercpt = 1
    crop_wofost.light_intercpt = 1

    while True:
        # Water uptake
        for crop in crop_list:
            if crop == crop_campbell:
                crop.water_uptake_campbell(soil_campbell)
            if crop == crop_dssat:
                crop.water_uptake_dssat(soil_dssat)
            if crop == crop_apsim:
                crop.water_uptake_apsim(soil_apsim)
            if crop == crop_feddes:
                crop.water_uptake_feddes(soil_feddes)
            if crop == crop_epic:
                crop.water_uptake_epic(soil_epic)
            if crop == crop_wofost:
                crop.water_uptake_wofost(soil_wofost)

        # Update soil water content
        soil_campbell.update_water_content([crop_campbell])
        soil_dssat.update_water_content([crop_dssat])
        soil_apsim.update_water_content([crop_apsim])
        soil_feddes.update_water_content([crop_feddes])
        soil_epic.update_water_content([crop_epic])
        soil_wofost.update_water_content([crop_wofost])

        # Print outputs
        print_outputs_campbell.daily(sim_day, new_year, day_of_year,
                                     crop_campbell, soil_campbell)
        print_outputs_dssat.daily(sim_day, new_year, day_of_year, crop_dssat,
                                  soil_dssat)
        print_outputs_apsim.daily(sim_day, new_year, day_of_year, crop_apsim,
                                  soil_apsim)
        print_outputs_feddes.daily(sim_day, new_year, day_of_year, crop_feddes,
                                   soil_feddes)
        print_outputs_epic.daily(sim_day, new_year, day_of_year, crop_epic,
                                 soil_epic)
        print_outputs_wofost.daily(sim_day, new_year, day_of_year, crop_wofost,
                                   soil_wofost)
        sim_day += 1 # New simulation day
        day_of_year += 1

        # Save excel files and end simulation
        if new_year == end_year and day_of_year == end_day:
            print_outputs_campbell.save_data('campbell_output.xls')
            print_outputs_dssat.save_data('DSSAT_output.xls')
            print_outputs_apsim.save_data('APSIM_output.xls')
            print_outputs_feddes.save_data('feddes_output.xls')
            print_outputs_epic.save_data('epic_output.xls')
            print_outputs_wofost.save_data('wofost_output.xls')
            break # end of simulation

if __name__ == '__main__':
    main()
