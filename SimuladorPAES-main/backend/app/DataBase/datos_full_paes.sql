-- datos_full_paes.sql (ejecutar todo de una vez)
CREATE DATABASE IF NOT EXISTS paes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE paes;

-- tablas básicas
CREATE TABLE IF NOT EXISTS universidades (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(200) NOT NULL,
  acreditacion INT NULL,
  sitio_web VARCHAR(255) NULL,
  direccion VARCHAR(255) NULL,
  latitud DECIMAL(10,7) NULL,
  longitud DECIMAL(10,7) NULL,
  UNIQUE KEY ux_universidad_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS carreras (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(200) NOT NULL,
  duracion VARCHAR(50) NULL,
  vacantes INT NULL,
  arancel INT NULL,
  universidad_id INT NOT NULL,
  CONSTRAINT fk_carrera_univ FOREIGN KEY (universidad_id) REFERENCES universidades(id),
  UNIQUE KEY ux_carrera_univ (universidad_id, nombre)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS puntajes_corte (
  id INT AUTO_INCREMENT PRIMARY KEY,
  carrera_id INT NOT NULL,
  puntaje_minimo DECIMAL(6,2) NOT NULL,
  ano INT NOT NULL,
  CONSTRAINT fk_pc_carrera FOREIGN KEY (carrera_id) REFERENCES carreras(id),
  UNIQUE KEY ux_pc_carrera_ano (carrera_id, ano)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS simulaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  carrera_id INT NULL,
  puntaje_lenguaje DECIMAL(6,2) NULL,
  puntaje_matematicas DECIMAL(6,2) NULL,
  puntaje_matematicas2 DECIMAL(6,2) NULL,
  puntaje_ciencias DECIMAL(6,2) NULL,
  puntaje_historia DECIMAL(6,2) NULL,
  puntaje_historia_electiva DECIMAL(6,2) NULL,
  puntaje_nem DECIMAL(6,2) NULL,
  puntaje_ranking DECIMAL(6,2) NULL,
  puntaje_total DECIMAL(7,2) NOT NULL,
  CONSTRAINT fk_sim_carrera FOREIGN KEY (carrera_id) REFERENCES carreras(id)
) ENGINE=InnoDB;

-- tabla de ponderaciones
CREATE TABLE IF NOT EXISTS ponderaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  carrera_id INT NOT NULL UNIQUE,
  w_lenguaje     DECIMAL(5,2) NOT NULL DEFAULT 0,
  w_matematicas  DECIMAL(5,2) NOT NULL DEFAULT 0,
  w_matematicas2 DECIMAL(5,2) NOT NULL DEFAULT 0,
  w_ciencias     DECIMAL(5,2) NOT NULL DEFAULT 0,
  w_historia     DECIMAL(5,2) NOT NULL DEFAULT 0,
  w_nem          DECIMAL(5,2) NOT NULL DEFAULT 0,
  w_ranking      DECIMAL(5,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_pond_carrera FOREIGN KEY (carrera_id) REFERENCES carreras(id)
) ENGINE=InnoDB;

-- --------------------
-- 1) Universidades (básicas)
-- --------------------
INSERT INTO universidades (nombre, acreditacion, sitio_web, direccion)
VALUES
('Universidad de Chile', 7, 'https://www.uchile.cl', 'Santiago'),
('Pontificia Universidad Católica de Chile', 7, 'https://www.uc.cl', 'Santiago'),
('Universidad de Santiago de Chile', 6, 'https://www.usach.cl', 'Santiago'),
('Universidad de Concepción', 6, 'https://www.udec.cl', 'Concepción'),
('Universidad Técnica Federico Santa María', 6, 'https://www.usm.cl', 'Valparaíso'),
('Universidad de Valparaíso', 5, 'https://www.uv.cl', 'Valparaíso'),
('Universidad Austral de Chile', 6, 'https://www.uach.cl', 'Valdivia'),
('Universidad de La Frontera', 5, 'https://www.ufro.cl', 'Temuco')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- --------------------
-- 2) Carreras (varias; sólo se insertan si faltan)
-- --------------------
INSERT INTO carreras (universidad_id, nombre, duracion, vacantes, arancel)
SELECT u.id, t.carrera, t.duracion, t.vacantes, t.arancel
FROM (
  SELECT 'Universidad de Chile' uni, 'Ingeniería Civil Industrial' AS carrera, '10 semestres' AS duracion, 120 AS vacantes, 2500000 AS arancel UNION ALL
  SELECT 'Universidad de Chile','Química y Farmacia','10 semestres', 80, 2200000 UNION ALL
  SELECT 'Universidad de Chile','Periodismo','8 semestres', 90, 1400000 UNION ALL

  SELECT 'Pontificia Universidad Católica de Chile','Ingeniería Civil Industrial','10 semestres',120,2600000 UNION ALL
  SELECT 'Pontificia Universidad Católica de Chile','Química y Farmacia','10 semestres',70,2300000 UNION ALL
  SELECT 'Pontificia Universidad Católica de Chile','Diseño','8 semestres',60,1300000 UNION ALL

  SELECT 'Universidad de Santiago de Chile','Ingeniería Civil Industrial','10 semestres',100,2100000 UNION ALL
  SELECT 'Universidad de Santiago de Chile','Contador Auditor','10 semestres',80,1200000 UNION ALL
  SELECT 'Universidad de Santiago de Chile','Periodismo','8 semestres',70,1100000 UNION ALL

  SELECT 'Universidad de Concepción','Ingeniería Civil Industrial','10 semestres',90,2000000 UNION ALL
  SELECT 'Universidad de Concepción','Química y Farmacia','10 semestres',60,1900000 UNION ALL
  SELECT 'Universidad de Concepción','Periodismo','8 semestres',50,1000000 UNION ALL

  SELECT 'Universidad Técnica Federico Santa María','Ingeniería Civil Informática','10 semestres',110,2400000 UNION ALL
  SELECT 'Universidad Técnica Federico Santa María','Construcción Civil','10 semestres',80,2000000 UNION ALL
  SELECT 'Universidad Técnica Federico Santa María','Ingeniería Civil Industrial','10 semestres',90,2300000 UNION ALL

  SELECT 'Universidad de Valparaíso','Fonoaudiología','10 semestres',40,900000 UNION ALL
  SELECT 'Universidad de Valparaíso','Nutrición y Dietética','9 semestres',50,850000 UNION ALL
  SELECT 'Universidad de Valparaíso','Periodismo','8 semestres',45,800000 UNION ALL

  SELECT 'Universidad Austral de Chile','Fonoaudiología','10 semestres',35,900000 UNION ALL
  SELECT 'Universidad Austral de Chile','Nutrición y Dietética','9 semestres',40,850000 UNION ALL
  SELECT 'Universidad Austral de Chile','Ingeniería Civil Industrial','10 semestres',50,1800000 UNION ALL

  SELECT 'Universidad de La Frontera','Terapia Ocupacional','10 semestres',30,700000 UNION ALL
  SELECT 'Universidad de La Frontera','Nutrición y Dietética','9 semestres',40,700000 UNION ALL
  SELECT 'Universidad de La Frontera','Ingeniería Civil Industrial','10 semestres',40,1500000
) AS t
JOIN universidades u ON u.nombre = t.uni
LEFT JOIN carreras c ON c.universidad_id = u.id AND c.nombre = t.carrera
WHERE c.id IS NULL;

