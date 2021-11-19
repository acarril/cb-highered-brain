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


def select_random_brain_id(brain_id_lst:list=['ML-Targeted', 'ML-Diverse']) -> str:
    return random.choice(brain_id_lst)

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

              

