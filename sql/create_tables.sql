-- simulação estrutura padrão de banco transacional de vendas
-- nornmaliza alguns dados para que o join faça uma extração mais real

-- 1. salespeople (sem dependências)
CREATE TABLE salespeople (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    region       VARCHAR(50) NOT NULL,
    hire_date    DATE NOT NULL,
    monthly_goal DECIMAL(10,2) NOT NULL
);

-- 2. products 
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    category    VARCHAR(80) NOT NULL,
    cost_price  DECIMAL(10,2) NOT NULL,
    sale_price  DECIMAL(10,2) NOT NULL
);

-- 3. customers 
CREATE TABLE customers (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(150) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    state   VARCHAR(2) NOT NULL
);

-- 4. orders (depende das três acima — sempre por último)
CREATE TABLE orders (
    id             SERIAL PRIMARY KEY,
    salesperson_id INTEGER REFERENCES salespeople(id),
    product_id     INTEGER REFERENCES products(id),
    customer_id    INTEGER REFERENCES customers(id),
    quantity       INTEGER NOT NULL,
    order_date     DATE NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'completed'
);

CREATE INDEX idx_orders_date        ON orders (order_date);
CREATE INDEX idx_orders_salesperson ON orders (salesperson_id);
CREATE INDEX idx_orders_product     ON orders (product_id);