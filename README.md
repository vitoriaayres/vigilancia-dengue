# Vigilância de dengue com LangGraph

Monitora arboviroses (dengue, chikungunya e zika) por município com dados do [InfoDengue](https://info.dengue.mat.br) (Fiocruz e FGV) e responde à pergunta da vigilância epidemiológica: **a incidência desta semana é normal para esta época do ano?**

Esta é a parte 1 de 4. Por enquanto o grafo não usa LLM, porque decidir se há epidemia é um cálculo estatístico. O modelo de linguagem entra nas próximas partes, para investigar causas e redigir o boletim.

## Como funciona

```
START -> buscar_dados -> avaliar_situacao --(anomalia)--> investigar -> END
                                          --(normal)----> encerrar   -> END
```

- **Canal endêmico** (diagrama de controle): para cada semana epidemiológica, calcula os quartis da incidência nos 5 anos anteriores e define as zonas.

  | Zona | Faixa |
  |---|---|
  | sucesso | até o Q1 |
  | segurança | até a mediana |
  | alerta | até o Q3 |
  | epidemia | acima do Q3 |

- **Regra de anomalia:** a semana está em zona de epidemia, **ou** está em alerta com Rt > 1 (transmissão acelerando).
- **Anos epidêmicos podem ser excluídos do histórico** (`--excluir-anos`). Sem isso, um ano recorde como 2024 eleva o limite e mascara epidemias futuras.
- A semana 53, que só existe em alguns anos, herda os limites da semana 52. Sem isso, o canal dela seria calculado com um único valor.

| Arquivo | Responsabilidade |
|---|---|
| `vigilancia/infodengue.py` | Cliente da API, com validação das colunas |
| `vigilancia/canal_endemico.py` | Quartis, zonas e semanas seguidas acima do Q3 |
| `vigilancia/estado.py` | Estado do grafo, só com tipos serializáveis |
| `vigilancia/nos.py` | Nós e roteamento |
| `vigilancia/grafo.py` | Montagem do `StateGraph` com checkpointer |

## Resultados

**Testes:** 9 testes passando (`pytest -q`), sem acesso à rede.

**Execução real:** Salvador (2927408), dengue, última semana de 2025 (SE 202553), com 314 semanas obtidas.

| Histórico | Incidência | Q1 | Mediana | Q3 | Zona |
|---|---|---|---|---|---|
| 2020–2024, excluindo 2024 | 1,3 | 0,5 | 1,3 | 2,0 | segurança |
| 2020–2024, completo | 1,3 | 0,7 | 1,9 | 2,0 | segurança |

O valor da incidência é em casos por 100 mil habitantes.

Incluir 2024 elevou o Q1 e a mediana, mesmo numa semana de baixa transmissão. Antes da correção da semana 53, essa mesma execução classificava Salvador como **epidemia com Rt de 0,45**. Foi um falso alarme, que só apareceu com dados reais.

## Como executar

Requer Python 3.12 ou superior.

```bash
pip install -r requirements.txt
pytest -q
python main.py 2927408 --diagrama
python main.py 2927408 --ano 2025 --excluir-anos 2024
```