-- --------------------
-- 3) Puntajes (2023-2025) - sólo inserta si falta
-- --------------------
INSERT INTO puntajes_corte (carrera_id, puntaje_minimo, ano)
SELECT c.id, p.puntaje, p.ano
FROM (
  /* UChile */
  SELECT 'Universidad de Chile' uni, 'Ingeniería Civil Industrial' carrera, 2025 ano, 750.00 puntaje UNION ALL
  SELECT 'Universidad de Chile','Ingeniería Civil Industrial',2024,742.00 UNION ALL
  SELECT 'Universidad de Chile','Química y Farmacia',2025,735.00 UNION ALL
  SELECT 'Universidad de Chile','Periodismo',2025,680.00 UNION ALL

  /* PUC */
  SELECT 'Pontificia Universidad Católica de Chile','Ingeniería Civil Industrial',2025,755.00 UNION ALL
  SELECT 'Pontificia Universidad Católica de Chile','Química y Farmacia',2025,740.00 UNION ALL
  SELECT 'Pontificia Universidad Católica de Chile','Diseño',2025,695.00 UNION ALL

  /* USACH */
  SELECT 'Universidad de Santiago de Chile','Ingeniería Civil Industrial',2025,720.00 UNION ALL
  SELECT 'Universidad de Santiago de Chile','Contador Auditor',2025,660.00 UNION ALL
  SELECT 'Universidad de Santiago de Chile','Periodismo',2025,665.00 UNION ALL

  /* UdeC */
  SELECT 'Universidad de Concepción','Ingeniería Civil Industrial',2025,710.00 UNION ALL
  SELECT 'Universidad de Concepción','Química y Farmacia',2025,710.00 UNION ALL
  SELECT 'Universidad de Concepción','Periodismo',2025,655.00 UNION ALL

  /* UTFSM */
  SELECT 'Universidad Técnica Federico Santa María','Ingeniería Civil Informática',2025,735.00 UNION ALL
  SELECT 'Universidad Técnica Federico Santa María','Construcción Civil',2025,670.00 UNION ALL
  SELECT 'Universidad Técnica Federico Santa María','Ingeniería Civil Industrial',2025,725.00 UNION ALL

  /* UV */
  SELECT 'Universidad de Valparaíso','Fonoaudiología',2025,650.00 UNION ALL
  SELECT 'Universidad de Valparaíso','Nutrición y Dietética',2025,655.00 UNION ALL
  SELECT 'Universidad de Valparaíso','Periodismo',2025,640.00 UNION ALL

  /* UACh */
  SELECT 'Universidad Austral de Chile','Fonoaudiología',2025,665.00 UNION ALL
  SELECT 'Universidad Austral de Chile','Nutrición y Dietética',2025,668.00 UNION ALL
  SELECT 'Universidad Austral de Chile','Ingeniería Civil Industrial',2025,705.00 UNION ALL

  /* UFRO */
  SELECT 'Universidad de La Frontera','Terapia Ocupacional',2025,650.00 UNION ALL
  SELECT 'Universidad de La Frontera','Nutrición y Dietética',2025,648.00 UNION ALL
  SELECT 'Universidad de La Frontera','Ingeniería Civil Industrial',2025,690.00
) AS p
JOIN universidades u ON u.nombre = p.uni
JOIN carreras c ON c.universidad_id = u.id AND c.nombre = p.carrera
LEFT JOIN puntajes_corte pc ON pc.carrera_id = c.id AND pc.ano = p.ano
WHERE pc.id IS NULL;

