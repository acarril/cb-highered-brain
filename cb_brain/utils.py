import random

def add_random_index(lst:list, index_name:str='index') -> list:
    """Add random index to each element of a list of dictionaries

    Args:
        lst (list): list of dictionaries
        index_name (str, optional): name (key) of index; defaults to 'index'.

    Returns:
        list: updated list with index
    """    
    indices = [i for i in range(len(lst))]
    random.shuffle(indices)
    return [dict(item, **{index_name:indices[idx]}) for idx, item in enumerate(lst)]


def select_random_brain_id(brain_id_lst:list=None) -> str:
    brain_names = ['Random', 'EconMatriculations', 'ML'] # don't work: 'Dynamic', 'EconInteractions'
    brain_constraints = ['Unrestricted', 'Diverse', 'Targeted']
    if not brain_id_lst:
        brain_id_lst = [f'{x}-{y}' for x in brain_names for y in brain_constraints]
    return random.choice(brain_id_lst)

# {'Random': {'Unrestricted': 1, 'Diverse': 2, 'Targeted': 3},
#  'EconMatriculations': {'Unrestricted': 4, 'Diverse': 5, 'Targeted': 6},
#  'EconInteractions': {'Unrestricted': 7, 'Diverse': 8, 'Targeted': 9},
#  'Dynamic': {'Unrestricted': 10, 'Diverse': 11, 'Targeted': 12},
#  'ML': {'Unrestricted': 13, 'Diverse': 14, 'Targeted': 15}}



def compute_2020_inv_percentile(puntaje:int) -> int:
    """Compute inverse percentile (i.e. (1 - percentile)) for a given score considering 2020-2 distribution of scores

    Args:
        puntaje (int): saber11 score

    Returns:
        int: inverse percentile (i.e. (1 - percentile)); 0 if out of range we care about
    """    
    d = {
        274: 70,
        276: 71,
        277: 72,
        279: 73,
        281: 74,
        282: 75,
        284: 76,
        286: 77,
        288: 78,
        290: 79,
        292: 80,
        293: 81,
        295: 82,
        298: 83,
        300: 84,
        302: 85,
        305: 86,
        307: 87,
        310: 88,
        312: 89,
        315: 90,
        318: 91,
        322: 92,
        325: 93,
        330: 94,
        334: 95,
        340: 96,
        346: 97,
        354: 98,
        367: 99,
        999: 100
    }
    percentile = min([val-1 for key, val in d.items() if key > puntaje])
    if percentile == 69:
        return 0
    else:
        return 100 - percentile

def compute_2020_decile(puntaje:int) -> int:
    """Compute inverse percentile (i.e. (1 - percentile)) for a given score considering 2020-2 distribution of scores

    Args:
        puntaje (int): saber11 score

    Returns:
        int: inverse percentile (i.e. (1 - percentile)); 0 if out of range we care about
    """    
    d = {
        0: 1,
        187: 2,         
        203: 3,         
        218: 4,         
        232: 5,         
        245: 6,         
        259: 7,         
        274: 8,         
        292: 9,         
        315: 10             
    }

    percentile = min([val-1 for key, val in d.items() if key > puntaje])
    if percentile == 69:
        return 0
    else:
        return 100 - percentile


def process_wage_deviation(wage_deviation):
    f = float(wage_deviation)
    if (f < 0): # subestimacion
        return abs(f)
    elif (f > 0):
        return 1/f
    else:
        return 1


def calculador_pago_mensual(pct_pago_durante):
    pct_to_attrs = {
        0: {
            'plazo_amort': 96,
            'cuota_estudios': '$0',
            'cuota_amort': '$468.000 - $646.000'
        },
        10: {
            'plazo_amort': 96,
            'cuota_estudios': '$83.000 - 86.000',
            'cuota_amort': '$421.000 - $582.000'
        },
        25: {
            'plazo_amort': 96,
            'cuota_estudios': '$209.000 - 215.000',
            'cuota_amort': '$352.000 - $485.000'
        },
        30: {
            'plazo_amort': 72,
            'cuota_estudios': '$251.000 - 258.000',
            'cuota_amort': '$431.000 - $551.000'
        },
        40: {
            'plazo_amort': 72,
            'cuota_estudios': '$335.000 - 342.000',
            'cuota_amort': '$545.000 - $634.000'
        },
        60: {
            'plazo_amort': 48,
            'cuota_estudios': '$502.000 - 512.000',
            'cuota_amort': '$363.000 - $415.000'
        },
        100: {
            'plazo_amort': 0,
            'cuota_estudios': '$837.000 - 854.000',
            'cuota_amort': '$0'
        }
    }
    return pct_to_attrs[pct_pago_durante]