from dataclasses import dataclass 
import pandas as pd 

MINIMO_ANOS_HISTORICO= 3 
@dataclass(frozen= True)
class Avaliacao: 
    semana: int
    incidencia: float 
    q1: float
    mediana: float
    q3: float
    zona: str 
    semanas_acima_q3: int
    rt: float 

def calcular_canal(
        serie: pd.DataFrame, 
        ano_referencia: int, 
        anos_historico: int= 5, 
        excluir_anos: tuple[int, ...]= (),
) -> pd.DataFrame: 
    anos= [ 
        ano for ano in range(ano_referencia - anos_historico, ano_referencia)
        if ano not in excluir_anos
    ]
    historico= serie[serie['ano'].isin(anos)]
    if historico['ano'].nunique() < MINIMO_ANOS_HISTORICO: 
        raise ValueError(
            f'histórico insuficiente: {historico["ano"].nunique()} anos disponíveis, necessário pelo menos {MINIMO_ANOS_HISTORICO}')
    # A semana 53 só existe em alguns anos; com 1 valor os quartis colapsam. Ela herda os limites da 52.
    historico= historico[historico['semana_epi'] <= 52]
    canal= (
        historico.groupby('semana_epi')['incidencia_100k']
        .quantile([0.25, 0.5, 0.75])
        .unstack()
        .rename(columns={0.25: 'q1', 0.5: 'mediana', 0.75: 'q3'})
    )
    return canal.reindex(range(1, 54)).ffill()

def classificar(incidencia: float, q1: float, mediana: float, q3: float) -> str: 
    if incidencia <= q1: 
        return 'sucesso'
    if incidencia <= mediana: 
        return 'seguranca'
    if incidencia <= q3:
        return 'alerta'
    return 'epidemia'

def contar_semanas_acima_q3(atual: pd.DataFrame, canal: pd.DataFrame) -> int:
    contagem= 0 
    for _, linha in atual.iloc[::-1].iterrows():
        if linha['incidencia_100k'] <= canal.loc[int(linha['semana_epi']), 'q3']: 
            break 
        contagem += 1 
    return contagem 

def avaliar_semana(serie: pd.DataFrame, canal: pd.DataFrame, ano_referencia: int) -> Avaliacao:
  atual= serie[serie['ano'] == ano_referencia].sort_values('semana_epi')
  if atual.empty: 
        raise ValueError(f'ANO {ano_referencia} NÃO ENCONTRADO NA SÉRIE') 
  ultima= atual.iloc[-1]
  limites= canal.loc[int(ultima['semana_epi'])]
  return Avaliacao(
      semana= int(ultima['semana']), 
      incidencia= float(ultima['incidencia_100k']), 
      q1= float(limites['q1']), 
      mediana= float(limites['mediana']), 
      q3= float(limites['q3']), 
      zona= classificar(ultima['incidencia_100k'], limites['q1'], limites['mediana'], limites['q3']),
      semanas_acima_q3= contar_semanas_acima_q3(atual, canal),
        rt= float(ultima['rt']),
  )