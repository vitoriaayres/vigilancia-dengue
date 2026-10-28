import pandas as pd
import pytest

from vigilancia.canal_endemico import avaliar_semana, calcular_canal, classificar


def serie_sintetica(incidencia_por_ano: dict[int, list[float] | float]) -> pd.DataFrame:
    linhas = []
    for ano, valores in incidencia_por_ano.items():
        lista = valores if isinstance(valores, list) else [valores] * 52
        for semana_epi, incidencia in enumerate(lista, start=1):
            linhas.append({
                "semana": ano * 100 + semana_epi,
                "ano": ano,
                "semana_epi": semana_epi,
                "incidencia_100k": incidencia,
                "rt": 1.2,
            })
    return pd.DataFrame(linhas)


HISTORICO = {2019: 10.0, 2020: 20.0, 2021: 30.0, 2022: 40.0, 2023: 50.0}


def test_quartis_do_canal():
    canal = calcular_canal(serie_sintetica(HISTORICO), ano_referencia=2024)
    assert canal.loc[10, "q1"] == pytest.approx(20)
    assert canal.loc[10, "mediana"] == pytest.approx(30)
    assert canal.loc[10, "q3"] == pytest.approx(40)


@pytest.mark.parametrize("incidencia, zona", [(15, "sucesso"), (25, "seguranca"), (35, "alerta"), (45, "epidemia")])
def test_classificacao_das_zonas(incidencia, zona):
    assert classificar(incidencia, q1=20, mediana=30, q3=40) == zona


def test_excluir_ano_epidemico_reduz_o_limite():
    com_epidemia = {**HISTORICO, 2023: 500.0}
    canal_contaminado = calcular_canal(serie_sintetica(com_epidemia), 2024)
    canal_limpo = calcular_canal(serie_sintetica(com_epidemia), 2024, excluir_anos=(2023,))
    assert canal_limpo.loc[10, "q3"] < canal_contaminado.loc[10, "q3"]


def test_historico_insuficiente():
    with pytest.raises(ValueError, match="histórico insuficiente"):
        calcular_canal(serie_sintetica({2022: 10.0, 2023: 20.0}), 2024)


def test_conta_semanas_seguidas_acima_do_q3():
    atual = [35.0] * 7 + [45.0, 50.0, 60.0]  # as 3 últimas semanas acima do Q3 (40)
    serie = serie_sintetica({**HISTORICO, 2024: atual})
    canal = calcular_canal(serie, 2024)
    avaliacao = avaliar_semana(serie, canal, 2024)
    assert avaliacao.semana == 202410
    assert avaliacao.zona == "epidemia"
    assert avaliacao.semanas_acima_q3 == 3


def test_semana_53_herda_limites_da_52():
    serie = serie_sintetica({**HISTORICO, 2020: [20.0] * 52 + [999.0]})
    canal = calcular_canal(serie, 2024)
    assert canal.loc[53].equals(canal.loc[52])
