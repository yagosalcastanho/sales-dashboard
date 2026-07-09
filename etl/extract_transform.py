"""
Pipeline de extracao, limpeza e enriquecimento para o dash
cada funcao implementa um RF ou regra de negócio específica,
referenciada em comentário para rastreabilidade com o documento de requisitos.
"""

import pandas as pd
import psycopg2
import logging
from pathlib import Path
from config import DB_CONFIG, OUTPUT_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

## RF01 — extracao via SQL com joins resolvidos no banco, nao no pandas
EXTRACT_QUERY = """
    SELECT
        o.id            AS order_id,
        o.order_date,
        o.quantity,
        o.status,
        sp.name         AS salesperson_name,
        sp.region,
        sp.monthly_goal,
        p.name          AS product_name,
        p.category,
        p.cost_price,
        p.sale_price,
        c.name          AS customer_name,
        c.segment       AS customer_segment,
        c.state         AS customer_state
    FROM orders o
    JOIN salespeople sp ON sp.id = o.salesperson_id
    JOIN products p     ON p.id  = o.product_id
    JOIN customers c    ON c.id  = o.customer_id
"""


def extract_from_postgres() -> pd.DataFrame:
    ## RF01 — conecta no PostgreSQL e extrai o dataset bruto via SQL.
    logger.info("Conectando ao PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(EXTRACT_QUERY, conn)
    finally:
        conn.close()  ## garante fechamento mesmo se read_sql falhar
    logger.info(f"[EXTRACT] {len(df):,} registros brutos extraídos.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    ## RF02 / RN01 — remove pedidos cancelados e devolvidos.
    ## eles existem no banco para auditoria operacional, mas não são venda real.
    
    df = df.copy()
    before = len(df)

    df = df[df["status"] == "completed"].drop(columns=["status"])

    df["cost_price"] = df["cost_price"].astype(float)
    df["sale_price"] = df["sale_price"].astype(float)
    df["quantity"]   = df["quantity"].astype(int)
    df["order_date"] = pd.to_datetime(df["order_date"])

    df = df.drop_duplicates(subset=["order_id"])

    removed = before - len(df)
    logger.info(f"[CLEAN] {removed} registros removidos (cancelados/devolvidos/duplicados).")
    logger.info(f"[CLEAN] {len(df):,} registros válidos restantes.")
    return df


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    
    ## RF03 / RF04 / RN02 / RN03 / RN04 — calcula métricas de negócio linha a linha.
    ## Pré-calculado aqui para que o valor seja idêntico em qualquer contexto
    ## de filtro do Power BI — ver decisão de arquitetura sobre margem.

    df = df.copy()

    ## RF03 / RN02 — margem sobre o preço efetivamente cobrado (sale_price)
    df["revenue"]    = (df["sale_price"] * df["quantity"]).round(2)
    df["cost"]       = (df["cost_price"] * df["quantity"]).round(2)
    df["margin"]     = (df["revenue"] - df["cost"]).round(2)
    df["margin_pct"] = (df["margin"] / df["revenue"] * 100).round(2)

    df["ticket_avg"] = (df["revenue"] / df["quantity"]).round(2)

    df["order_year"]       = df["order_date"].dt.year
    df["order_month"]      = df["order_date"].dt.month
    df["order_month_name"] = df["order_date"].dt.strftime("%b/%Y")
    df["order_quarter"]    = df["order_date"].dt.quarter

    ## RF04 / RN03 — meta sempre relativa ao mês da venda, não ao mês atual
    monthly_revenue = (
        df.groupby(["salesperson_name", "order_year", "order_month"])["revenue"]
        .transform("sum")
    )

    ## RN04 — vendedor sem meta cadastrada não pode quebrar o pipeline
    ## replace(0, pd.NA) evita ZeroDivisionError/inf sem precisar de try/except
    safe_goal = df["monthly_goal"].replace(0, float("nan"))
    df["goal_attainment_pct"] = (monthly_revenue / safe_goal * 100).round(1)

    logger.info("[ENRICH] Colunas de negócio calculadas: revenue, margin, goal_attainment_pct.")
    return df


def export_for_powerbi(df: pd.DataFrame, output_path: str):
    ## RNF04 — UTF-8 com BOM para compatibilidade de acentuação no Power BI Windows.
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info(f"[EXPORT] {output_path} ({len(df):,} linhas, {len(df.columns)} colunas).")


def run_pipeline() -> pd.DataFrame:
    ## Orquestra as etapas — função única testável de ponta a ponta.
    df_raw      = extract_from_postgres()
    df_clean    = clean_data(df_raw)
    df_enriched = enrich_data(df_clean)
    return df_enriched


def main():
    df_final = run_pipeline()
    export_for_powerbi(df_final, OUTPUT_PATH)

    print("\n" + "=" * 50)
    print("  RESUMO DA EXTRAÇÃO")
    print("=" * 50)
    print(f"  Pedidos processados : {len(df_final):,}")
    print(f"  Receita total       : R$ {df_final['revenue'].sum():,.2f}")
    print(f"  Margem média        : {df_final['margin_pct'].mean():.1f}%")
    print(f"  Período             : {df_final['order_date'].min().date()} a {df_final['order_date'].max().date()}")
    print("=" * 50)


if __name__ == "__main__":
    main()