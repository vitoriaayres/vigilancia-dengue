import httpx 
import pandas as pd 

URL_ALERTA_MUNICIPIO= "https://info.dengue.mat.br/api/alertcity" 
DOENCAS= ('dengue', 'chikungunya', 'zika')

COLUNAS= {
    'SE': 'semana', 
    'data_iniSE': 'inicio_semana', 
    'casos': 'casos', 
    'casos_est': 'casos_estimados', 
    'p_inc100k': 'incidencia_100k',
    'Rt': 'rt', 
    'nivel': 'nivel_alerta', 
    'pop': 'populacao',
}
class ErroInfoDengue(Exception): 
    pass 

def buscar_serie(
        geocodigo: int, 
        doenca: str, 
        ano_inicio: int, 
        ano_fim: int, 
        cliente: httpx.Client | None= None,
) -> pd.DataFrame: 
    if doenca not in DOENCAS: 
        raise ValueError(f'DOENÇA INVÁLIDA: {doenca}. USE UMA DE {DOENCAS}')

    parametros= {
        'geocode': geocodigo, 
        'disease': doenca, 
        'format': 'json', 
        'ew_start': 1, 
        'ew_end': 53, 
        'ey_start': ano_inicio, 
        'ey_end': ano_fim,
    }
    https= cliente or httpx.Client(timeout=30)
    try:
        resposta = https.get(URL_ALERTA_MUNICIPIO, params=parametros)
        resposta.raise_for_status()
    except httpx.HTTPError as erro:
        raise ErroInfoDengue(f"falha ao consultar o InfoDengue: {erro}") from erro
    finally:
        if cliente is None:
            https.close()

    registros = resposta.json()
    if not registros:
        raise ErroInfoDengue(f"série vazia para o geocódigo {geocodigo} entre {ano_inicio} e {ano_fim}")
    return normalizar(pd.DataFrame(registros))

def normalizar(bruto: pd.DataFrame) -> pd.DataFrame: 
    ausentes= set(COLUNAS) - set(bruto.columns)
    if ausentes: 
        raise ErroInfoDengue(f' A API MUDOU: COLUNAS AUSENTES: {sorted(ausentes)}')
    serie= bruto[list(COLUNAS)].rename(columns= COLUNAS)
    serie['inicio_semana']= converter_data(serie['inicio_semana'])
    serie['ano']= serie['semana'] // 100 
    serie['semana_epi']= serie['semana'] % 100
    return serie.sort_values('semana').reset_index(drop=True)

def converter_data(coluna: pd.Series) -> pd.Series: 
    if pd.api.types.is_numeric_dtype(coluna): 
        return pd.to_datetime(coluna, unit='ms')
    return pd.to_datetime(coluna) 

    
