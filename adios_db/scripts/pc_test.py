import adios_db
from adios_db import scripting as dbs
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd
import os
import json
import shutil
from scipy import integrate
from adios_db import scripting as ads
from adios_db.computation.physical_properties import get_distillation_cuts

from datetime import datetime, timedelta
from gnome import spill_container
from gnome import scripting as gs
from gnome.environment import constant_wind, Water
from gnome.weatherers import FayGravityViscous, Langmuir, Evaporation


class TestEvaporation(object):
    '''
    This class is to test evaporation and spreading modules in PyGnome 
    '''      
    def full_test(self, t_hours, amount, time_step, start_time, end_time, temperature, substance, num_elems, wind_speed, sp=False, evap=False, thick=None):
        self.spread = FayGravityViscous()
        self.spread.water = Water(temperature)
    
        self.evap = Evaporation(Water(temperature), wind=constant_wind(wind_speed, 0))
        self.start_time = start_time #gs.asdatetime("2015-05-14")
        self.end_time = end_time #gs.asdatetime(start_time) + gs.hours(12)
        self.time_step=time_step
#        self.weathering_substeps=time_step // 900
        self.num_elems=num_elems
            
        water = Water()
        rqd_weatherers = [FayGravityViscous(water)]
        arrays = dict()
        arrays.update(self.evap.array_types)
        
        for wd in rqd_weatherers:
            arrays.update(wd.array_types)
#        substance = gs.GnomeOil(**test_oil) 
        arrays.update(substance.array_types)
      
        #substance.molecular_weight = 1000 * mw
        
        self.spill = gs.surface_point_line_spill(num_elements=self.num_elems,
                                        start_position=(0.0, 0.0, 0.0),
                                        release_time=self.start_time,
                                        end_release_time=self.end_time,
                                        amount=amount,
                                        substance=substance, #'ALASKA NORTH SLOPE (MIDDLE PIPELINE, 1997)',
                                        units='bbl')                                        
        self.spills = spill_container.SpillContainer()
        self.spills.spills.add(self.spill)
        
        arrays.update(self.spill.all_array_types)
        self.spills.prepare_for_model_run(array_types=arrays)
        self.model_time=self.start_time
        
        self.evap.prepare_for_model_run(self.spills)
        self.evap.prepare_for_model_step(self.spills, self.time_step, self.model_time)
        
        self.oil_kvis = self.spills.get_substances(False)[0].kvis_at_temp(self.spread.water.get('temperature'))
        self.spread._set_thickness_limit(self.oil_kvis)
        if thick is not None:
              self.spread.thickness_limit = thick
#        print(self.spread.thickness_limit)
#        self.spread.initialize_data(self.spills, num_elems)
        x=[1./3600.] 
        y=[1]
        z=[self.spills['area'].sum()]  
        q=self.spills['mass_components']      
#        t_hours=12 #125 #160
        for i in range(1, int(t_hours*3600/self.time_step)):
            num_elems_timestep = self.spills.release_elements(self.start_time, self.end_time)  #(self.time_step, self.model_time)
            
            self.spread.initialize_data(self.spills, num_elems_timestep)
            self.evap.initialize_data(self.spills, num_elems_timestep)
            if i == 1:
               q = np.append(q, self.spills['mass_components'],0)
#            print(self.spread.thickness_limit)
            if sp is True:     
                 self.spread.weather_elements(self.spills, self.time_step, self.model_time)
            else:
                 self.spills['area'][:] = (self.spills['init_mass'][:] / self.spills['density'][:]) / self.spread.thickness_limit
            
            if evap is True:
                 self.evap.weather_elements(self.spills, self.time_step, self.model_time)             
            
            self.model_time += gs.seconds(self.time_step)
            self.spills['age'][:] = self.spills['age'][:] + self.time_step
     
            x.append(i*self.time_step/3600)
            y.append(self.spills['mass'].sum()/self.spills['init_mass'].sum())
            z.append(self.spills['area'].sum())
            q = np.append(q, self.spills['mass_components'],0)
           
        return (x, y, z, q)
        
        
def make_interval(x_raw):
    x_frac = []
    boiling = []
    for i in range(0, len(x_raw)):
        if i == 0:
            x_frac.append((x_raw[1].fraction.value - x_raw[0].fraction.value) / 2.0)
        elif i == len(x_raw) - 1:     
            x_frac.append((x_raw[-1].fraction.value - x_raw[-2].fraction.value) / 2.0)       
        else:
            left = (x_raw[i].fraction.value - x_raw[i-1].fraction.value) / 2.0
            right = (x_raw[i+1].fraction.value - x_raw[i].fraction.value) / 2.0            
            x_frac.append(left + right)
        boiling.append(x_raw[i].vapor_temp.value)             
    return x_frac, boiling

def pseudo6(vapor_temperature, fraction, cut_point = 400., Resolution = 5):
    '''
    This function is to create pseudo components based on distillation data
    PC-1 is the average of the low boiling temperature and 80 oC
    PC-2 is the average of 80 oC and 144 oC
    PC-3... n-1 is created between 144 oC and the cut point for high boiling temperature (e.g., 400 oC)
    PC-3... n-1 is determined based on temperature resolution (e.g., 30 C)
    PC-n is the average of cut point for high boiling temperature and the terminal boiling temperature 
    
    inputs:
    1. vapor_temperature (oC) and fraction) are boiling point and mass fraction from distillation data
    2. cut_point is cut point for high boiling temperature
    3. Resolution is temperature resolution  
    '''
# add terminal boiling temperature if mass fraction is not 1
    if fraction[-1] != 1.:
       k = (vapor_temperature[-1] - vapor_temperature[0]) / (fraction[-1] - fraction[0])
       temp_100 = k * (1.0 - fraction[-1]) + vapor_temperature[-1]
       fraction = np.append(fraction, 1.)
       vapor_temperature = np.append(vapor_temperature, temp_100)  
 
# add terminal boiling temperature if mass fraction is not 1  

# boiling point of 80 oC and 144 oC     
    bl = []
    frac = []
    slope = []
# boiling point of 80 oC and 144 oC 
# special case 0 for terminal biling point > cuting point
    if vapor_temperature[0] > cut_point:
       bl =np.append(bl, (vapor_temperature[0] + vapor_temperature[-1]) / 2.)
       frac = np.append(frac, 1.0)
       return (bl + 273.15, frac, 0, Resolution)
# special case 0 for terminal biling point > cuting point
# special case I for terminal boiling < 80 oC
    if vapor_temperature[-1] <= 80.0:
       bl =np.append(bl, (vapor_temperature[0] + vapor_temperature[-1]) / 2.)
       frac = np.append(frac, 1.0)
       return (bl + 273.15, frac, 0, Resolution)
# special case I for terminal boiling < 80 oC   

    if vapor_temperature[0] <= 80.0:
       bl = np.append(bl, (vapor_temperature[0] + 80.0) / 2.)
       
