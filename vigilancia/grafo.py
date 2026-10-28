from langgraph.checkpoint.base import BaseCheckpointSaver 
from langgraph.checkpoint.memory import InMemorySaver 
from langgraph.graph import END, START, StateGraph 

from .estado import EstadoVigilancia 
from .nos import avaliar_situacao, buscar_dados, encerrar, investigar, rota_apos_avaliacao 

def construir_grafo(checkpointer: BaseCheckpointSaver | None= None): 
    grafo= StateGraph(EstadoVigilancia)
    grafo.add_node('buscar_dados', buscar_dados) 
    grafo.add_node('avaliar_situacao', avaliar_situacao)
    grafo.add_node('investigar', investigar)
    grafo.add_node('encerrar', encerrar)

    grafo.add_edge(START, 'buscar_dados')
    grafo.add_edge('buscar_dados', 'avaliar_situacao')
    grafo.add_conditional_edges('avaliar_situacao', rota_apos_avaliacao, ['investigar', 'encerrar'])
    grafo.add_edge('investigar', END)
    grafo.add_edge('encerrar', END)

    return grafo.compile(checkpointer=checkpointer or InMemorySaver())