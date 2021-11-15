from random import shuffle

def add_random_index(lst:list, index_name:str='index') -> list:
    """Add random index to each element of a list of dictionaries

    Args:
        lst (list): list of dictionaries
        index_name (str, optional): name (key) of index; defaults to 'index'.

    Returns:
        list: updated list with index
    """    
    indices = [i for i in range(len(lst))]
    shuffle(indices)
    return [dict(item, **{index_name:indices[idx]}) for idx, item in enumerate(lst)]

