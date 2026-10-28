import argparse 
from datetime import date 
from vigilancia.grafo import construir_grafo 
from vigilancia.infodengue import DOENCAS, ErroInfoDengue

def ler_argumentos() -> argparse.Namespace: 
    parser= argparse.ArgumentParser(description='VIGILANCIA DE ARBOVIROSES POR MUNICIPIO')
    parser.add_argument('geocodigo', type= int, help= 'codigo IBGE DE 7 DIGITOS (EX: 2927408 = SALVADOR)')
    parser.add_argument('--doenca', default='dengue', choices= DOENCAS)
    parser.add_argument('--ano', type= int, default= date.today().year)
    parser.add_argument('--excluir-anos', type= int, nargs= '*', default=[], help= 'ANOS EPIDEMICOS FORA DO HISTORICO')
    parser.add_argument('--diagrama', action='store_true', help='imprime o grafo em mermaid e sai')
    return parser.parse_args()

def main() -> None:
    args = ler_argumentos()
    grafo = construir_grafo()

    if args.diagrama:
        print(grafo.get_graph().draw_mermaid())
        return

    config = {"configurable": {"thread_id": f"{args.geocodigo}-{args.doenca}-{args.ano}"}}
    entrada = {
        "geocodigo": args.geocodigo,
        "doenca": args.doenca,
        "ano_referencia": args.ano,
        "excluir_anos": tuple(args.excluir_anos),
    }

    try:
        resultado = grafo.invoke(entrada, config)
    except (ErroInfoDengue, ValueError) as erro:
        raise SystemExit(f"Erro: {erro}")

    avaliacao = resultado["avaliacao"]
    print(f"Semana {avaliacao['semana']}: {avaliacao['incidencia']:.1f} casos/100 mil")
    print(f"Canal endêmico: Q1={avaliacao['q1']:.1f}  mediana={avaliacao['mediana']:.1f}  Q3={avaliacao['q3']:.1f}")
    print(f"Zona: {avaliacao['zona'].upper()}  |  anomalia: {'sim' if resultado['anomalia'] else 'não'}")
    for observacao in resultado["observacoes"]:
        print(f"  - {observacao}")


if __name__ == "__main__":
    main()