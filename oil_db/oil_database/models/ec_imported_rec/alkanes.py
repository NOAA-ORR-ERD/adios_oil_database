#
# Model class for Environment Canada's n-Alkane
# oil properties.
#
from pydantic import BaseModel, constr


class ECNAlkanes(BaseModel):
    '''
        n-Alkanes (ug/g oil) (ESTS 2002a)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    pristane_ug_g: float = None
    phytane_ug_g: float = None
    c8_ug_g: float = None
    c9_ug_g: float = None
    c10_ug_g: float = None
    c11_ug_g: float = None
    c12_ug_g: float = None
    c13_ug_g: float = None
    c14_ug_g: float = None
    c15_ug_g: float = None
    c16_ug_g: float = None
    c17_ug_g: float = None
    c18_ug_g: float = None
    c19_ug_g: float = None
    c20_ug_g: float = None
    c21_ug_g: float = None
    c22_ug_g: float = None
    c23_ug_g: float = None
    c24_ug_g: float = None
    c25_ug_g: float = None
    c26_ug_g: float = None
    c27_ug_g: float = None
    c28_ug_g: float = None
    c29_ug_g: float = None
    c30_ug_g: float = None
    c31_ug_g: float = None
    c32_ug_g: float = None
    c33_ug_g: float = None
    c34_ug_g: float = None
    c35_ug_g: float = None
    c36_ug_g: float = None
    c37_ug_g: float = None
    c38_ug_g: float = None
    c39_ug_g: float = None
    c40_ug_g: float = None
    c41_ug_g: float = None
    c42_ug_g: float = None
    c43_ug_g: float = None
    c44_ug_g: float = None

    def __repr__(self):
        return ('<ECNAlkanes('
                'pristane={0.pristane_ug_g}, '
                'phytane={0.phytane_ug_g}, '
                'c8={0.c8_ug_g}, '
                'c9={0.c9_ug_g}, '
                'c10={0.c10_ug_g}, '
                'c11={0.c11_ug_g}, '
                'c12={0.c12_ug_g}, '
                'c13={0.c13_ug_g}, '
                'c14={0.c14_ug_g}, '
                'c15={0.c15_ug_g}, '
                'c16={0.c16_ug_g}, '
                'c17={0.c17_ug_g}, '
                'c18={0.c18_ug_g}, '
                'c19={0.c19_ug_g}, '
                'c20={0.c20_ug_g}, '
                'c21={0.c21_ug_g}, '
                'c22={0.c22_ug_g}, '
                'c23={0.c23_ug_g}, '
                'c24={0.c24_ug_g}, '
                'c25={0.c25_ug_g}, '
                'c26={0.c26_ug_g}, '
                'c27={0.c27_ug_g}, '
                'c28={0.c28_ug_g}, '
                'c29={0.c29_ug_g}, '
                'c30={0.c30_ug_g}, '
                'c31={0.c31_ug_g}, '
                'c32={0.c32_ug_g}, '
                'c33={0.c33_ug_g}, '
                'c34={0.c34_ug_g}, '
                'c35={0.c35_ug_g}, '
                'c36={0.c36_ug_g}, '
                'c37={0.c37_ug_g}, '
                'c38={0.c38_ug_g}, '
                'c39={0.c39_ug_g}, '
                'c40={0.c40_ug_g}, '
                'c41={0.c41_ug_g}, '
                'c42={0.c42_ug_g}, '
                'c43={0.c43_ug_g}, '
                'c44={0.c44_ug_g}, '
                'weathering={0.weathering})>'
                .format(self))