-- --------------------
-- 4) Ponderaciones (plantillas por tipo de carrera). No duplica.
-- --------------------
/* STEM / Ingenierías / Informática */
INSERT INTO ponderaciones (carrera_id, w_lenguaje, w_matematicas, w_matematicas2, w_ciencias, w_historia, w_nem, w_ranking)
SELECT c.id, 0.15, 0.20, 0.15, 0.20, 0.00, 0.15, 0.15
FROM carreras c
WHERE c.nombre LIKE '%Ingenier%' OR c.nombre LIKE '%Inform%'
ON DUPLICATE KEY UPDATE
  w_lenguaje=VALUES(w_lenguaje), w_matematicas=VALUES(w_matematicas),
  w_matematicas2=VALUES(w_matematicas2), w_ciencias=VALUES(w_ciencias),
  w_historia=VALUES(w_historia), w_nem=VALUES(w_nem), w_ranking=VALUES(w_ranking);

/* Derecho / Humanidades */
INSERT INTO ponderaciones (carrera_id, w_lenguaje, w_matematicas, w_matematicas2, w_ciencias, w_historia, w_nem, w_ranking)
SELECT c.id, 0.30, 0.10, 0.00, 0.00, 0.20, 0.20, 0.20
FROM carreras c
WHERE c.nombre LIKE '%Derecho%' OR c.nombre LIKE '%Humanid%' OR c.nombre LIKE '%Periodismo%'
ON DUPLICATE KEY UPDATE
  w_lenguaje=VALUES(w_lenguaje), w_matematicas=VALUES(w_matematicas),
  w_matematicas2=VALUES(w_matematicas2), w_ciencias=VALUES(w_ciencias),
  w_historia=VALUES(w_historia), w_nem=VALUES(w_nem), w_ranking=VALUES(w_ranking);

/* Salud */
INSERT INTO ponderaciones (carrera_id, w_lenguaje, w_matematicas, w_matematicas2, w_ciencias, w_historia, w_nem, w_ranking)
SELECT c.id, 0.20, 0.20, 0.10, 0.20, 0.00, 0.15, 0.15
FROM carreras c
WHERE c.nombre LIKE '%Medicin%' OR c.nombre LIKE '%Enfermer%' OR c.nombre LIKE '%Nutrici%' OR c.nombre LIKE '%Fonoaud%'
ON DUPLICATE KEY UPDATE
  w_lenguaje=VALUES(w_lenguaje), w_matematicas=VALUES(w_matematicas),
  w_matematicas2=VALUES(w_matematicas2), w_ciencias=VALUES(w_ciencias),
  w_historia=VALUES(w_historia), w_nem=VALUES(w_nem), w_ranking=VALUES(w_ranking);

/* Negocios / Admin */
INSERT INTO ponderaciones (carrera_id, w_lenguaje, w_matematicas, w_matematicas2, w_ciencias, w_historia, w_nem, w_ranking)
SELECT c.id, 0.25, 0.20, 0.00, 0.00, 0.10, 0.20, 0.25
FROM carreras c
WHERE c.nombre LIKE '%Contador%' OR c.nombre LIKE '%Administr%' OR c.nombre LIKE '%Econom%'
ON DUPLICATE KEY UPDATE
  w_lenguaje=VALUES(w_lenguaje), w_matematicas=VALUES(w_matematicas),
  w_matematicas2=VALUES(w_matematicas2), w_ciencias=VALUES(w_ciencias),
  w_historia=VALUES(w_historia), w_nem=VALUES(w_nem), w_ranking=VALUES(w_ranking);

-- --------------------
-- 5) Chequeo rápido (resultados visibles al ejecutar)
-- --------------------
SELECT COUNT(*) AS universidades FROM universidades;
SELECT COUNT(*) AS carreras FROM carreras;
SELECT COUNT(*) AS puntajes FROM puntajes_corte;
SELECT COUNT(*) AS ponderaciones FROM ponderaciones;

SELECT u.nombre AS universidad, c.nombre AS carrera, pc.ano, pc.puntaje_minimo
FROM puntajes_corte pc
JOIN carreras c ON c.id = pc.carrera_id
JOIN universidades u ON u.id = c.universidad_id
WHERE pc.ano IN (2023,2024,2025)
ORDER BY pc.ano DESC, u.nombre, c.nombre
LIMIT 200;
