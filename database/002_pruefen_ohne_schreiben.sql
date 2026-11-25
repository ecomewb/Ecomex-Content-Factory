-- Prüfqueries: können nach erfolgreicher Tabellenanlage gelesen/ausgeführt werden.
-- Keine Veränderung von Daten.
SELECT 'ecomex_sources' AS objekt, count(*) AS anzahl FROM public.ecomex_sources
UNION ALL
SELECT 'ecomex_documents', count(*) FROM public.ecomex_documents;

SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname='public' AND tablename IN ('ecomex_sources','ecomex_documents')
ORDER BY tablename;

SELECT extname, extversion FROM pg_extension WHERE extname='vector';

-- Nach dem ersten Import: Stichprobe mit Herkunft und Locator anzeigen:
-- SELECT d.id, left(d.content,120) AS auszug,
--        d.metadata->>'source_id' AS quelle,
--        d.metadata->>'locator' AS fundstelle,
--        s.review_status
-- FROM public.ecomex_documents d
-- JOIN public.ecomex_sources s ON s.source_id=d.source_id
-- ORDER BY d.id DESC LIMIT 10;
