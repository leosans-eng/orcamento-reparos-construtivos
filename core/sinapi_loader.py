import os
import re
from pathlib import Path

import pandas as pd

from app_paths import app_dir
from core.sinapi_base import SinapiBase

APP_DIR = app_dir()
PASTA_SINAPI_PROCESSADO = os.path.join(APP_DIR, "sinapi", "sinapi_processado")
CAMINHO_FALLBACK_SINAPI = os.path.join(APP_DIR, "sinapi_precos.csv")

PADRAO_CATALOGO = re.compile(
    r"(?i)SINAPI_Refer[eê]ncia_(\d{4})_(\d{2})_catalogo\.csv$"
)
PADRAO_PRECOS = re.compile(
    r"(?i)SINAPI_Refer[eê]ncia_(\d{4})_(\d{2})_precos\.csv$"
)
PADRAO_LEGADO = re.compile(
    r"(?i)SINAPI_Refer[eê]ncia_(\d{4})_(\d{2})\.csv$"
)

PADRAO_XLSX_REFERENCIA = re.compile(
    r"(?i)SINAPI_Refer[eê]ncia_(\d{4})_(\d{2})\.xlsx$"
)


def _rotulo_referencia(ano: int, mes: int) -> str:
    return f"{mes:02d}/{ano}"


def _listar_pares_processados(pasta_processado: str) -> dict[tuple[int, int], tuple[str, str]]:
    if not os.path.isdir(pasta_processado):
        return {}
    catalogos: dict[tuple[int, int], str] = {}
    precos: dict[tuple[int, int], str] = {}
    for nome in os.listdir(pasta_processado):
        if not nome.lower().endswith(".csv"):
            continue
        caminho = os.path.join(pasta_processado, nome)
        match_cat = PADRAO_CATALOGO.match(nome)
        if match_cat:
            catalogos[(int(match_cat.group(1)), int(match_cat.group(2)))] = caminho
            continue
        match_pre = PADRAO_PRECOS.match(nome)
        if match_pre:
            precos[(int(match_pre.group(1)), int(match_pre.group(2)))] = caminho
    return {
        chave: (catalogos[chave], precos[chave])
        for chave in catalogos.keys() & precos.keys()
    }


def _listar_legado_processado(pasta_processado: str) -> tuple[str, str] | tuple[None, None]:
    if not os.path.isdir(pasta_processado):
        return None, None
    candidatos = []
    for nome in os.listdir(pasta_processado):
        match = PADRAO_LEGADO.match(nome)
        if match and "_catalogo" not in nome.lower() and "_precos" not in nome.lower():
            candidatos.append(
                ((int(match.group(1)), int(match.group(2))), os.path.join(pasta_processado, nome))
            )
    if not candidatos:
        return None, None
    candidatos.sort(key=lambda item: item[0], reverse=True)
    ano, mes = candidatos[0][0]
    return candidatos[0][1], _rotulo_referencia(ano, mes)


def obter_csv_sinapi_mais_recente(pasta_processado):
    """Compatibilidade: retorna caminho legado ou catálogo do par mais recente."""
    pares = _listar_pares_processados(pasta_processado)
    if pares:
        chave = max(pares.keys())
        caminho_catalogo, _caminho_precos = pares[chave]
        return caminho_catalogo, _rotulo_referencia(chave[0], chave[1])
    return _listar_legado_processado(pasta_processado)


def _carregar_par(caminho_catalogo: str, caminho_precos: str, rotulo: str):
    catalogo = pd.read_csv(
        caminho_catalogo,
        dtype={"codigo": str},
        usecols=lambda c: c.strip().lower() in {"codigo", "descricao", "unidade", "tipo"},
    )
    precos = pd.read_csv(
        caminho_precos,
        dtype={"codigo": str},
        usecols=lambda c: c.strip().lower() in {"codigo", "estado", "custo"},
    )
    base = SinapiBase(catalogo, precos)
    return base, caminho_catalogo, rotulo


def _carregar_legado(caminho: str, rotulo: str):
    df = pd.read_csv(caminho, dtype={"codigo": str})
    base = SinapiBase.from_dataframe_legado(df)
    return base, caminho, rotulo


def carregar_sinapi_por_referencia(pasta_processado=PASTA_SINAPI_PROCESSADO):
    pares = _listar_pares_processados(pasta_processado)
    if pares:
        chave = max(pares.keys())
        caminho_catalogo, caminho_precos = pares[chave]
        rotulo = _rotulo_referencia(chave[0], chave[1])
        return _carregar_par(caminho_catalogo, caminho_precos, rotulo)

    caminho_legado, rotulo = _listar_legado_processado(pasta_processado)
    if caminho_legado and rotulo:
        return _carregar_legado(caminho_legado, rotulo)

    if os.path.isfile(CAMINHO_FALLBACK_SINAPI):
        return _carregar_legado(
            CAMINHO_FALLBACK_SINAPI,
            "arquivo local (sinapi_precos.csv na raiz do projeto)",
        )

    return SinapiBase.vazio(), None, "BASE AUSENTE"


def carregar_sinapi_inicial():
    return carregar_sinapi_por_referencia()


def recarregar_sinapi():
    return carregar_sinapi_por_referencia()


def obter_xlsx_sinapi_referencia_mais_recente():
    pasta = Path(app_dir()) / "sinapi" / "sinapi_referencia"
    if not pasta.is_dir():
        return None
    candidatos = []
    for arquivo in pasta.glob("*.xlsx"):
        if arquivo.name.startswith("~$"):
            continue
        match = PADRAO_XLSX_REFERENCIA.match(arquivo.name)
        if match:
            candidatos.append(
                ((int(match.group(1)), int(match.group(2))), arquivo)
            )
    if not candidatos:
        return None
    candidatos.sort(key=lambda item: item[0], reverse=True)
    return candidatos[0][1]


def obter_estados_da_sinapi(sinapi):
    if isinstance(sinapi, SinapiBase):
        return sinapi.estados()
    if getattr(sinapi, "empty", True):
        return []
    if "estado" not in sinapi.columns:
        return []
    return sorted(sinapi["estado"].dropna().unique().tolist())
