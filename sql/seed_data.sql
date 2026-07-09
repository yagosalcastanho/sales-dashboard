-- vendedores
INSERT INTO salespeople (name, region, hire_date, monthly_goal) VALUES
('Ana Ribeiro',    'Sudeste', '2022-03-01', 50000),
('Bruno Castro',   'Sul',     '2021-07-15', 45000),
('Carla Mendes',   'Nordeste','2023-01-10', 40000),
('Diego Santos',   'Sudeste', '2020-11-20', 55000),
('Elaine Souza',   'Centro-Oeste', '2022-09-05', 38000),
('Fabio Lima',     'Norte',   '2023-04-18', 35000);

-- produtos para venda
INSERT INTO products (name, category, cost_price, sale_price) VALUES
('Notebook Pro 15',      'Eletrônicos', 2800.00, 4200.00),
('Mouse Sem Fio',        'Acessórios',     25.00,   59.90),
('Monitor 27" 4K',       'Eletrônicos', 1100.00, 1799.00),
('Teclado Mecânico',     'Acessórios',    180.00,  349.90),
('Cadeira Ergonômica',   'Móveis',        650.00, 1199.00),
('Headset Gamer',        'Acessórios',    120.00,  259.90),
('Webcam HD',            'Acessórios',     90.00,  189.90),
('SSD 1TB',              'Componentes',   220.00,  399.00);

-- clientes, segmentos e estados
INSERT INTO customers (name, segment, state) VALUES
('TechCorp Ltda',      'Corporativo', 'SP'),
('Maria Oliveira',     'Varejo',      'RJ'),
('Prefeitura Municipal','Governo',    'MG'),
('João Pereira',       'Varejo',      'RS'),
('InovaTech S.A.',     'Corporativo', 'SP'),
('Secretaria Estadual','Governo',     'BA'),
('Pedro Almeida',      'Varejo',      'PR'),
('Construtora Silva',  'Corporativo', 'SC');

-- pedidos: 18 meses de histórico, distribuidos aleatoriamente
-- generate_series cria as combinações sem precisar loop manual
INSERT INTO orders (salesperson_id, product_id, customer_id, quantity, order_date, status)
SELECT
    (random() * 5 + 1)::int,
    (random() * 7 + 1)::int,
    (random() * 7 + 1)::int,
    (random() * 5 + 1)::int,
    (DATE '2024-01-01' + (random() * 540)::int),
    CASE WHEN random() < 0.05 THEN 'cancelled'
         WHEN random() < 0.08 THEN 'returned'
         ELSE 'completed' END
FROM generate_series(1, 2000);