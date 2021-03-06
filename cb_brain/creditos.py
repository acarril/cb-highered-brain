import pandas as pd

def gen_df_creditos():
    id_credito = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35
    ]
    req_estrato_max = [
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        6,
        6,
        6,
        6,
        3,
        6,
        3,
        6,
        6,
        6,
        3,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        3,
        3,
        3,
        6
    ]
    req_sisben_bajoC8 = [
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
    ]
    req_notas = [
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        34,
        30
    ]
    req_saber11 = [
        300,
        210,
        270,
        290,
        290,
        290,
        290,
        290,
        290,
        260,
        240,
        240,
        240,
        260,
        240,
        210,
        240,
        240,
        210,
        270,
        260,
        240,
        240,
        240,
        260,
        240,
        240,
        240,
        240,
        0,
        0,
        210,
        210,
        210,
        240
    ]
    req_saber11_indigenas = [
        300,
        210,
        270,
        200,
        200,
        200,
        200,
        200,
        200,
        260,
        240,
        240,
        240,
        260,
        240,
        200,
        240,
        240,
        200,
        270,
        260,
        240,
        240,
        240,
        260,
        240,
        240,
        240,
        240,
        0,
        0,
        200,
        200,
        200,
        240
    ]
    d = {
        'id_credito': id_credito,
        'req_estrato_max': req_estrato_max,
        'req_sisben_bajoC8': req_sisben_bajoC8,
        'req_notas': req_notas,
        'req_saber11': req_saber11,
        'req_saber11_indigenas': req_saber11_indigenas
    }
    return pd.DataFrame(data=d)

def gen_oferta_creditos(estrato, sisben_bajoC8, saber11, nota = 34, indigena=False):
    df = gen_df_creditos()
    mask1 = (df.req_estrato_max >= estrato) & (df.req_sisben_bajoC8 <= sisben_bajoC8) & (df.req_notas <= nota)
    if not indigena:
        mask2 = (df.req_saber11 <= saber11)
    else:
        mask2 = (df.req_saber11_indigenas <= saber11)
    mask = mask1 & mask2
    return df['id_credito'][mask].tolist()