# special case II for terminal boiling < 144 oC
    if vapor_temperature[-1] <= 144.0:
       bl = np.append(bl, (vapor_temperature[-1] + 80.0) / 2.)
       
       tmp_bl = bl[0]
       pos0 = np.argmax(vapor_temperature > tmp_bl)
       pos1 = np.argmax(vapor_temperature > tmp_bl) - 1   
       k = (fraction[pos1] - fraction[pos0]) / (vapor_temperature[pos1] - vapor_temperature[pos0]) 
       tmp_frac = k * (tmp_bl - vapor_temperature[pos0]) + fraction[pos0]       
       frac = np.append(frac, tmp_frac)
       slope = np.append(slope, 1.0 / k)
               
       frac = np.append(frac, 1.0)
       return (bl + 273.15, frac, slope, Resolution)
# special case II for terminal boiling < 144 oC     
 
    if vapor_temperature[0] <= (80.0 + 144.0) / 2.:
       bl = np.append(bl, (80.0 + 144.0) / 2.)    
#      bl = np.array([(vapor_temperature[0] + 80.0) / 2., (80.0 + 144.0) / 2.])

    for i, value in enumerate(bl):
      index = np.where(vapor_temperature == value)
      if len(index[0]) != 0: 
         frac = np.append(frac, 100*fraction[index])
         
         pos0 = np.argmax(vapor_temperature > value)
         if pos0 > 0:
            pos1 = np.argmax(vapor_temperature > value) - 1
         else:
            pos1 = np.argmax(vapor_temperature > value) + 1
         k = (fraction[pos1] - fraction[pos0]) / (vapor_temperature[pos1] - vapor_temperature[pos0])
         slope = np.append(slope, k * 100)
      else:
         pos0 = np.argmax(vapor_temperature > value)
         if pos0 > 0:
            pos1 = np.argmax(vapor_temperature > value) - 1
         else:
            pos1 = np.argmax(vapor_temperature > value) + 1
         
         k = (fraction[pos1] - fraction[pos0]) / (vapor_temperature[pos1] - vapor_temperature[pos0])
         
         tmp = k * (value - vapor_temperature[pos0]) + fraction[pos0]          
         frac = np.append(frac, tmp * 100.0)
         slope = np.append(slope, k * 100)
    
# boiling point of 80 oC and 144 oC      
    if not np.any(bl):
       start_point = vapor_temperature[0]
    else:
       start_point = 144.0    
    
    Nmax = np.ceil((min(cut_point, vapor_temperature[-1]) - start_point) / Resolution)
#    increment = (cut_point - 144.0) / Nmax   
 
    for i in range(1, int(Nmax)+1):
          if i == 1:
             tmp_bl = start_point + Resolution / 2.0
          else:
             tmp_bl = bl[-1] + Resolution          
          pos0 = np.argmax(vapor_temperature > tmp_bl)
          pos1 = np.argmax(vapor_temperature > tmp_bl) - 1
          
          k = (fraction[pos1] - fraction[pos0]) / (vapor_temperature[pos1] - vapor_temperature[pos0]) 
          tmp_frac = k * (tmp_bl - vapor_temperature[pos0]) + fraction[pos0]           
          
          if tmp_bl <= min(cut_point, vapor_temperature[-1]):
               bl = np.append(bl, tmp_bl)
               frac = np.append(frac, tmp_frac * 100)
               slope = np.append(slope, 1.0 / k) 
           
# boiling point equal to 400 oC    
    if vapor_temperature[-1] > cut_point:
          bl = np.append(bl, cut_point + (vapor_temperature[-1] - cut_point) / 2.)                
          frac = np.append(frac, 100.0)
    else:
          bl = np.append(bl, vapor_temperature[-1])                
          frac = np.append(frac, 100.0)
    
    bl = bl + 273.15    
    k = (frac[-1] - frac[-2]) / (vapor_temperature[-1] - (bl[-2] - 273.15))
    slope = np.append(slope, k)
    
    frac = frac / 100

    return (bl, frac, slope, Resolution)

    
def pseudo_error(arrayT, arrayF, bl, frac, cut_point):
    '''
    This function is to compute 'error bars', which is actually the temperature range or fraction range that PCs represent
    inputs:
    1. arrayT is boiling temperature of PCs
    2. arrayF is mass fraction of PCs
    3. bl is boiling temperature of distillation data
    4. frac is mass fraction of distillation data
    5. cut_point is the cut point for high boiling temperature
    '''
    # add terminal boiling temperature if mass fraction is not 1
    if frac[-1] != 1.:
       k = (bl[-1] - bl[0]) / (frac[-1] - frac[0])
       temp_100 = k * (1.0 - frac[-1]) + bl[-1]
       frac = np.append(frac, 1.)
       bl = np.append(bl, temp_100)  
       
    # add terminal boiling temperature if mass fraction is not 1 

    error_bar_T = np.zeros((2, len(arrayT)))
    error_bar_F = np.zeros((2, len(arrayF)))
    start_point = 0
    
    if arrayT[0] <= 80.0:          
        error_bar_T[0][0] = arrayT[0] - bl[0] 
        error_bar_T[1][0] = 80.0 - arrayT[0]
        start_point = 1        
# special case for terminal boiling point < 80 oC or initial boiling point > cut_point
    if len(arrayT) == 1: 
        error_bar_T[0][0] = arrayT[0] - bl[0]
        error_bar_T[1][0] = bl[-1] - arrayT[0]
        error_bar_F[0][0] = arrayF[0] 
        error_bar_F[1][0] = 0.0
        return error_bar_T, error_bar_F
