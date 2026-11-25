-- ECOMEX Content Factory — Anpassungen für den Betrieb mit n8n
-- VERSION: 0.2.0 · Voraussetzung: 001_create_kb.sql wurde ausgeführt.
-- Wiederholbar: Alle Befehle sind so geschrieben, dass ein zweiter Lauf nichts kaputt macht.
--
-- Was diese Datei ändert:
-- 1. Embedding-Modell wird erzwungen: Ein Chunk mit Embedding braucht
--    metadata.embedding_model = 'text-embedding-3-small'. Vorher ging ein fehlender Wert
--    still durch (NULL erfüllt einen CHECK). So mischt später niemand versehentlich Modelle.
-- 2. ecomex_storage_inventory(): listet die Dateien der Storage-Ablage mit Status
--    (schon registriert? wie viele Chunks? gibt es eine PDF-Fassung?) für den Ablage-Import.
-- 3. ecomex_kb_status(): Kurzbericht über Quellen und Chunks je Status.
-- Beide Funktionen sind nur für den serverseitigen Schlüssel (service_role) aufrufbar.

BEGIN;

-- 1. Embedding-Modell verbindlich machen -----------------------------------------------
ALTER TABLE public.ecomex_documents DROP CONSTRAINT IF EXISTS ecomex_docs_embedding_model;
ALTER TABLE public.ecomex_documents ADD CONSTRAINT ecomex_docs_embedding_model CHECK (
  embedding IS NULL OR coalesce(embedding_model, '') = 'text-embedding-3-small'
);

-- 2. Inventar der Storage-Ablage --------------------------------------------------------
CREATE OR REPLACE FUNCTION public.ecomex_storage_inventory (
  p_bucket text DEFAULT 'ecomex-sources',
  p_prefix text DEFAULT ''
)
RETURNS TABLE (
  object_path text,
  folder text,
  file_name text,
  extension text,
  bytes bigint,
  mimetype text,
  updated_at timestamptz,
  storage_uri text,
  source_id_vorschlag text,
  source_type text,
  registered boolean,
  registered_source_id text,
  chunks bigint,
  has_pdf_twin boolean,
  empfohlen boolean,
  grund text
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, storage, pg_temp
AS $$
  WITH obj AS (
    SELECT o.name AS object_path,
           coalesce(nullif(regexp_replace(o.name, '/[^/]*$', ''), o.name), '') AS folder,
           regexp_replace(o.name, '^.*/', '') AS file_name,
           lower(substring(o.name from '\.([^./]+)$')) AS extension,
           (o.metadata ->> 'size')::bigint AS bytes,
           o.metadata ->> 'mimetype' AS mimetype,
           o.updated_at,
           'supabase://' || o.bucket_id || '/' || o.name AS storage_uri,
           'SB-' || left(md5(o.bucket_id || '/' || o.name), 12) AS source_id_vorschlag
    FROM storage.objects o
    WHERE o.bucket_id = p_bucket
      AND o.name LIKE (coalesce(p_prefix, '') || '%')
      AND o.name NOT LIKE '%/.emptyFolderPlaceholder'
  ),
  norm AS (
    SELECT obj.*,
           regexp_replace(lower(regexp_replace(file_name, '\.[^.]+$', '')), '[^a-z0-9]', '', 'g') AS stamm
    FROM obj
  ),
  reg AS (
    SELECT s.storage_uri, s.source_id,
           (SELECT count(*) FROM public.ecomex_documents d WHERE d.source_id = s.source_id) AS chunks
    FROM public.ecomex_sources s
  ),
  bewertet AS (
    SELECT n.object_path, n.folder, n.file_name, n.extension, n.bytes, n.mimetype, n.updated_at,
           n.storage_uri, n.source_id_vorschlag,
           CASE n.extension
             WHEN 'pptx' THEN 'pptx' WHEN 'pdf' THEN 'pdf' WHEN 'docx' THEN 'docx'
             WHEN 'md' THEN 'md' WHEN 'txt' THEN 'md'
             ELSE 'other' END AS source_type,
           (r.source_id IS NOT NULL) AS registered,
           r.source_id AS registered_source_id,
           coalesce(r.chunks, 0) AS chunks,
           (n.extension IN ('pptx','docx') AND EXISTS (
              SELECT 1 FROM norm p
              WHERE p.folder = n.folder AND p.extension = 'pdf' AND p.stamm = n.stamm
           )) AS has_pdf_twin
    FROM norm n
    LEFT JOIN reg r ON r.storage_uri = n.storage_uri
  )
  SELECT b.*,
         (b.extension IN ('pdf','docx','pptx','xlsx','csv','md','txt')
          AND NOT b.has_pdf_twin
          AND b.file_name NOT ILIKE '%masterlayout%'
          AND b.folder NOT ILIKE '%mastervorlage%'
          AND b.folder NOT ILIKE 'storyboard%'
          AND (NOT b.registered OR b.chunks = 0)) AS empfohlen,
         CASE
           WHEN b.extension NOT IN ('pdf','docx','pptx','xlsx','csv','md','txt') THEN 'Dateityp wird nicht eingelesen'
           WHEN b.file_name ILIKE '%masterlayout%' OR b.folder ILIKE '%mastervorlage%' THEN 'Folienmaster – Vorlage, keine Wissensquelle'
           WHEN b.folder ILIKE 'storyboard%' THEN 'Storyboard – Produktionsauftrag, keine Wissensquelle'
           WHEN b.has_pdf_twin THEN 'PDF-Fassung im selben Ordner wird stattdessen gelesen'
           WHEN b.registered AND b.chunks > 0 THEN 'bereits eingelesen'
           WHEN b.registered THEN 'registriert, aber noch ohne Text – wird erneut eingelesen'
           ELSE 'neu'
         END AS grund
  FROM bewertet b
  ORDER BY b.object_path;
$$;

-- 3. Statusbericht der Wissensbasis ------------------------------------------------------
CREATE OR REPLACE FUNCTION public.ecomex_kb_status ()
RETURNS TABLE (
  review_status text,
  quellen bigint,
  quellen_ohne_text bigint,
  chunks bigint
)
LANGUAGE sql
STABLE
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
  SELECT s.review_status,
         count(*) AS quellen,
         count(*) FILTER (WHERE NOT EXISTS (SELECT 1 FROM public.ecomex_documents d WHERE d.source_id = s.source_id)) AS quellen_ohne_text,
         coalesce(sum((SELECT count(*) FROM public.ecomex_documents d WHERE d.source_id = s.source_id)), 0)::bigint AS chunks
  FROM public.ecomex_sources s
  GROUP BY s.review_status
  ORDER BY s.review_status;
$$;

REVOKE ALL ON FUNCTION public.ecomex_storage_inventory(text, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.ecomex_storage_inventory(text, text) TO service_role;
REVOKE ALL ON FUNCTION public.ecomex_kb_status() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.ecomex_kb_status() TO service_role;

COMMIT;

-- Prüfen (verändert nichts):
-- SELECT * FROM public.ecomex_kb_status();
-- SELECT object_path, bytes, empfohlen, grund FROM public.ecomex_storage_inventory() ORDER BY 1;
