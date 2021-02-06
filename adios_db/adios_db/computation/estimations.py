"""
estimations for filling out the missing properties of an
oil record
"""

import numpy as np

def pour_point_from_kvis(ref_kvis, ref_temp_k):
    '''
        Source: Adios2

        If we have an oil kinematic viscosity at a reference temperature,
        then we can estimate what its pour point might be.
    '''
    c_v1 = 5000.0
    ref_kvis = np.array(ref_kvis)
    ref_temp_k = np.array(ref_temp_k)

    T_pp = (c_v1 * ref_temp_k) / (c_v1 - ref_temp_k * np.log(ref_kvis))

    return T_pp


def flash_point_from_bp(temp_k):
    '''
        Source: Reference: Chang A., K. Pashakanti, and Y. Liu (2012),
                           Integrated Process Modeling and Optimization,
                           Wiley Verlag.

    '''
    temp_k = np.array(temp_k)
    return 117.0 + 0.69 * temp_k


def flash_point_from_api(api):
    '''
        Source: Reference: Chang A., K. Pashakanti, and Y. Liu (2012),
                           Integrated Process Modeling and Optimization,
                           Wiley Verlag.

    '''
    api = np.array(api)
    return 457.0 - 3.34 * api

