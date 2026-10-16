-- P1. ¿Cuántas pólizas tienen 0, 1, 2 y más siniestros?
SELECT
ClaimNb,
count(*) AS n_polizas,
round(count(*) * 100 / sum(count(*)) OVER (), 2)      AS pct_polizas
FROM workspace.raw.fremtpl2_freq
GROUP BY ClaimNb
ORDER BY ClaimNb;

-- P2. Mínimo y máximo de exposure, cantidad de pólizas con más de 1 en exposure
SELECT
min(exposure) AS min_exposure,
max(exposure) AS max_exposure,
sum(CASE WHEN exposure > 1 THEN 1 ELSE 0 END) AS n_polizas_mas_1
FROM workspace.raw.fremtpl2_freq;

-- P3. ¿Todas las pólizas de freMTPL2sev existen en freMTPL2freq? ¿Y al revés, cuántas pólizas con
-- ClaimNb > 0 no tienen ningún siniestro en sev?

-- P3a: ¿Todos los siniestros de sev tienen su póliza en freq?
SELECT
    count(*) AS siniestros_sin_poliza
FROM workspace.raw.fremtpl2_sev AS s
LEFT JOIN workspace.raw.fremtpl2_freq AS f
    ON s.IDpol = f.IDpol
WHERE f.IDpol IS NULL;

-- P3b: ¿Cuántas pólizas con ClaimNb > 0 no tienen ningún siniestro en sev?
SELECT
    count(*) AS polizas_con_siniestro_sin_detalle
FROM workspace.raw.fremtpl2_freq AS f
LEFT JOIN workspace.raw.fremtpl2_sev AS s
    ON f.IDpol = s.IDpol
WHERE f.ClaimNb > 0
  AND s.IDpol IS NULL;

-- P3c: Verificación entre tablas: siniestros según freq vs montos en sev
SELECT
    (SELECT sum(ClaimNb) FROM workspace.raw.fremtpl2_freq) AS siniestros_segun_freq,
    (SELECT count(*)     FROM workspace.raw.fremtpl2_sev)  AS siniestros_con_monto_sev;


-- P3d: Hipótesis de grano: ¿una fila de sev = un siniestro?
-- Compara ClaimNb de freq con la cantidad de filas en sev, por póliza
SELECT
    sum(CASE WHEN f.ClaimNb = s.n_filas THEN 1 ELSE 0 END)  AS coincide,
    sum(CASE WHEN f.ClaimNb > s.n_filas THEN 1 ELSE 0 END)  AS freq_cuenta_mas,
    sum(CASE WHEN f.ClaimNb < s.n_filas THEN 1 ELSE 0 END)  AS sev_tiene_mas
FROM workspace.raw.fremtpl2_freq AS f
INNER JOIN (
    SELECT IDpol, count(*) AS n_filas
    FROM workspace.raw.fremtpl2_sev
    GROUP BY IDpol
) AS s
    ON f.IDpol = s.IDpol;

-- P4. Frecuencia (siniestros / exposición) por Area y por tramo de DrivAge que vos definas. ¿Qué
--tramo es el más caro?

-- P4a: Frecuencia de siniestros por Area (A = rural … F = urbano)
SELECT
    Area,
    sum(ClaimNb)                               AS siniestros,
    round(sum(Exposure), 0)                    AS anios_poliza,
    round(sum(ClaimNb) / sum(Exposure), 4)     AS frecuencia
FROM workspace.raw.fremtpl2_freq
GROUP BY Area
ORDER BY Area;

-- P4b: Frecuencia de siniestros por tramo de edad del conductor
SELECT
    CASE
        WHEN DrivAge <= 25 THEN '1. 18-25'
        WHEN DrivAge <= 35 THEN '2. 26-35'
        WHEN DrivAge <= 50 THEN '3. 36-50'
        WHEN DrivAge <= 65 THEN '4. 51-65'
        ELSE                    '5. 66+'
    END                                        AS tramo_edad,
    count(*)                                   AS polizas,
    sum(ClaimNb)                               AS siniestros,
    round(sum(ClaimNb) / sum(Exposure), 4)     AS frecuencia
FROM workspace.raw.fremtpl2_freq
GROUP BY 1
ORDER BY 1;

-- P4c: Verificación: totales de freq (deben coincidir con la suma de P4a y P4b)
SELECT
    sum(ClaimNb)                AS total_siniestros,
    round(sum(Exposure), 0)     AS total_anios_poliza
FROM workspace.raw.fremtpl2_freq;


-- P5: Severidad: costo medio, mediano y máximo por siniestro
-- ¿Qué dice la diferencia entre media y mediana?
SELECT
    count(*)                       AS siniestros,
    round(avg(ClaimAmount), 2)     AS costo_medio,
    round(median(ClaimAmount), 2)  AS costo_mediano,
    round(max(ClaimAmount), 2)     AS costo_maximo
FROM workspace.raw.fremtpl2_sev;



-- HALLAZGOS PRINCIPALES DEL PERFILADO

-- 1. Cartera: el 94,98 % de las pólizas no tiene siniestros (643.953 de 678.013).
--    Hay valores extremos: 3 pólizas con 11 siniestros y 1 con 16

-- 2. Exposición: va de mínimo 0,00273 que es 1 día a 2,01 años, y 1.224 pólizas superan 1 año,
--    aunque el dataset dice que se observaron "principalmente durante un año" ( posible error de datos)

-- 3. Relación freq y sev NO está limpia:
--    - 195 filas de sev (siniestros, según el grano de la tabla) no tienen su póliza en freq.
--    - 9.116 pólizas con ClaimNb > 0 no tienen ningún siniestro en sev, pareciera que no estan aun registrados.
--    - Un test de relación en dbt puede fallar (Detectarlo)

-- 4. El grano de sev es correcto(1 fila = 1 siniestro): en 24.943 pólizas ClaimNb coincide
--    con sus filas en sev. Lo incompleto es la cobertura: freq cuenta 36,102 siniestros y sev
--    tiene 26,639 montos, hay 9,463 siniestros sin costo. 

-- 5. Frecuencia por zona: sube en escalera de rural a urbano (A = 0,0817 y F = 0,1391).
--    F tiene la menor exposición (8,129 años-póliza), su frecuencia es la menos confiable.

-- 6. Frecuencia por edad: los conductores de 18-25 (0,1751) tienen aproximadamente 1,8 veces la frecuencia
--    del resto, que es casi plana (≈ 0,095–0,099). 

-- 7. Severidad: la media (2.278,54) es aprox 1,94 veces la mediana (1.172) y el máximo llega a
--    4,075,400 costo muy concentrado en pocos siniestros graves (distribución sesgada).

