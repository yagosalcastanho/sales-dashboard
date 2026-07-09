"""
Configuracao centraliza do pipe
Credenciais vem de variaveis do ambioente - nunca hardcoded do codigo
para que o repositorio possa ser publico sem expor acesso ao banco
"""

import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5436)),
    "dbname":   os.getenv("DB_NAME", "sales_dashboard_db"),
    "user":     os.getenv("DB_USER", "dash_user"),
    "password": os.getenv("DB_PASSWORD", "dash_pass"),
}

OUTPUT_PATH = os.getenv("OUTPUT_PATH", "../data/sales_clean.csv")
