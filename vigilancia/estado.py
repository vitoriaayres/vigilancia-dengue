import operator 
from typing import Annotated, TypedDict 

class EstadoVigilancia(TypedDict, total= False): 
    geocodigo: int 
    doenca: str
    ano_referencia: int 
    excluir_anos: tuple[int, ...]

    serie: list[dict]
    avaliacao: dict 
    anomalia: bool

    observacoes: Annotated[list[str], operator.add]
                       
