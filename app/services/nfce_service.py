import re
from typing import Any

from bs4 import BeautifulSoup, Tag


def extrair_dados_nfce(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    dados: dict[str, Any] = {}

    try:
        # Emitente e CNPJ
        txt_center = soup.find("div", class_="txtCenter")
        emitente = txt_center.find("div", class_="txtTopo").text.strip()
        cnpj_text = txt_center.find_all("div", class_="text")[0].text.strip()
        endereco = txt_center.find_all("div", class_="text")[1].text.strip()
        cnpj_match = re.search(r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", cnpj_text)
        cnpj = cnpj_match.group(1) if cnpj_match else None

        # Itens
        itens = extrair_itens(soup)

        # Valor total
        valor_total = extrair_valor_total(soup)

        # Tributos totais
        tributos = extrair_tributos_totais(soup)

        # Informações gerais
        info_geral_div = soup.find(
            "div", string=re.compile("Informações gerais da Nota")
        ) or soup.find("div", class_="ui-collapsible-content")

        li_info = info_geral_div.find("li", class_="ui-li-static")
        texto_info = li_info.get_text(" ", strip=True)

        numero = re.search(r"Número:\s*(\d+)", texto_info).group(1)
        serie = re.search(r"Série:\s*(\d+)", texto_info).group(1)
        data_emissao = re.search(
            r"Emissão:\s*(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", texto_info
        ).group(1)
        protocolo = re.search(r"Protocolo de Autorização:\s*(\d+)", texto_info).group(1)

        chave_span = soup.find("span", class_="chave")
        chave_acesso = chave_span.text.strip().replace(" ", "") if chave_span else ""

        # Consumidor (opcional)  # noqa: ERA001
        consumidor_div = soup.find(
            "div", {"data-role": "collapsible"}, string=re.compile("Consumidor")
        )
        consumidor = ""
        if consumidor_div:
            consumidor_li = consumidor_div.find_next("li")
            consumidor = consumidor_li.text.strip() if consumidor_li else ""

        dados = {
            "emitente": emitente,
            "cnpj": cnpj,
            "endereco": endereco,
            "valor_total": valor_total,
            "numero": numero,
            "serie": serie,
            "data_emissao": data_emissao,
            "protocolo": protocolo,
            "chave_acesso": chave_acesso,
            "consumidor": consumidor,
            "tributos": tributos,
            "itens": itens,
        }

    except (AttributeError, IndexError, ValueError, TypeError, re.error) as e:
        dados["erro"] = f"Erro ao extrair dados: {e!s}"
        msg = "Erro ao processar dados da NFC-e"
        raise ValueError(msg) from e

    return dados


def extrair_tributos_totais(soup: BeautifulSoup) -> float | None:
    tributo_span = soup.select_one("div#totalNota span.totalNumb.txtObs")
    if not tributo_span:
        return None
    return float(tributo_span.text.strip().replace(".", "").replace(",", "."))


def extrair_itens(soup: BeautifulSoup) -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    trs = soup.select("table#tabResult tbody tr")

    for tr in trs:
        item = processar_linha_item(tr)
        if item:
            itens.append(item)

    return itens


def processar_linha_item(tr: Tag) -> dict[str, Any] | None:
    tds = tr.find_all("td")
    if len(tds) < 2:
        return None

    try:
        td_desc = tds[0]
        descricao = extrair_texto(td_desc, "txtTit")

        quantidade = extrair_valor_regex(td_desc, "Rqtd", r"Qtde\.\:\s*([\d,\.]+)")
        unidade = extrair_texto_regex(td_desc, "RUN", r"UN:\s*(\S+)")
        valor_unitario = extrair_valor_regex(
            td_desc, "RvlUnit", r"Vl\. Unit\.\:\s*([\d,\.]+)"
        )

        valor_total = None
        valor_span = tds[1].find("span", class_="valor")
        if valor_span:
            valor_total = float(
                valor_span.text.strip().replace(".", "").replace(",", ".")
            )
    except (AttributeError, ValueError, TypeError):
        return None
    else:
        return {
            "descricao": descricao,
            "quantidade": quantidade,
            "unidade": unidade,
            "valor_unitario": valor_unitario,
            "valor_total": valor_total,
        }


def extrair_texto(base: Tag, classe: str) -> str:
    tag = base.find("span", class_=classe)
    return tag.text.strip() if tag else ""


def extrair_texto_regex(base: Tag, classe: str, pattern: str) -> str | None:
    tag = base.find("span", class_=classe)
    if tag:
        match = re.search(pattern, tag.text)
        if match:
            return match.group(1)
    return None


def extrair_valor_regex(base: Tag, classe: str, pattern: str) -> float | None:
    texto = extrair_texto_regex(base, classe, pattern)
    if texto:
        return float(texto.replace(",", "."))
    return None


def extrair_valor_total(soup: BeautifulSoup) -> float:
    span_valor = soup.select_one("#totalNota span.totalNumb.txtMax")
    if not span_valor:
        msg = "Valor total não encontrado"
        raise ValueError(msg)
    return float(span_valor.text.strip().replace(".", "").replace(",", "."))
