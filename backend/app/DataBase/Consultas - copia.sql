-- Agregar columna 'region' a la tabla 'universidades'
ALTER TABLE universidades ADD COLUMN region VARCHAR(100);

-- Modificar la columna 'nombre' de la tabla 'carreras' para aumentar su longitud
ALTER TABLE carreras MODIFY nombre VARCHAR(200);




-- Select simple
SELECT * FROM universidades;

-- Select con JOIN entre universidades y carreras
SELECT u.nombre AS universidad, c.nombre AS carrera
FROM universidades u
JOIN carreras c ON c.universidad_id = u.id;

-- Select con JOIN entre universidades, carreras y puntajes_corte
SELECT u.nombre, c.nombre, pc.ano, pc.puntaje_minimo
FROM universidades u
JOIN carreras c ON c.universidad_id = u.id
JOIN puntajes_corte pc ON pc.carrera_id = c.id
WHERE pc.ano = 2025;


-- Actualizar el puntaje mínimo para una carrera específica en 2025
UPDATE puntajes_corte SET puntaje_minimo = 650
WHERE carrera_id = 1 AND ano = 2025;

-- Cambiar el nombre de una universidad
UPDATE universidades SET nombre = 'Universidad de Santiago'
WHERE id = 2;


-- Insertar una nueva universidad
INSERT INTO universidades (nombre) VALUES ('Universidad Técnica Estatal');

-- Insertar una nueva carrera
INSERT INTO carreras (nombre, universidad_id) VALUES ('Ingeniería Civil', 1);

-- Insertar un puntaje de corte para una carrera
INSERT INTO puntajes_corte (carrera_id, ano, puntaje_minimo) VALUES (1, 2025, 700);





-- Eliminar el puntaje de corte de la carrera 1 en 2024
DELETE FROM puntajes_corte WHERE carrera_id = 1 AND ano = 2024;

-- Eliminar la carrera con id 10
DELETE FROM simulaciones WHERE carrera_id = 10;

-- Eliminar la tabla temporal si existe
DELETE FROM puntajes_corte WHERE carrera_id = 10;