# special case for terminal boiling point < 80 oC   
   
    if len(arrayT) > 1:
       if arrayT[1] == (80.0 + 144.0) / 2. or bl[-1] <= 144.0:    # consider terminal boiling point < 144 oC
          error_bar_T[0][1] = arrayT[1] - 80.0 
          error_bar_T[1][1] = min(144.0, (arrayT[min(len(arrayT)-1,2)] + arrayT[1]) / 2.) - arrayT[1]
          start_point = start_point + 1
       
    for i in range(start_point, len(arrayT)-1):
          tmp0 = (arrayT[i] - arrayT[i-1]) / 2.0
          tmp1 = (arrayT[i+1] - arrayT[i]) / 2.0
          error_bar_T[0][i] = tmp0
          error_bar_T[1][i] = tmp1
          
          if i == start_point:
               if start_point == 0: 
                    error_bar_T[0][i] = arrayT[i] - bl[0]
               else:
                    error_bar_T[0][i] = arrayT[i] - (arrayT[i-1] + error_bar_T[1][i-1]) #144.0
                    
          if i == len(arrayT)-2 and arrayT[-1] > cut_point:
               error_bar_T[1][i] = cut_point - arrayT[i]             
  
    if len(arrayT) >= 2 and arrayT[-1] > 144.0:
        if arrayT[-1] > cut_point:    
             error_bar_T[0][-1] = arrayT[-1] - cut_point
        else:
             error_bar_T[0][-1] = (arrayT[-1] - arrayT[-2]) / 2.   
    error_bar_T[1][-1] = bl[-1] - arrayT[-1]

    for i in range(0, len(arrayF)):
          val1 = arrayT[i] - error_bar_T[0][i]
          
          pos0 = np.argmax(bl > val1)
          pos1 = np.argmax(bl > val1) - 1
          k =  (frac[pos1] - frac[pos0]) / (bl[pos1] - bl[pos0]) 
          frac_0 = k * (val1 - bl[pos0]) + frac[pos0]
          if i == 0:
             error_bar_F[0][i] = arrayF[i] 
          else:          
             error_bar_F[0][i] = arrayF[i] - frac_0
          
          val2 = arrayT[i] + error_bar_T[1][i]
          
          pos0 = np.argmax(bl > val2)
          pos1 = np.argmax(bl > val2) - 1
          k =  (frac[pos1] - frac[pos0]) / (bl[pos1] - bl[pos0]) 
          frac_1 = k * (val2 - bl[pos0]) + frac[pos0]
          
          error_bar_F[1][i] = frac_1 - arrayF[i]
           
    return error_bar_T, error_bar_F    

def calculate_mass_fraction(temps, frac, bl_pc, pc_yerr, residual):
 
    mass_fraction_pc = []
    T0 = bl_pc - pc_yerr[0][:] - 273.15
    T1 = bl_pc + pc_yerr[1][:] - 273.15
    for i in range(0, len(bl_pc)):
#        print('temperature range', T0[i], T1[i])
        if T1[i] <= temps[-1] and i == (len(bl_pc) - 1):
           index = np.where(temps == T0[i])
           if len(index[0]) != 0: 
              Frac0 = frac[index]
           else:
              pos0 = np.argmax(temps > T0[i])
              if pos0 > 0:
                 pos1 = np.argmax(temps > T0[i]) - 1              
              else:
                 pos1 = np.argmax(temps > T0[i]) + 1
              k = (frac[pos1] - frac[pos0]) / (temps[pos1] - temps[pos0])         
              Frac0 = k * (T0[i] - temps[pos0]) + frac[pos0]
           mass_fraction_pc = np.append(mass_fraction_pc, 1.0-Frac0)   
        elif T1[i] <= temps[0] and i == 0:
           mass_fraction_pc = np.append(mass_fraction_pc, frac[0])
        elif T0[i] <= temps[0] and T1[i] >= temps[0] and i == 0:
           index = np.where(temps == T1[i])
           if len(index[0]) != 0: 
              Frac1 = frac[index]
           else:
              pos0 = np.argmax(temps > T1[i])
              if pos0 > 0:
                 pos1 = np.argmax(temps > T1[i]) - 1              
              else:
                 pos1 = np.argmax(temps > T1[i]) + 1
              k = (frac[pos1] - frac[pos0]) / (temps[pos1] - temps[pos0])         
              Frac1 = k * (T1[i] - temps[pos0]) + frac[pos0]
           mass_fraction_pc = np.append(mass_fraction_pc, Frac1)  
        elif T1[i] <= temps[0] and i != 0:
           mass_fraction_pc = np.append(mass_fraction_pc, 0)
        elif T0[i] <= temps[0] and T1[i] >= temps[0]:
           index = np.where(temps == T1[i])
           if len(index[0]) != 0: 
              Frac1 = frac[index]
           else:
              pos0 = np.argmax(temps > T1[i])
              if pos0 > 0:
                 pos1 = np.argmax(temps > T1[i]) - 1              
              else:
                 pos1 = np.argmax(temps > T1[i]) + 1
              k = (frac[pos1] - frac[pos0]) / (temps[pos1] - temps[pos0])         
              Frac1 = k * (T1[i] - temps[pos0]) + frac[pos0]
           mass_fraction_pc = np.append(mass_fraction_pc, Frac1-frac[0])
        elif T0[i] >= temps[0] and T1[i] <= temps[-1]:
           index = np.where(temps == T0[i])
           if len(index[0]) != 0: 
              Frac0 = frac[index]
           else:
              pos0 = np.argmax(temps > T0[i])
              if pos0 > 0:
                 pos1 = np.argmax(temps > T0[i]) - 1              
              else:
                 pos1 = np.argmax(temps > T0[i]) + 1
              k = (frac[pos1] - frac[pos0]) / (temps[pos1] - temps[pos0])         
              Frac0 = k * (T0[i] - temps[pos0]) + frac[pos0]
           
           index = np.where(temps == T1[i])
           if len(index[0]) != 0: 
              Frac1 = frac[index]
           else:
              pos0 = np.argmax(temps > T1[i])
              if pos0 > 0:
                 pos1 = np.argmax(temps > T1[i]) - 1              
              else:
                 pos1 = np.argmax(temps > T1[i]) + 1
              k = (frac[pos1] - frac[pos0]) / (temps[pos1] - temps[pos0])         
              Frac1 = k * (T1[i] - temps[pos0]) + frac[pos0]
           
           mass_fraction_pc = np.append(mass_fraction_pc, Frac1-Frac0)
        elif T0[i] <= temps[-1] and T1[i] >= temps[-1]:
           index = np.where(temps == T0[i])
           if len(index[0]) != 0: 
              Frac0 = frac[index]
           else:
              pos0 = np.argmax(temps > T0[i])
              if pos0 > 0:
                 pos1 = np.argmax(temps > T0[i]) - 1              
              else:
                 pos1 = np.argmax(temps > T0[i]) + 1
              k = (frac[pos1] - frac[pos0]) / (temps[pos1] - temps[pos0])         
              Frac0 = k * (T0[i] - temps[pos0]) + frac[pos0]
        
           mass_fraction_pc = np.append(mass_fraction_pc, 1.0 - Frac0)
        elif T0[i] >= temps[-1]:
           mass_fraction_pc = np.append(mass_fraction_pc, 1.0 - frac[-1])
        else:
           print('Error: mass fraction has not been checked')         
        
# add residual mass beyond measurement of the distillation data    
        
    return mass_fraction_pc


def molecular_weight1(boiling, index = 'Mp'):
    '''
    This function is to compute the molecular weight directly from the MW Equations. 
    '''
    molecular_weight = np.empty_like(boiling) 
    
    for i in range(1, len(boiling)+1):
        bl = min(boiling[i-1] + 273.15, 1000.)
        if index == 'Mp':
           tmp = ((1./0.02013)*(6.98291-np.log(1070.-bl)))**(3./2.)
        
        if index == 'Mn':
           tmp = ((1./0.02239)*(6.95649-np.log(1028.-bl)))**(3./2.)
           
        if index == 'Ma':
           tmp = ((1./0.02247)*(6.91062-np.log(1015.-bl)))**(3./2.)   

        molecular_weight[i-1] = tmp
    
    return molecular_weight/1000
    
