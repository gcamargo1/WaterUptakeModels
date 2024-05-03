"""Module that create the crop class for each water uptake simulation model"""
import math
import numpy as np

from functions import feddes_stress_factor, p_wofost


class Crop(object):
    """Crop class"""

    def __init__(self, crop_no, sim_length, book, soil):
        """A new crop instance"""
        sheet_inputs = book.sheet_by_name("inputs")
        # Campbell max canopy transpiration, mm/d:
        self.campbell_max_daily_transp = sheet_inputs.cell(6, crop_no).value
        # DSSAT max water uptake, cm3water/cm3root:
        self.dssat_max_water_uptake = sheet_inputs.cell(7, crop_no).value
        # Feddes stress threshold water potential for low T demand, J/kg
        self.P2L = sheet_inputs.cell(8, crop_no).value
        # Feddes stress threshold water potential for high T demand, J/kg
        self.P2H = sheet_inputs.cell(9, crop_no).value
        # Feddes high transpiration demand, mm/day
        self.R2H = sheet_inputs.cell(10, crop_no).value
        # Feddes low transpiration demand, mm/day
        self.R2L = sheet_inputs.cell(11, crop_no).value
        # Feddes alue of the pressure head, below which roots start to extract
        # water from the soil
        self.P0 = sheet_inputs.cell(12, crop_no).value
        # Campbell leaf water potential at onset of stomatal closure [J/kg]:
        self.leaf_water_pot_stress_onset = sheet_inputs.cell(13, crop_no).value
        # Campbell leaf water potential at wilting point [J/kg]:
        self.leaf_water_pot_wilt_point = sheet_inputs.cell(14, crop_no).value
        # EPIC water extraction distribution
        self.water_extraction_dist = sheet_inputs.cell(15, crop_no).value

        self.leaf_water_pot = 0  # J/kg
        self.sim_length = sim_length  # d
        self.conductance = np.ones(soil.total_layers)
        self.water_uptake = np.zeros(soil.total_layers)
        self.leaf_water_potential = np.zeros(soil.total_layers)
        self.soil_water_pot_avg = 0
        self.transp_ratio = 0  # to quantify crop water stress
        self.crop_transp = 0
        self.pot_transp = 0
        self.att_transp = 0
        self.expect_transp = 0
        self.cum_transp = 0
        self.cum_pot_transp = 0
        self.root_dens = np.zeros(soil.total_layers)  # m root / m3 soil
        self.root_fraction = np.zeros(soil.total_layers)  # m root / m soil
        sheet_soil = book.sheet_by_name("soil")
        for lyr in soil.layers:
            self.root_dens[lyr] = sheet_soil.cell(9 + lyr, 9).value
            self.root_fraction[lyr] = sheet_soil.cell(9 + lyr, 10).value
        self.root_depth = sheet_soil.cell(3, 4).value

    def water_uptake_dssat(self, soil):
        """DSSAT model water uptake

        soil: soil class with properties

        References:
        Jones, J.W., Hoogenboom, G., Porter, C.H., Boote, K.J., Batchelor, W.D.
         Hunt, L.A., Wilkens, P.W., Singh, U., Gijsman, A.J., Ritchie, J.T.,
         2003. The DSSAT cropping system model. Eur. J. Agron. 18, 235-265.
        Boote, K. J., F. Sau, G. Hoogenboom, and J. W. Jones. 2008. Experience
         with Water Balance, Evapotranspiration, and Predictions of Water
         Stress Effects in the CROPGRO Model. In Response of Crops to Limited
         Water. Understanding and Modeling Water Stress Effects on Plant Growth
         Processes. L. R. Ahuja, V. R. Reddy, S. A. Saseendran, and Q. Yu, eds.
         Madison, WI: ASA-CSSA-SSSA.

        original source code: ROOTWU.FOR
        """
        CONV1 = 1e-4  # convert m/m3 to cm/cm3
        CONV2 = 100  # convert m to cm
        CONV3 = 10  # convert cm to mm

        daily_ref_evap_transp = soil.daily_ref_evap_transp
        transp_pot = daily_ref_evap_transp * self.light_intercpt
        root_dens = self.root_dens * CONV1  # cm root / cm3 soil
        CONST1 = 1.3e-3
        CONST2 = np.zeros(soil.total_layers)
        CONST3 = 7.01
        layer_thickness = soil.layer_thickness * CONV2
        water_uptake = np.zeros(soil.total_layers)
        # Constant 2
        for lyr in soil.layers:
            CONST2[lyr] = 120 - 250 * soil.perm_wilt_point[lyr]
            if soil.perm_wilt_point[lyr] > 0.3:
                CONST2[lyr] = 45
        # Water uptake per unit root length
        for lyr in soil.layers:
            if root_dens[lyr] <= 0.00001 or (
                soil.water_content[lyr] <= soil.perm_wilt_point[lyr]
            ):
                water_uptake[lyr] = 0
            else:
                water_uptake[lyr] = (
                    CONST1
                    * math.exp(
                        min(
                            (
                                CONST2[lyr]
                                * (soil.water_content[lyr] - soil.perm_wilt_point[lyr])
                            ),
                            40,
                        )
                    )
                    / (CONST3 - math.log(root_dens[lyr]))
                )
                water_uptake[lyr] = min(water_uptake[lyr], self.dssat_max_water_uptake)
            # Water uptake in [cm/d] volume
            water_uptake[lyr] = (
                water_uptake[lyr] * layer_thickness[lyr] * root_dens[lyr]
            )
            # Water uptake in [mm/d] volume
            water_uptake[lyr] = water_uptake[lyr] * CONV3
        # Total water uptake [mm/d]
        crop_transp = water_uptake.sum()
        min_transp = min(transp_pot, crop_transp)
        # Update crop arrays
        for lyr in soil.layers:
            if min_transp > 0:
                self.water_uptake[lyr] = water_uptake[lyr] * (min_transp / crop_transp)
            else:
                self.water_uptake[lyr] = 0
        self.att_transp = self.water_uptake.sum()  # mm/day
        self.cum_transp += self.att_transp  # mm
        self.transp_ratio = self.att_transp / transp_pot
        self.expect_transp = transp_pot
        self.cum_pot_transp += self.expect_transp

    def water_uptake_apsim(self, soil):
        """APSIM model water uptake

        soil: soil class with properties

        References:
        Passioura, J.B., 1983. Roots and drought resistance. Agricultural Water
         Management 7, 265-280.
        Monteith, J.L., 1986. How do crops manipulate water supply and demand?
         Philosophical Transactions of the Royal Society of London 316, 245-259

        original source code:
        crop_sw_uptake0.cpp: crop_sw_uptake0 (subroutine)
        crp_watrModule.f: crop_sw_supply (subroutine)
        maize.f: Maize_water_uptake (subroutine)
        """
        soil_wat_avail = np.zeros(soil.total_layers)
        soil_wat_supply = np.zeros(soil.total_layers)
        daily_ref_evap_transp = soil.daily_ref_evap_transp
        transp_pot = daily_ref_evap_transp * self.light_intercpt
        # Water available in each layer [mm]
        for lyr in soil.layers:
            soil_wat_avail[lyr] = (
                (soil.water_content[lyr] - soil.perm_wilt_point[lyr])
                * soil.layer_thickness[lyr]
                * soil.WATER_DENSITY
            )
        # Water supply
        for lyr in soil.layers:
            soil_wat_supply[lyr] = soil_wat_avail[lyr] * soil.kl[lyr]

        # Water uptake (no supply or demand)
        if (soil_wat_supply.sum() <= 0) or (transp_pot <= 0):
            for lyr in soil.layers:
                self.water_uptake[lyr] = 0
        else:
            # Water uptake (water is not limiting)
            if transp_pot < soil_wat_supply.sum():
                # distribute demand proportionately to the water supply
                for lyr in soil.layers:
                    self.water_uptake[lyr] = (
                        soil_wat_supply[lyr] / soil_wat_supply.sum() * transp_pot
                    )
            else:
                # Water uptake (water is limiting)
                for lyr in soil.layers:
                    self.water_uptake[lyr] = soil_wat_supply[lyr]

        self.att_transp = self.water_uptake.sum()  # mm/day
        self.cum_transp += self.att_transp  # mm
        self.transp_ratio = self.att_transp / transp_pot
        self.expect_transp = transp_pot
        self.cum_pot_transp += transp_pot

    def water_uptake_feddes(self, soil):
        """
        SWAP/Feddes model water uptake

        soil: soil class with properties

        References:
        Feddes, R. A., P. J. Kowalik, and H. Zaradny. 1978. Simulation of field
         water use and crop yield. Wageningen.
        Simunek, J., T. Vogel, and M. T. v. Genuchten. 1994. The SWMS _ 2D Code
         for Simulating Water Flow and Solute Transport in Two-Dimensional
         Variably Saturated Media. FAlfa function. http://www.pc-progress.com/
         Documents/programs/SWMS_2D.pdf
        Diamantopoulos, E., N. Dercas, K. X. Soulis, S. Jellali, and A.
        Stefopoulou. 2011. Application of phosphate water and slime in
         agriculture: investigation of the mobility of the pollutants using
         hydrologic modeling. Global NEST Journal 13(2):130-140. ***Reference
          water potential values"""

        # Value of the pressure head, below which roots extract water at the
        # maximum possible rate
        P1 = soil.field_capacity_water_potential.mean()  # -25 # J/kg
        P3 = soil.perm_wilt_point_pot.mean()  # -8000 # J/kg wilting point
        daily_ref_evap_transp = soil.daily_ref_evap_transp
        transp_pot = daily_ref_evap_transp * self.light_intercpt
        for lyr in soil.layers:
            stress_fact = feddes_stress_factor(
                transp_pot,
                soil.water_potential[lyr],
                self.P0,
                P1,
                self.P2L,
                self.P2H,
                P3,
                self.R2H,
                self.R2L,
            )
            self.water_uptake[lyr] = stress_fact * self.root_fraction[lyr] * transp_pot
        self.att_transp = self.water_uptake.sum()  # mm/day
        self.cum_transp += self.att_transp
        self.expect_transp = transp_pot
        self.cum_pot_transp += self.expect_transp
        self.transp_ratio = self.att_transp / transp_pot

    def water_uptake_wofost(self, soil):
        """
        WOFOST model water uptake

        soil: soil class with properties

        References:
        Supit, I., A. A. Hooijer, and C. v. Diepen. 1994. System Description of
         the WOFOST 6.0 Crop Simulation Model Implemented in CGMS, vol. 1:
         Theory and Algorithms. Joint Research Centre, Commission of the
         European Communities, EUR 15956 EN. Luxembourg.
         source code file: evtra.f
        """
        daily_ref_evap_transp = soil.daily_ref_evap_transp
        transp_pot = daily_ref_evap_transp * self.light_intercpt
        DROUGHT_CAT = 4
        p_value = p_wofost(transp_pot, DROUGHT_CAT)
        # WOFOST does not account for different layers
        for lyr in soil.layers:
            # Root fraction values over-written to simulate as there is only
            # one soil layer
            self.root_fraction[lyr] = soil.layer_thickness[lyr]
            crit_soil_moist = (1 - p_value) * (
                soil.field_capacity[lyr] - soil.perm_wilt_point[lyr]
            ) + soil.perm_wilt_point[lyr]
            stress_fact = (soil.water_content[lyr] - soil.perm_wilt_point[lyr]) / (
                crit_soil_moist - soil.perm_wilt_point[lyr]
            )
            if stress_fact > 1:
                stress_fact = 1
            if stress_fact < 0:
                stress_fact = 0
            self.water_uptake[lyr] = stress_fact * self.root_fraction[lyr] * transp_pot
        self.att_transp = self.water_uptake.sum()  # mm/day
        self.cum_transp += self.att_transp
        self.expect_transp = transp_pot
        self.cum_pot_transp += self.expect_transp
        self.transp_ratio = self.att_transp / transp_pot

    def water_uptake_campbell(self, soil):
        """CropSyst/Campbell model daily water uptake

        soil: soil class with properties

        Reference:
         Campbell, G. S. 1985. Soil physics with BASIC: Transport models for
          soil-plant systems. Developments in soil science. Elsevier, Amsterdam
        Campbell, G. S. 1991. Simulation of water uptake by plant roots. In
         Modeling plant and soil systems, 273-285. J. Hanks, and J. T. Ritchie,
         eds. Madison, WI: ASA/CSSA/SSSA.
        """
        daily_ref_evap_transp = soil.daily_ref_evap_transp
        root_hydr_cond = np.zeros(soil.total_layers)
        shoot_hydr_cond = np.zeros(soil.total_layers)
        plant_hydr_cond = np.zeros(soil.total_layers)
        root_activity = np.zeros(soil.total_layers)
        root_cond_adj = np.zeros(soil.total_layers)
        tot_root_cond_adj = 0
        salinity_factor = np.zeros(soil.total_layers)
        soil_water_pot_avg = 0
        WAT_POT_FIELD_CAP = -33

        # Transpiration
        self.pot_transp = daily_ref_evap_transp * self.light_intercpt
        self.max_pot_transp = self.campbell_max_daily_transp * self.light_intercpt
        self.expect_transp = min(self.pot_transp, self.max_pot_transp)  # mm/day

        # Plant hydraulic conductance (kg s m-4)
        tot_plant_hydr_cond = self.max_pot_transp / (
            WAT_POT_FIELD_CAP - self.leaf_water_pot_stress_onset
        )
        # assumption of 2/3 of plant hydraulic conductance is from roots
        tot_root_hydr_cond = tot_plant_hydr_cond / 0.65
        # assumption of 1/3 of plant hydraulic conductivity is from shoots
        tot_shoot_hydr_cond = tot_plant_hydr_cond / 0.35

        for lyr in soil.layers:
            root_activity[lyr] = 1
            salinity_factor[lyr] = 1
            root_cond_adj[lyr] = (
                root_activity[lyr] * self.root_fraction[lyr] * salinity_factor[lyr]
            )
            root_hydr_cond[lyr] = tot_root_hydr_cond * root_cond_adj[lyr]
            tot_root_cond_adj += root_cond_adj[lyr]

        # Root, shoot and plant hydraulic conductance(kg s m-4)
        for lyr in soil.layers:
            if root_cond_adj[lyr] > 0:
                shoot_hydr_cond[lyr] = (
                    tot_shoot_hydr_cond * root_cond_adj[lyr] / tot_root_cond_adj
                )
                plant_hydr_cond[lyr] = (
                    root_hydr_cond[lyr]
                    * shoot_hydr_cond[lyr]
                    / (root_hydr_cond[lyr] + shoot_hydr_cond[lyr])
                )
            else:
                plant_hydr_cond[lyr] = 0

        tot_root_hydr_cond *= tot_root_cond_adj
        tot_plant_hydr_cond = (tot_root_hydr_cond * tot_shoot_hydr_cond) / (
            tot_root_hydr_cond + tot_shoot_hydr_cond
        )

        if tot_plant_hydr_cond > 0:
            for lyr in soil.layers:
                soil_water_pot_avg += soil.water_potential[lyr] * root_cond_adj[lyr]
            leaf_water_pot = (
                soil_water_pot_avg - self.expect_transp / tot_plant_hydr_cond
            )
            if leaf_water_pot < self.leaf_water_pot_stress_onset:
                leaf_water_pot = (
                    tot_plant_hydr_cond
                    * soil_water_pot_avg
                    * (
                        self.leaf_water_pot_stress_onset
                        - self.leaf_water_pot_wilt_point
                    )
                    + self.leaf_water_pot_wilt_point * self.expect_transp
                ) / (
                    tot_plant_hydr_cond
                    * (
                        self.leaf_water_pot_stress_onset
                        - self.leaf_water_pot_wilt_point
                    )
                    + self.expect_transp
                )
            if leaf_water_pot < self.leaf_water_pot_wilt_point:
                leaf_water_pot = self.leaf_water_pot_wilt_point
                self.att_transp = 0
                transp_ratio = self.att_transp / self.expect_transp

            elif leaf_water_pot < self.leaf_water_pot_stress_onset:
                self.att_transp = (
                    self.expect_transp
                    * (leaf_water_pot - self.leaf_water_pot_wilt_point)
                    / (
                        self.leaf_water_pot_stress_onset
                        - self.leaf_water_pot_wilt_point
                    )
                )
                transp_ratio = self.att_transp / self.expect_transp

            else:
                self.att_transp = self.expect_transp
                transp_ratio = 1
            # crop water uptake (kg/m2/d = mm/d)
            for lyr in soil.layers:
                self.water_uptake[lyr] = (
                    plant_hydr_cond[lyr]
                    * (soil.water_potential[lyr] - leaf_water_pot)
                    * transp_ratio
                )
                if self.water_uptake[lyr] < 0:
                    self.water_uptake[lyr] = 0
        self.crop_transp = self.water_uptake.sum()  # mm/day
        self.cum_transp += self.crop_transp
        self.cum_pot_transp += self.expect_transp
        self.transp_ratio = self.crop_transp / self.expect_transp

    def water_uptake_epic(self, soil):
        """EPIC latest EPIC0810"""
        WATER_DENSITY = 1000
        self.water_uptake = np.zeros(soil.total_layers)
        SUM = np.zeros(soil.total_layers)
        daily_ref_evap_transp = soil.daily_ref_evap_transp
        EP = daily_ref_evap_transp * self.light_intercpt
        UB1 = self.water_extraction_dist
        UOB = 1 - math.exp(-self.water_extraction_dist)
        RD = 1
        RGS = 1
        CPWU = 0.5
        UX = 0
        TOS = 0
        SCRP211 = 9  # 9.6991521 rounded param of s-curve solved using excel
        SCRP212 = 0.005  # 0.004988621 rounded param s-curve solved using excel
        for lyr in soil.layers:
            BLM = soil.perm_wilt_point[lyr] * soil.layer_thickness[lyr] * WATER_DENSITY
            FC = soil.field_capacity[lyr] * soil.layer_thickness[lyr] * WATER_DENSITY
            ST = soil.water_content[lyr] * soil.layer_thickness[lyr] * WATER_DENSITY
            XX = math.log(BLM)

            SUM[lyr] = EP * (1 - math.exp(-UB1 * soil.cum_depth[lyr] / RD)) / UOB

            WTN = max(
                5, 10 ** (3.1761 - 1.6576 * ((math.log(ST) - XX) / (math.log(FC) - XX)))
            )
            XX = TOS + WTN
            if XX < 5000:
                F = 1 - XX / (XX + math.exp(SCRP211 - SCRP212 * XX))
                self.water_uptake[lyr] = (
                    min(
                        SUM[lyr] - CPWU * self.water_uptake.sum() - (1.0 - CPWU) * UX,
                        ST - BLM,
                    )
                    * RGS
                    * F
                )
                if self.water_uptake[lyr] < 0:
                    self.water_uptake[lyr] = 0
            UX = SUM[lyr]

        self.att_transp = self.water_uptake.sum()
        self.cum_transp += self.att_transp
        self.expect_transp = EP
        self.cum_pot_transp += self.expect_transp
        self.transp_ratio = self.att_transp / EP
