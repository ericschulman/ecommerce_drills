SELECT * FROM census a
JOIN (SELECT place, COUNT(*)
FROM census
GROUP BY place
HAVING count(*) > 1) b
ON a.place = b.place
ORDER BY a.place