def molecular_weight2(err, boiling, index = 'Mp'):
    '''
    This function is to compute the molecular weight from the integral of MW equations over the temperature range that PCs represent.
    '''
    molecular_weight = np.empty_like(boiling) 
    for i in range(1, len(boiling)+1):
        a = boiling[i-1]-err[0][i-1] + 273.15
        b = boiling[i-1]+err[1][i-1] + 273.15
        b = min(b, 1000.)
        if index == 'Mp':
           tmp = integrate.quad(lambda x: ((1./0.02013)*(6.98291-np.log(1070.-x)))**(3./2.), a, b) / (b-a)
        
        if index == 'Mn':
           tmp = integrate.quad(lambda x: ((1./0.02239)*(6.95649-np.log(1028.-x)))**(3./2.), a, b) / (b-a)
           
        if index == 'Ma':
           tmp = integrate.quad(lambda x: ((1./0.02247)*(6.91062-np.log(1015.-x)))**(3./2.), a, b) / (b-a)   

        molecular_weight[i-1] = tmp[0]
    
    return molecular_weight/1000

def molecular_weight3(erry, errx, boiling, fraction, slope, index = 'Mp'):
    '''
    This function is to compute the molecular weight from the following scheme:
    1. compute the moles over the boiling range for PCs
    2. dm / the value computed from step 1  
    '''
    molecular_weight = np.empty_like(boiling) 
     
    for i in range(1, len(boiling)+1):
        a = boiling[i-1]-erry[0][i-1] + 273.15
        b = boiling[i-1]+erry[1][i-1] + 273.15
        b = min(b, 1000.)
        
        if index == 'Mp':
           tmp = scipy.integrate.quad(lambda x: slope[i-1] / ((1./0.02013)*(6.98291-np.log(1070.-x)))**(3./2.), a, b)
        
        if index == 'Mn':
           tmp = scipy.integrate.quad(lambda x: slope[i-1] / ((1./0.02239)*(6.95649-np.log(1028.-x)))**(3./2.), a, b)
           
        if index == 'Ma':
           tmp = scipy.integrate.quad(lambda x: slope[i-1] / ((1./0.02247)*(6.91062-np.log(1015.-x)))**(3./2.), a, b)   
        a = fraction[i-1]-errx[0][i-1]
        b = fraction[i-1]+errx[1][i-1]
        
        molecular_weight[i-1] = 100 * (b-a) / tmp[0]
        
    return molecular_weight/1000
    
    
def density_cal(pc_xerr, tmp, substance):
    '''
    compute density for each PC
    '''
#    substance = ads.Oil.from_file(test_oil)
    
    factor_std = [3.89095068e-10, -1.80761223e-07, 4.47121572e-05, 8.25949995e-03]
    poly_fit_density = [4.38563364e-09, -5.17419970e-06, 2.24786983e-03, 5.44378167e-01]
    
    mass_frac_pc = pc_xerr[1][:] + pc_xerr[0][:]
    # print(substance.sub_samples[0].physical_properties.densities[0].density.unit)
    if substance.sub_samples[0].physical_properties.densities[0].density.unit == 'g/mL':
       den_obs = substance.sub_samples[0].physical_properties.densities[0].density.value
    elif substance.sub_samples[0].physical_properties.densities[0].density.unit == 'kg/m^3':
       den_obs = substance.sub_samples[0].physical_properties.densities[0].density.value / 1000.
    elif substance.sub_samples[0].physical_properties.densities[0].density.unit == 'g/cm^3': 
       den_obs = substance.sub_samples[0].physical_properties.densities[0].density.value    
    
    #tmp = bl_pc - 273.15
    den_pc_3 = poly_fit_density[0] * tmp**3 + poly_fit_density[1] * tmp**2 + poly_fit_density[2] * tmp + poly_fit_density[3]           
        
    factor_ini = factor_std[0] * tmp**3 + factor_std[1] * tmp**2 + factor_std[2] * tmp + factor_std[3]
     
    denominator = sum(factor_ini * mass_frac_pc * den_pc_3)

    numerator = sum(mass_frac_pc * den_pc_3)
                
    factor_3 = (den_obs - numerator) / denominator
    den_pc_3 = den_pc_3 * (1. + factor_3 * factor_ini) 
    
    return 1000. * den_pc_3

   
def viscosity_cal(pc_xerr, mw, tmp, substance):
    '''
    compute viscosity for each PC
    '''
#    substance = ads.Oil.from_file(test_oil)
    
    poly_fit_vis = [4.37216703e-08, -1.52957475e-05, 5.01984022e-03, -4.60879542e-01]
    vis_pc = poly_fit_vis[0] * tmp**3 + poly_fit_vis[1] * tmp**2 + poly_fit_vis[2] * tmp + poly_fit_vis[3]

    mass_frac_pc = pc_xerr[1][:] + pc_xerr[0][:]
    mol_frac_pc = mass_frac_pc / mw
    mol_frac_pc = mol_frac_pc / sum(mol_frac_pc)
                   
    total_vis_pc = sum(mol_frac_pc * vis_pc)
    
    if len(substance.sub_samples[0].physical_properties.kinematic_viscosities)>0:
       vis_measured = substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.value
    elif len(substance.sub_samples[0].physical_properties.dynamic_viscosities)>0:   
       vis_measured = np.log10(substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.value / substance.sub_samples[0].physical_properties.densities[0].density.value)

    factor_visc = vis_measured / total_vis_pc
    vis_pc = factor_visc * vis_pc              
    vis_pc = 10.0**vis_pc
    
    return vis_pc

    
def distillation_data(test_oil):
    '''
    extract distillation data from adios oil file 
    '''
    substance = ads.Oil.from_file(test_oil)

    dist = get_distillation_cuts(substance, temp_units='C')
    frac, temps = zip(*dist)
    frac = np.array(frac)
    temps = np.array(temps)
    if frac[-1] == 1:
        return frac, temps
    if substance.sub_samples[0].distillation_data.end_point is None:
        # extrapolation to obtain 100% loss !!!!! from data
        k = (temps[-1] - temps[0]) / (frac[-1] - frac[0])
        temp_100 = k * (1.0 - frac[-1]) + temps[-1]
      
        frac = np.append(frac, 1.)
        temps = np.append(temps, temp_100)    
        # extrapolation to obtain 100% loss
        # print(temps)
    elif substance.sub_samples[0].distillation_data.end_point.value is None:
        k = (temps[-1] - temps[0]) / (frac[-1] - frac[0])
        temp_100 = k * (1.0 - frac[-1]) + temps[-1]
        
        if substance.sub_samples[0].distillation_data.end_point.min_value is not None:
           temp_100 = max(temp_100, substance.sub_samples[0].distillation_data.end_point.min_value)
        
        frac = np.append(frac, 1.)
        temps = np.append(temps, temp_100)        
    else:
        frac = np.append(frac, 1.)
        temps = np.append(temps, substance.sub_samples[0].distillation_data.end_point.value)
    
    return frac, temps    
   
