#
# Model class for Environment Canada's headspace
# oil properties.
#
from pydantic import BaseModel, constr


class ECHeadspace(BaseModel):
    '''
        Headspace Analysis (mg/g oil) (ESTS 2002b)
    '''
    weathering: float = 0.0
    method: constr(max_length=16) = None

    n_c5_mg_g: float = None
    n_c6_mg_g: float = None
    n_c7_mg_g: float = None
    n_c8_mg_g: float = None

    c5_group_mg_g: float = None
    c6_group_mg_g: float = None
    c7_group_mg_g: float = None

    def __repr__(self):
        return ('<{0.__class__.__name__}('
                'n_c5={0.n_c5_mg_g}, '
                'n_c6={0.n_c6_mg_g}, '
                'n_c7={0.n_c7_mg_g}, '
                'n_c8={0.n_c8_mg_g}, '
                'c5_group={0.c5_group_mg_g}, '
                'c6_group={0.c6_group_mg_g}, '
                'c7_group={0.c7_group_mg_g}, '
                'w={0.weathering})>'
                .format(self))
