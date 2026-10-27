-- 1. Cuántos valores distintos tiene cada candidata a dimensión
SELECT count(*) AS polizas,
       count(DISTINCT Region) AS regiones,
       count(DISTINCT Area) AS zonas,
       count(DISTINCT VehBrand) AS marcas,
       count(DISTINCT VehGas) AS combustibles,
       count(DISTINCT VehPower) AS potencias,
       count(DISTINCT VehAge) AS antiguedades,
       count(DISTINCT DrivAge) AS edades,
       count(DISTINCT BonusMalus) AS bonus_malus
FROM workspace.raw.fremtpl2_freq;

-- 2. Cuántos vehículos distintos hay, si un vehículo es marca + combustible + potencia
SELECT count(*) AS vehiculos
FROM (SELECT DISTINCT VehBrand, VehGas, VehPower
      FROM workspace.raw.fremtpl2_freq) AS v;

-- 3. ¿La zona cuelga de la región? Cuántas zonas distintas hay dentro de cada región
SELECT Region, count(DISTINCT Area) AS zonas, count(*) AS polizas
FROM workspace.raw.fremtpl2_freq
GROUP BY Region
ORDER BY zonas, Region;

-- 4. Cómo vienen escritos los valores, tal cual
SELECT Region, Area, VehBrand, VehGas
FROM workspace.raw.fremtpl2_freq
LIMIT 3;