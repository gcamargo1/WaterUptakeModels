"""Prints water uptake and water stress results in a spreadsheet"""
from xlwt import Workbook
class PrintOutput(object):
    """Create a print class"""
    def __init__(self, soil):

        self.book_out = Workbook(encoding='utf-8') # Output data
        # Crop headers
        self.crop_out = self.book_out.add_sheet('crop')
        #self.crop_out2 = self.book_out.add_sheet('crop 2')
        self.crop_headers = ['sim_day', 'Year', 'DOY', '', 'Transpiration',
                             'Potential Transp.', 'Transp.Ratio', 'Cum.Transp.',
                             'Cum.Pot.Transp.']
        FIRST_ROW = 0
        for i in range(len(self.crop_headers)):
            self.crop_out.write(FIRST_ROW, i, self.crop_headers[i])
        # Soil headers in excel output
        self.soil_out = self.book_out.add_sheet('soil')
        self.soil_headers = ['sim_day', 'Year', 'DOY', 'Runoff', 'Infiltration',
                             'Drainage', 'Soil evaporation']
        for i in range(1, soil.total_layers+1):
            self.soil_headers.append('Layer %d WC'%i)
        for i in range(1, soil.total_layers+1):
            self.soil_headers.append('Layer %d WP'%i)
        for i in range(len(self.soil_headers)):
            self.soil_out.write(FIRST_ROW, i, self.soil_headers[i])

    def daily(self, sim_day, year, doy, crop, soil):
        # Crop printing
        self.crop_out.write(sim_day, 0, sim_day)
        self.crop_out.write(sim_day, 1, year)
        self.crop_out.write(sim_day, 2, doy)
        self.crop_out.write(sim_day, 4, crop.att_transp)
        self.crop_out.write(sim_day, 5, crop.expect_transp)
        self.crop_out.write(sim_day, 6, crop.transp_ratio)
        self.crop_out.write(sim_day, 7, crop.cum_transp)
        self.crop_out.write(sim_day, 8, crop.cum_pot_transp)
        #Soil printing
        self.soil_out.write(sim_day, 0, sim_day)
        self.soil_out.write(sim_day, 1, year)
        self.soil_out.write(sim_day, 2, doy)
        self.soil_out.write(sim_day, 3, 0)
        self.soil_out.write(sim_day, 4, 0)
        self.soil_out.write(sim_day, 5, 0)
        self.soil_out.write(sim_day, 6, 0)
        water_content_list = []
        water_potential_list = []
        for wc in soil.water_content:
            water_content_list.append(wc)
        for wp in soil.water_potential:
            water_potential_list.append(wp)
        for col in range(7, 7 + soil.total_layers):
            self.soil_out.write(sim_day, col, water_content_list[col-7])
        for col in range(7 + soil.total_layers, 7 + 2 * soil.total_layers):
            self.soil_out.write(sim_day, col, water_potential_list[
                col - (7 + soil.total_layers)])

    def save_data(self, fname):
        self.book_out.save(fname)