def pseudo_file(dir, bl, frac, mw, den_pc, density, ref_den, viscosity, ref_visc, api, test_oil, cut_point, Resolution = None):       
    '''
    This function is to create oil file for pseudo components
    inputs:
    1. bl is boling point of PCs
    2. frac is mass fraction of PCs
    3. mw is molecular weight of PCs 
    4. Resolution is the mass-fraction resolution
    '''
    fn = os.path.splitext(test_oil)
# open a file west_blend.json
    
    if Resolution is not None:
       filename = fn[0] + '_{0}_{1}.json'.format(int(Resolution), int(cut_point))
       variablename = fn[0] + '{0}_{1}'.format(int(Resolution), int(cut_point))
    else:
       filename = fn[0]+ '.json'
       variablename = fn[0]
       
    filepath = os.path.join(dir + '_pc', filename)      
# write content
    f = open(filepath, 'w')
#    f = open(filename, 'w')    
#    f.write(variablename)    
    f.write('{"api": ')
    f.write('{0},'.format(api))
    
    f.write(' "boiling_point": [')
    for i in range(0, len(bl)-1):
       f.write('{},\n'.format(bl[i]))
    f.write('{}],\n'.format(bl[-1]))
    
    f.write('"bullwinkle_fraction": 0.1937235,\n')
    
    f.write('"component_density": [')
    for i in range(0, len(den_pc)-1):
       f.write('{0}, \n'.format(den_pc[i]))
    f.write('{0}], \n'.format(den_pc[-1]))
    
    if len(density) > 1:
        f.write('"densities": [{0}, {1}],\n'.format(density[0], density[1]))
        f.write('"density_ref_temps": [{0}, {1}],\n'.format(ref_den[0] + 273.15, ref_den[1] + 273.15))
    else:
        f.write('"densities": [{0}],\n'.format(density[0]))
        f.write('"density_ref_temps": [{0}],\n'.format(ref_den[0] + 273.15))
        
    f.write('"density_weathering": [0.0, 0.0],\n')
    f.write('"emulsion_water_fraction_max": 0.9,\n')
    
    if len(viscosity) >1:
        f.write('"kvis": [{0}, {1}],\n'.format(viscosity[0], viscosity[1]))
        f.write('"kvis_ref_temps": [{0}, {1}],\n'.format(ref_visc[0] + 273.15, ref_visc[1] + 273.15))
    else:
        f.write('"kvis": [{0}],\n'.format(viscosity[0]))
        f.write('"kvis_ref_temps": [{0}],\n'.format(ref_visc[0] + 273.15))
    
    f.write('"kvis_weathering": [0.0, 0.0],\n')
    
    if len(bl) > 1:
        f.write('"mass_fraction": [')
        f.write('{},\n'.format(frac[0]))
        for i in range(1, len(bl)-1):
           f.write('{},\n'.format(frac[i]-frac[i-1]))
        f.write('{}],\n'.format(frac[-1]-frac[-2]))   
    else:
       f.write('"mass_fraction": [{}],\n'.format(frac[0]))
    f.write(' "molecular_weight": [')
    for i in range(0, len(mw)-1):
       f.write('{},\n'.format(mw[i]))
    f.write('{}],\n'.format(mw[-1]))
    
    
    f.write(' "name":')
    f.write(' "{}"'.format(variablename))
    f.write(',')
    f.write('\n')
    f.write(' "pour_point": 219.15,\n')
    
    f.write('"sara_type": [')
    for i in range(0, len(bl)-1):
       f.write('"Saturates",\n')
    f.write('"Asphaltenes"],\n')
    
    f.write('  "solubility": 0.0}')
    f.close()
    
    oil_file = json.load(open(filepath)) #filename))
    json.dump(oil_file, open(filepath,"w"), indent = 4)    
    return
# write content    

   
def bar_plot(bl, frac, bl_err, frac_err, filename = 'test-bar_50C.png'):
    '''
    bar plot for pseudo components
    '''
    for i in range(0, len(bl)):
            x0 = [bl[i]-bl_err[0][i], bl[i]+bl_err[1][i]]
            
            if i ==0:
               y0 = [frac[i], frac[i]]
            else:
               y0 = [frac[i]-frac[i-1], frac[i]-frac[i-1]]               
            l0, = plt.plot(x0, y0, 'k')
            
            x0 = [bl[i]-bl_err[0][i], bl[i]-bl_err[0][i]]
            if i ==0:
               y0 = [0, frac[i]]
            else:
               y0 = [0, frac[i]-frac[i-1]]
            l0, = plt.plot(x0, y0, 'k')
            
            x0 = [bl[i]+bl_err[1][i], bl[i]+bl_err[1][i]]
            if i ==0:
               y0 = [0, frac[i]]
            else:
               y0 = [0, frac[i]-frac[i-1]]
            l0, = plt.plot(x0, y0, 'k')
            
                       
    plt.xlabel('Temperature, C', fontsize=16)
    plt.ylabel('Mass fraction, %', fontsize=16)

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlim(min(bl), max(bl))
    plt.ylim(0.0, 1.0)
    plt.savefig(filename, bbox_inches='tight')
    plt.close() 

    return   
   
def distillation_plot(dir, frac, temps, pc_frac, pc_bl, pc_yerr, pc_xerr, filename):
    '''
    distillation data plot
    '''
    fontsize0 = 24
    filepath = os.path.join(dir + '_pc', filename) 
    
    fig, ax = plt.subplots()
#    l0, = plt.plot(frac, temps, marker = 'o', linestyle = 'None')
#    l3  = plt.scatter(pc_frac, pc_bl - 273.15, s=80., c = 'r')
    l0, = ax.plot(frac, temps, 'k', linewidth=2.0, alpha=0.8)
    l2  = ax.errorbar(pc_frac, pc_bl - 273.15, pc_yerr, pc_xerr, ecolor='y', fmt="o", c='r') #ls='None') #, 
#    plt.legend((l0, l2), ['distillation data', 'pseudocomponents'], loc='upper left')
#    plt.xlabel('Mass fraction', fontsize = fontsize0)
#    plt.ylabel('Boiling point, ($^\circ$C)', fontsize = fontsize0, offsetText = fontsize0)
    
    ax.set_xlabel('Mass fraction', fontsize = fontsize0)
    ax.set_ylabel('Boiling point, $^\circ$C', fontsize = fontsize0)
    
    #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    #ax.xticks(fontsize = fontsize0)
    #ax.yticks(fontsize = fontsize0)
    ax.set_xticks(np.arange(0, 1.2, 0.2))
    ax.tick_params(axis='both', which='major', labelsize=fontsize0)
    #ax.xlim(0, 1.05)
    #y_axis = np.concatenate((temps, pc_bl-273.15), axis=0)
    #ax.ylim(min(y_axis)-30., max(y_axis)+30.)
    plt.savefig(filepath, bbox_inches='tight') #filename
    plt.close() 

    return   
   
