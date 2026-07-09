"""
Testes unitários das regras de negócio.
Cada teste mapeia diretamente para um TC do documento de requisitos.
Rodar com: pytest tests/test_business_rules.py -v
"""

import pandas as pd
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "etl"))
from extract_transform import clean_data, enrich_data


@pytest.fixture
def raw_sample() -> pd.DataFrame:
    ## Dataset mínimo cobrindo os casos de borda do documento de requisitos.
    return pd.DataFrame({
        "order_id":         [1, 2, 3, 4, 5],
        "order_date":       pd.to_datetime(["2024-03-01"] * 5),
        "quantity":         [2, 1, 1, 1, 1],
        "status":           ["completed", "cancelled", "completed", "completed", "completed"],
        "salesperson_name": ["Ana", "Ana", "Ana", "Bruno", "Bruno"],
        "region":           ["Sudeste"] * 5,
        "monthly_goal":     [50000, 50000, 50000, 0, 0],   ## Bruno sem meta — TC04
        "product_name":     ["Notebook"] * 5,
        "category":         ["Eletrônicos"] * 5,
        "cost_price":       [60.0] * 5,
        "sale_price":       [100.0] * 5,
        "customer_name":    ["Cliente X"] * 5,
        "customer_segment": ["Varejo"] * 5,
        "customer_state":   ["SP"] * 5,
    })


def test_tc01_remove_cancelled_orders(raw_sample):
    ## TC01 — pedido cancelado é excluído do dataframe final.
    df_clean = clean_data(raw_sample)
    assert 2 not in df_clean["order_id"].values
    assert len(df_clean) == 4  ## 5 originais - 1 cancelado


def test_tc02_revenue_calculation(raw_sample):
    ## TC02 — revenue = sale_price × quantity.
    df_clean   = clean_data(raw_sample)
    df_enriched = enrich_data(df_clean)
    order_1 = df_enriched[df_enriched["order_id"] == 1].iloc[0]
    assert order_1["revenue"] == 200.0  ## 100 * 2


def test_tc03_margin_calculation(raw_sample):
    ## TC03 — margin e margin_pct calculados sobre sale_price, não preço de tabela.
    df_clean    = clean_data(raw_sample)
    df_enriched = enrich_data(df_clean)
    order_3 = df_enriched[df_enriched["order_id"] == 3].iloc[0]
    assert order_3["margin"] == 40.0       ## 100 - 60
    assert order_3["margin_pct"] == 40.0   ## 40 / 100 * 100


def test_tc04_goal_zero_does_not_raise(raw_sample):
    ## TC04 — vendedor com monthly_goal=0 não gera exceção, retorna nulo.
    df_clean    = clean_data(raw_sample)
    df_enriched = enrich_data(df_clean)
    bruno_rows = df_enriched[df_enriched["salesperson_name"] == "Bruno"]
    assert bruno_rows["goal_attainment_pct"].isna().all()


def test_tc05_goal_attainment_consistent_within_month(raw_sample):
    ## TC05 — dois pedidos do mesmo vendedor no mesmo mês têm o mesmo attainment.
    df_clean    = clean_data(raw_sample)
    df_enriched = enrich_data(df_clean)
    ana_rows = df_enriched[df_enriched["salesperson_name"] == "Ana"]
    assert ana_rows["goal_attainment_pct"].nunique() == 1


def test_tc06_output_types_are_correct(raw_sample):
    ## TC06 — colunas numéricas e de data não ficam como object após o pipeline.
    df_clean    = clean_data(raw_sample)
    df_enriched = enrich_data(df_clean)
    assert pd.api.types.is_float_dtype(df_enriched["revenue"])
    assert pd.api.types.is_datetime64_any_dtype(df_enriched["order_date"])


def test_tc07_pipeline_is_idempotent(raw_sample):
    ## TC07 — rodar o pipeline duas vezes sobre os mesmos dados gera o mesmo resultado.
    run_1 = enrich_data(clean_data(raw_sample))
    run_2 = enrich_data(clean_data(raw_sample))
    pd.testing.assert_frame_equal(
        run_1.reset_index(drop=True),
        run_2.reset_index(drop=True)
    )