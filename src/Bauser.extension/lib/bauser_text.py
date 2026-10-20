# -*- coding: utf-8 -*-
"""UI strings, Portuguese (default) and English.

Non-ASCII text uses u"" literals so IronPython 2.7 and CPython 3 agree.
The chosen language lives in pyRevit's config (section "Bauser"); the Language
button flips it.
"""
SECTION = "Bauser"
DEFAULT = "pt"

# key: (English, Portuguese)
STRINGS = {
    "no_walls": (u"No walls found in the model.", u"Nenhuma parede encontrada no modelo."),
    "scope_sel": (u"Selection (%d walls)", u"Seleção (%d paredes)"),
    "scope_model": (u"Entire model", u"Modelo inteiro"),
    "cancelled": (u"Cancelled.", u"Cancelado."),
    "cancelled_nothing": (u"Cancelled. Nothing changed.", u"Cancelado. Nada foi alterado."),
    # window
    "btn_export": (u"Export CSV", u"Exportar CSV"),
    "btn_budget": (u"Export budget CSV", u"Exportar orçamento CSV"),
    "btn_close": (u"Close", u"Fechar"),
    "saved": (u"Saved:", u"Salvo:"),
    "save_failed": (u"Could not save CSV:", u"Não foi possível salvar o CSV:"),
    # columns
    "col_type": (u"Type", u"Tipo"),
    "col_qty": (u"Qty", u"Qtd"),
    "col_area": (u"Area m²", u"Área m²"),
    "col_mark": (u"Mark", u"Marca"),
    "col_level": (u"Level", u"Nível"),
    "col_length": (u"Length m", u"Comprimento m"),
    "col_rate": (u"Rate R$/m²", u"Preço R$/m²"),
    "col_ref": (u"SINAPI ref", u"Ref. SINAPI"),
    "col_cost": (u"Cost R$", u"Custo R$"),
    "col_openings": (u"Openings", u"Aberturas"),
    # pricing basis
    "basis_prompt": (u"Price panels on:", u"Precificar painéis por:"),
    "basis_net": (u"Net area (openings excluded)", u"Área líquida (sem aberturas)"),
    "basis_gross": (u"Full panel size (length x height)", u"Tamanho total do painel (comprimento x altura)"),
    "bud_basis": (u"Pricing basis: %s", u"Base de preço: %s"),
    "irregular_note": (
        u"%d panel(s) have an edited profile or a slanted/tapered section. For them, full panel size "
        u"(length x height) is an upper bound; use net area or check them by hand.",
        u"%d painel(is) têm perfil editado ou seção inclinada/cônica. Para eles, o tamanho total do "
        u"painel (comprimento x altura) é um limite superior; use a área líquida ou confira manualmente."),
    # count
    "count_title": (u"Panel count", u"Contagem de painéis"),
    "panels": (u"Panels", u"Painéis"),
    "types": (u"Panel types", u"Tipos de painel"),
    "total_area": (u"Total area", u"Área total"),
    # number
    "number_title": (u"Panels numbered", u"Painéis numerados"),
    "number_confirm": (
        u"Number %d panels (%s to %s)?\n\nThis overwrites the Mark parameter. Undo with Ctrl+Z.",
        u"Numerar %d painéis (%s a %s)?\n\nIsso sobrescreve o parâmetro Marca. Desfazer: Ctrl+Z."),
    "number_dialog": (u"Bauser - Number panels", u"Bauser - Numerar painéis"),
    "marks_written": (u"Marks written", u"Marcas gravadas"),
    "skipped": (u"Skipped (read-only)", u"Ignorados (somente leitura)"),
    "range": (u"Range", u"Faixa"),
    "number_note": (u"Order: level, then X, then Y", u"Ordem: nível, depois X, depois Y"),
    # cost
    "cost_title": (u"Panel cost estimate", u"Estimativa de custo dos painéis"),
    "waste_prompt": (u"Waste factor (%):", u"Fator de perdas (%):"),
    "waste_title": (u"Bauser - Panel cost", u"Bauser - Custo dos painéis"),
    "not_a_number": (u"'%s' is not a number.", u"'%s' não é um número."),
    "card_total": (u"Total with %s%% waste", u"Total com %s%% de perdas"),
    "card_eur": (u"Approx. in EUR (EUR/BRL %s, BCB PTAX %s)",
                 u"Aprox. em EUR (EUR/BRL %s, PTAX BCB %s)"),
    "card_per_m2": (u"All-in per m²", u"Total por m²"),
    "cost_note": (u"Cost = area x rate x (1 + waste). Demo rates.",
                  u"Custo = área x preço x (1 + perdas). Preços de demonstração."),
    # budget csv
    "bud_code": (u"Code", u"Código"),
    "bud_desc": (u"Description", u"Descrição"),
    "bud_unit": (u"Unit", u"Un."),
    "bud_qty": (u"Qty", u"Qtd."),
    "bud_price": (u"Unit price (R$)", u"Preço unit. (R$)"),
    "bud_total": (u"Total (R$)", u"Total (R$)"),
    "bud_waste": (u"Waste (%s%%)", u"Perdas (%s%%)"),
    "bud_total_brl": (u"TOTAL (R$)", u"TOTAL (R$)"),
    "bud_total_eur": (u"TOTAL (EUR, approx.)", u"TOTAL (EUR, aprox.)"),
    "bud_fx": (u"EUR/BRL %s - BCB PTAX closing %s", u"EUR/BRL %s - PTAX BCB fechamento %s"),
    # language button
    "lang_set": (u"Language: English", u"Idioma: Português"),
}


def lang():
    try:
        from pyrevit import script
        v = script.get_config(SECTION).get_option("lang", DEFAULT)
    except Exception:
        v = DEFAULT
    return v if v in ("en", "pt") else DEFAULT


def set_lang(value):
    from pyrevit import script
    script.get_config(SECTION).set_option("lang", value)
    script.save_config()


def t(key, *args):
    en, pt = STRINGS[key]
    s = pt if lang() == "pt" else en
    return s % args if args else s