def make_pc(dir, res, cp):
    files = glob.glob(dir + '/' + "*.json")
    #test_oil = [dbs.Oil.from_file(file) for i, file in enumerate(files)]
    #for i in range(0, len(files)):
    #    print(files[i])

    for id_no in range(0, len(files)):
        substance = ads.Oil.from_file(files[id_no])
        test_oil = os.path.basename(files[id_no])
        density = []
        ref_den = []
        viscosity = []
        ref_visc = []
        #print(test_oil)
        #if len(substance.sub_samples[0].distillation_data.cuts)>0:
        #    print(substance.metadata.name, substance.oil_id, substance.metadata.API) #substance.metadata.name, substance.oil_id, substance.metadata.API) #   
         
    # step 1: complete distillation data
            frac, temps = distillation_data(files[id_no])
            
            # step 2: construct pseudo components
            bl_pc,  frac_pc,  sl_pc5, res_pc = pseudo6(temps, frac, cut_point = cp, Resolution = res)
            pc_yerr,  pc_xerr =  pseudo_error(bl_pc  - 273.15, frac_pc,  temps, frac, cut_point = cp)
            #for i in range(0, len(frac_pc)):
            #    print(pc_xerr[0][i], pc_xerr[1][i])
            # step 3: compute molecular weight
            mw_MP = molecular_weight1(bl_pc - 273.15, index = 'Mp') #(pc_yerr, bl_pc - 273.15, index = 'Mp')
            mw_MN = molecular_weight1(bl_pc - 273.15, index = 'Mn') #(pc_yerr, bl_pc - 273.15, index = 'Mn')
            mw_MA = molecular_weight1(bl_pc - 273.15, index = 'Ma') #(pc_yerr, bl_pc - 273.15, index = 'Ma')

            mw = 1000. * (mw_MP + mw_MN + mw_MA) / 3.

            # step 4: compute density
            den_pc = density_cal(pc_xerr, bl_pc - 273.15, substance)

            # step 5: compute viscosity
    #        visc_pc = viscosity_cal(pc_xerr, mw, bl_pc - 273.15, substance)

            # step 6: import density vs viscosity
            if substance.sub_samples[0].physical_properties.densities[0].density.unit == 'g/mL':
                den1 = 1000 * substance.sub_samples[0].physical_properties.densities[0].density.value
                ref1 = substance.sub_samples[0].physical_properties.densities[0].ref_temp.convert_to('C').value
            elif substance.sub_samples[0].physical_properties.densities[0].density.unit == 'kg/m^3':
                den1 = substance.sub_samples[0].physical_properties.densities[0].density.value
                ref1 = substance.sub_samples[0].physical_properties.densities[0].ref_temp.convert_to('C').value  
            elif substance.sub_samples[0].physical_properties.densities[0].density.unit == 'g/cm^3': 
                den1 = 1000 * substance.sub_samples[0].physical_properties.densities[0].density.value
                ref1 = substance.sub_samples[0].physical_properties.densities[0].ref_temp.convert_to('C').value             
            
            density = [den1,]
            ref_den = [ref1,]
            
            if len(substance.sub_samples[0].physical_properties.densities) > 1:
               if substance.sub_samples[0].physical_properties.densities[0].density.unit == 'g/mL':
                   den2 = 1000 * substance.sub_samples[0].physical_properties.densities[1].density.value
                   ref2 = substance.sub_samples[0].physical_properties.densities[1].ref_temp.convert_to('C').value
               elif substance.sub_samples[0].physical_properties.densities[1].density.unit == 'kg/m^3':
                   den2 = substance.sub_samples[0].physical_properties.densities[1].density.value
                   ref2 = substance.sub_samples[0].physical_properties.densities[1].ref_temp.convert_to('C').value

               elif substance.sub_samples[0].physical_properties.densities[1].density.unit == 'g/cm^3': 
                   den2 = 1000 * substance.sub_samples[0].physical_properties.densities[1].density.value
                   ref2 = substance.sub_samples[0].physical_properties.densities[1].ref_temp.convert_to('C').value             
            
               density = np.append(density, den2)
               ref_den = np.append(ref_den, ref2)
            #print('llleeeooo', ref_den, substance.sub_samples[0].physical_properties.densities[0].ref_temp.convert_to('C').value)
            #print(substance.sub_samples[0].physical_properties.kinematic_viscosities) 
            #print(substance.sub_samples[0].physical_properties.densities[0].density.unit)
            
            if len(substance.sub_samples[0].physical_properties.kinematic_viscosities) > 0:
                #print(substance.sub_samples[0].physical_properties.kinematic_viscosities[0].viscosity.unit)         
                if substance.sub_samples[0].physical_properties.kinematic_viscosities[0].viscosity.unit == 'm^2/s':
                   visc1 = substance.sub_samples[0].physical_properties.kinematic_viscosities[0].viscosity.value
                   ref1 = substance.sub_samples[0].physical_properties.kinematic_viscosities[0].ref_temp.convert_to('C').value
                
                if substance.sub_samples[0].physical_properties.kinematic_viscosities[0].viscosity.unit == 'cSt':
                   visc1 = substance.sub_samples[0].physical_properties.kinematic_viscosities[0].viscosity.value / 1.e6
                   ref1 = substance.sub_samples[0].physical_properties.kinematic_viscosities[0].ref_temp.convert_to('C').value
                
                viscosity = [visc1,]
                ref_visc = [ref1,]

                if len(substance.sub_samples[0].physical_properties.kinematic_viscosities) > 1:
                    visc2 = substance.sub_samples[0].physical_properties.kinematic_viscosities[1].viscosity.value
                    ref2 = substance.sub_samples[0].physical_properties.kinematic_viscosities[1].ref_temp.convert_to('C').value   
                    
                    if substance.sub_samples[0].physical_properties.kinematic_viscosities[0].viscosity.unit == 'cSt':
                       visc2 = substance.sub_samples[0].physical_properties.kinematic_viscosities[1].viscosity.value / 1.e6
                       ref2 = substance.sub_samples[0].physical_properties.kinematic_viscosities[1].ref_temp.convert_to('C').value
                    
                    viscosity = np.append(viscosity, visc2)
                    ref_visc = np.append(ref_visc, ref2)
            
            #print(substance.sub_samples[0].physical_properties.dynamic_viscosities)        
            if len(substance.sub_samples[0].physical_properties.dynamic_viscosities) > 0:
                #print(substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.unit)         
                if substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.unit == 'kg/(m s)':
                   visc1 = (substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.value / den1)
                   ref1 = substance.sub_samples[0].physical_properties.dynamic_viscosities[0].ref_temp.convert_to('C').value
                
                if substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.unit == 'mPa.s':
                   visc1 = (substance.sub_samples[0].physical_properties.dynamic_viscosities[0].viscosity.value / den1) / 1000.
                   ref1 = substance.sub_samples[0].physical_properties.dynamic_viscosities[0].ref_temp.convert_to('C').value
                   
                viscosity = [visc1,]
                ref_visc = [ref1,]
                
                if len(substance.sub_samples[0].physical_properties.dynamic_viscosities) > 1:
                   if substance.sub_samples[0].physical_properties.dynamic_viscosities[1].viscosity.unit == 'kg/(m s)':
                     visc2 = (substance.sub_samples[0].physical_properties.dynamic_viscosities[1].viscosity.value / density[-1])
                     ref2 = substance.sub_samples[0].physical_properties.dynamic_viscosities[1].ref_temp.convert_to('C').value   
                   
                   if substance.sub_samples[0].physical_properties.dynamic_viscosities[1].viscosity.unit == 'mPa.s':
                     visc2 = (substance.sub_samples[0].physical_properties.dynamic_viscosities[1].viscosity.value / density[-1]) / 1000.
                     ref2 = substance.sub_samples[0].physical_properties.dynamic_viscosities[1].ref_temp.convert_to('C').value
                   
                   viscosity = np.append(viscosity, visc2)
                   ref_visc = np.append(ref_visc, ref2)


            api = substance.metadata.API
            pseudo_file(dir, bl_pc, frac_pc, mw, den_pc, density, ref_den, viscosity, ref_visc, api, test_oil, cut_point = cp, Resolution = res)

            f0 = os.path.splitext(test_oil)
            fn_0 = f0[0]+ '_bar.png'
            fn_1 = f0[0]+ '_distillation._{0}_{1}.png'.format(int(res), int(cp))

    #        bar_plot(bl_pc - 273.15, frac_pc, pc_yerr, pc_xerr, fn_0)
            distillation_plot(dir, frac, temps, frac_pc, bl_pc, pc_yerr, pc_xerr, fn_1)
                
    return    
 
 
