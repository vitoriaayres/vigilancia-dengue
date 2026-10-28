from dataclasses import asdict 
from typing import Literal 
import pandas as pd 

from .canal_endemico import avaliar_semana, calcular_canal 
from .estado import EstadoVigilancia
from .infodengue import buscar_serie 

ANOS_HISTORICO= 5 

def buscar_dados(estado: EstadoVigilancia) -> dict: 
    ano= estado['ano_referencia']
    serie= buscar_serie(estado['geocodigo'], estado['doenca'], ano - ANOS_HISTORICO, ano)
    serie['inicio_semana']= serie['inicio_semana'].dt.strftime('%Y-%m-%d')
    return {
        'serie': serie.to_dict('records'), 
        'observacoes': [f'{len(serie)} SEMANAS OBTIDAS DO INFO DENGUE'],
    }

def avaliar_situacao(estado: EstadoVigilancia) -> dict: 
    serie= pd.DataFrame(estado['serie'])
    canal= calcular_canal(
        serie, estado['ano_referencia'], ANOS_HISTORICO, tuple(estado.get('excluir_anos', []))
    )
    avaliacao= avaliar_semana(serie, canal, estado['ano_referencia'])
    anomalia= avaliacao.zona == 'epidemia' or (avaliacao.zona == 'alerta' and avaliacao.rt > 1)
    return {
        'avaliacao': asdict(avaliacao),
        'anomalia': anomalia,
    }

def rota_apos_avaliacao(estado: EstadoVigilancia) -> Literal['investigar', 'encerrar']: 
    return 'investigar' if estado['anomalia'] else 'encerrar'

def investigar(estado: EstadoVigilancia) -> dict: 
    avaliacao= estado['avaliacao']
    return { 
        'observacoes': [
            f'ANOMALIA NA SEMANA {avaliacao['semana']}: zona {avaliacao['zona']}, '
            f'{avaliacao['semanas_acima_q3']} SEMANAS ACIMA DO Q3, RT={avaliacao['rt']:.2f}'
        ]
    }

def encerrar(estado: EstadoVigilancia) -> dict:
    avaliacao= estado['avaliacao']
    return {'observacoes': [f'SEMANA {avaliacao['semana']}: zona {avaliacao['zona']}, SEM ANOMALIA']}