def ran_evaporation(dir):
    
    num_elems = 1
    temperature = 25.0 + 273.15
    time_step = 900.0
    wind_speed = 5.0
    period = 240.0
    start_time = gs.asdatetime("2015-05-14")
    end_time = gs.asdatetime(start_time) #+ gs.hours(12)
    fontsize0 = 24
      
    files = glob.glob(dir + '_pc' + '/' + "*.json")
    basenames = []
    [basenames.append(os.path.basename(file)[0:7]) for file in files]
    basenames = list(set(basenames))
    
    scenario1 = ['_10_400.json'] #  ['_1_400.json', '_5_400.json', '_10_400.json', '_20_400.json', '_30_400.json', '_50_400.json'] #
    scenario2 = ['_20_400.json', '_20_500.json', '_20_600.json']

    stat_1 = np.zeros((960,len(basenames),len(scenario1)))
    stat_2 = np.zeros((960,len(basenames),len(scenario1)))
    
    stat_3 = np.zeros((960,len(basenames),len(scenario2)))
    stat_4 = np.zeros((960,len(basenames),len(scenario2)))
    
    file0 = open(dir + '_pc' + '/' + 'Oil_NameList.txt', 'w+')
    
    for id_no in range(0, len(basenames)):
        # evaporation test for resolution without spreading
        file0.write(basenames[id_no])
        file0.write('\n')
        print(basenames[id_no])
        
        f = []
        for case_no in range(0, len(scenario1)):
            oil_name =  dir + '_pc' + '/' + basenames[id_no] + scenario1[case_no]
            #print(oil_name)
            test_oil = json.load(open(oil_name))
            substance = gs.GnomeOil(**test_oil)
            Test_object1 = TestEvaporation()
            xpiece30, ypiece30, zpiece30, qpiece30 = Test_object1.full_test(period, 1000, time_step, start_time, end_time, temperature, substance, num_elems, wind_speed, sp=False,  evap=True) 
            '''
            # output mass fraction for each PCs
            # output mass fraction for each PCs
            plt.xscale("log")
            for i in range(1, qpiece30.shape[1]+1):
                l1 = plt.plot(xpiece30,qpiece30[:,i-1]/qpiece30[0,i-1], label = 'pc-{}'.format(i)) #, marker ="o")
                
            plt.legend(bbox_to_anchor = (1.5, 0.6))
            plt.xlabel('Time, h', fontsize=16)
            plt.ylabel('Mass fraction', fontsize=16)
            #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            #plt.xlim(1./(3600.), max(x0))
            plt.xlim(1./(3600.), 240.0)
            plt.ylim(0.0, 1.1)
            plt.savefig('AMOP-test-evaporation_PseudoComponents_20C.png', bbox_inches='tight')
            plt.close() 
            # output mass fraction for each PCs
            # output mass fraction for each PCs
            '''
            l1, = plt.plot(xpiece30, ypiece30)
            f.append(l1)
            stat_1[:,id_no,case_no] = np.array(ypiece30)
            #print(stat_1[:,id_no,case_no])
        # create a method here to do the statistics
        #for i in range(0, 960):
        
        #plt.legend((f[0], f[1], f[2], f[3], f[4], f[5]), ['RES-1  C', 'RES-5  C', 'RES-10 C', 'RES-20 C', 'RES-30 C', 'RES-50 C'], fontsize=fontsize0)
        plt.xlabel('Time, h', fontsize=fontsize0)
        plt.ylabel('Mass fraction', fontsize=fontsize0)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.xticks(fontsize = fontsize0)
        plt.yticks(fontsize = fontsize0)
        plt.xlim(0, 1) #240)
        plt.ylim(0., 1.0)
        plt.savefig(dir + '_pc' + '/' + 'test-evaporation_RES_' + basenames[id_no] + '.png', bbox_inches='tight')
        plt.close()
        
        '''
        # evaporation test for resolution with spreading
        f = []
        for case_no in range(0, len(scenario1)):
            oil_name =  dir + '_pc' + '/' + basenames[id_no] + scenario1[case_no]
            #print(oil_name)
            test_oil = json.load(open(oil_name))
            substance = gs.GnomeOil(**test_oil)
            Test_object1 = TestEvaporation()
            xpiece30, ypiece30, zpiece30, qpiece30 = Test_object1.full_test(period, 1000, time_step, start_time, end_time, temperature, substance, num_elems, wind_speed, sp=True,  evap=True) 
            l1, = plt.plot(xpiece30, ypiece30)
            f.append(l1)
            stat_2[:,id_no,case_no] = np.array(ypiece30)             
             
        #plt.legend((f[0], f[1], f[2], f[3], f[4], f[5]), ['RES-1  C', 'RES-5  C', 'RES-10 C', 'RES-20 C', 'RES-30 C', 'RES-50 C'])
        plt.xlabel('Time, h', fontsize=fontsize0)
        plt.ylabel('Mass fraction', fontsize=fontsize0)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.xticks(fontsize = fontsize0)
        plt.yticks(fontsize = fontsize0)
        plt.xlim(0, 240)
        plt.ylim(0., 1.0)
        plt.savefig(dir + '_pc' + '/' + 'test-evaporation_RES_spreading_' + basenames[id_no] + '.png', bbox_inches='tight')
        plt.close()
        
        # evaporation test for cutoff without spreading
        f = []
        for case_no in range(0, len(scenario2)):
            oil_name =  dir + '_pc' + '/' + basenames[id_no] + scenario2[case_no]
            #print(oil_name)
            test_oil = json.load(open(oil_name))
            substance = gs.GnomeOil(**test_oil)
            Test_object1 = TestEvaporation()
            xpiece30, ypiece30, zpiece30, qpiece30 = Test_object1.full_test(period, 1000, time_step, start_time, end_time, temperature, substance, num_elems, wind_speed, sp=False,  evap=True) 
            l1, = plt.plot(xpiece30, ypiece30)
            f.append(l1)
            stat_3[:,id_no,case_no] = np.array(ypiece30)             
             
        plt.legend((f[0], f[1], f[2]), ['Cutoff-400 C', 'Cutoff-500 C', 'Cutoff-600 C'])
        plt.xlabel('Time, h', fontsize=fontsize0)
        plt.ylabel('Mass fraction', fontsize=fontsize0)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.xticks(fontsize = fontsize0)
        plt.yticks(fontsize = fontsize0)
        plt.xlim(0, 240)
        plt.ylim(0., 1.0)
        plt.savefig(dir + '_pc' + '/' + 'test-evaporation_CUTOFF_' + basenames[id_no] + '.png', bbox_inches='tight')
        plt.close()
        
        # evaporation test for cutoff with spreading
        f = []
        for case_no in range(0, len(scenario2)):
            oil_name =  dir + '_pc' + '/' + basenames[id_no] + scenario2[case_no]
            #print(oil_name)
            test_oil = json.load(open(oil_name))
            substance = gs.GnomeOil(**test_oil)
            Test_object1 = TestEvaporation()
            xpiece30, ypiece30, zpiece30, qpiece30 = Test_object1.full_test(period, 1000, time_step, start_time, end_time, temperature, substance, num_elems, wind_speed, sp=True,  evap=True) 
            l1, = plt.plot(xpiece30, ypiece30)
            f.append(l1)
            stat_4[:,id_no,case_no] = np.array(ypiece30)              
             
        plt.legend((f[0], f[1], f[2]), ['Cutoff-400 C', 'Cutoff-500 C', 'Cutoff-600 C'])
        plt.xlabel('Time, h', fontsize=fontsize0)
        plt.ylabel('Mass fraction', fontsize=fontsize0)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.xticks(fontsize = fontsize0)
        plt.yticks(fontsize = fontsize0)
        plt.xlim(0, 240)
        plt.ylim(0., 1.0)
        plt.savefig(dir + '_pc' + '/' + 'test-evaporation_CUTOFF_spreading_' + basenames[id_no] + '.png', bbox_inches='tight')
        plt.close()
        
        
    # output results to text files
    file1 = open(dir + '_pc' + '/' + 'evaporation-RES-NOspreading.txt', 'w+')
    file2 = open(dir + '_pc' + '/' + 'evaporation-RES-Spreading.txt', 'w+')
    
    file3 = open(dir + '_pc' + '/' + 'evaporation-CUT-NOspreading.txt', 'w+')
    file4 = open(dir + '_pc' + '/' + 'evaporation-CUT-Spreading.txt', 'w+')
    
    for i in range(0, stat_1.shape[1]):
        for j in range(1, stat_1.shape[2]):
            content = str(np.mean(np.abs(stat_1[:,i,j] - stat_1[:,i,0]))) 
            file1.write(content)
            file1.write('  ')

            content = str(np.mean(np.abs(stat_2[:,i,j] - stat_2[:,i,0]))) 
            file2.write(content)
            file2.write('  ')
            
        file1.write('\n')
        file2.write('\n')
    
    for i in range(0, stat_3.shape[1]):
        for j in range(1, stat_3.shape[2]):
            content = str(np.mean(np.abs(stat_3[:,i,j] - stat_3[:,i,0]))) 
            file3.write(content)
            file3.write('  ')

            content = str(np.mean(np.abs(stat_4[:,i,j] - stat_4[:,i,0]))) 
            file4.write(content)
            file4.write('  ')
            
        file3.write('\n')
        file4.write('\n')    
    # output results to text files
    '''
    return    

'''
dir = [r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/AD',
       r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/EC',
       r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/EX',
       r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/NO']
for i in range(0, len(dir)):
    make_pc(dir[i], res=20., cp=400.)
    make_pc(dir[i], res=20., cp=500.)
    make_pc(dir[i], res=20., cp=600.)
'''
    

# Step 1 ------ construct pseudo components for all types of oil in adios oil database
dir = [#r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/1_Crude_Oil_NOS/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/2_Tight_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/3_Condensate/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/4_Bitumen_Blend/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/5_Bitumen/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/6_Refined_Product_NOS/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/7_Fuel_Oil_NOS/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/8_Distillate_Fuel_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/9_Residual_Fuel_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/10_Refinery_Intermediate/New folder (2)',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/11_Solvent/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/12_Bio_fuel_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/13_Bio_Petro_Fuel_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/14_Natural_Plant_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/15_Lube_Oil/New folder',
       r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/16_Dielectric_Oil/New folder',
       #r'C:/Users/leo.geng/Pygnome/gnome_tech_doc/validation/PC_Construction/17_Other/New folder'
       ]

for i in range(0, 1): #len(dir)):
#    print(dir[i])
    make_pc(dir[i], res=1., cp=400.)
#    make_pc(dir[i], res=5., cp=400.)
#    make_pc(dir[i], res=10., cp=400.)
#    make_pc(dir[i], res=30., cp=400.)
#    make_pc(dir[i], res=50., cp=400.)    
#    make_pc(dir[i], res=20., cp=400.)
#    make_pc(dir[i], res=20., cp=500.)
#    make_pc(dir[i], res=20., cp=600.)
    
# step 2 ------ run evaporation module in PyGNOME to test optimal set of PCs
#for i in range(0, len(dir)):
#    ran_evaporation(dir[i]) 
    
#make_pc(dir[0], res=20., cp=400.)
#ran_evaporation(dir[0])






















    
