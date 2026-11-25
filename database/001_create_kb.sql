-- ECOMEX Content Factory — initiale, nicht-destruktive SQL-Anlage
-- VERSION: 0.1.0, ENTWURF: nur in NEUEM, leerem Supabase-Projekt ausführen.
-- Bestehende Tabellen mit denselben Namen? STOPP und Konflikt klären.
-- In Supabase SQL Editor EINMAL ausführen; danach nicht blind wiederholt verändern.
-- n8n Data Loader muss metadata.source_id UND metadata.embedding_model setzen.
-- Embedding-Pilot: text-embedding-3-small mit 1536 Dimensionen.
-- Vereinbarung: Normen stehen in Git; diese Datenbank enthält nur Quellen/Chunks.
BEGIN;
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

CREATE TABLE public.ecomex_sources (
  source_id text PRIMARY KEY,
  title text NOT NULL,
  source_type text NOT NULL CHECK (source_type IN ('pptx','pdf','docx','md','web','other')),
  storage_provider text NOT NULL CHECK (storage_provider IN ('sharepoint','supabase_storage','git','external_url','other')),
  storage_uri text NOT NULL,
  module_id text,
  review_status text NOT NULL DEFAULT 'reference'
    CHECK (review_status IN ('draft','reference','approved','archived')),
  access_class text NOT NULL DEFAULT 'internal'
    CHECK (access_class IN ('public','internal','restricted')),
  version_label text,
  sha256 text,
  license_note text,
  last_verified_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  notes text
);

CREATE TABLE public.ecomex_documents (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  content text NOT NULL CHECK (length(trim(content)) > 0),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_id text GENERATED ALWAYS AS (metadata ->> 'source_id') STORED,
  embedding extensions.vector(1536),
  embedding_model text GENERATED ALWAYS AS (metadata ->> 'embedding_model') STORED,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ecomex_docs_source_required CHECK (
    coalesce(length(trim(metadata ->> 'source_id')),0) > 0
  ),
  CONSTRAINT ecomex_docs_source_fk FOREIGN KEY (source_id)
    REFERENCES public.ecomex_sources(source_id),
  CONSTRAINT ecomex_docs_embedding_model CHECK (
    embedding IS NULL OR embedding_model = 'text-embedding-3-small'
  )
);

CREATE INDEX ecomex_docs_source_idx ON public.ecomex_documents (source_id);
CREATE INDEX ecomex_docs_metadata_idx ON public.ecomex_documents USING gin (metadata);
CREATE INDEX ecomex_docs_fts_de_idx ON public.ecomex_documents
  USING gin (to_tsvector('german'::regconfig, content));
-- HNSW erst nach dem ersten erfolgreichen Pilotimport und Suchtest aktivieren.
-- CREATE INDEX ecomex_docs_embed_hnsw_idx ON public.ecomex_documents
--   USING hnsw (embedding vector_cosine_ops);

-- Diese Funktion ist an die n8n-/LangChain-Schnittstelle angelehnt.
-- Standard: Nur APPROVED, nicht RESTRICTED. Referenzquellen nur mit
-- explizitem filter={"allow_reference":true}. Dieses Flag muss vom
-- orchestrierenden Workflow gesetzt werden, nicht autonom vom LLM.
CREATE OR REPLACE FUNCTION public.ecomex_match_documents (
  query_embedding extensions.vector(1536),
  match_count integer DEFAULT 5,
  filter jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
  id bigint,
  content text,
  metadata jsonb,
  similarity double precision
)
LANGUAGE sql
STABLE
SECURITY INVOKER
SET search_path = public, extensions
AS $$
  SELECT d.id, d.content, d.metadata,
         (1 - (d.embedding <=> query_embedding))::double precision AS similarity
  FROM public.ecomex_documents d
  JOIN public.ecomex_sources s ON s.source_id = d.source_id
  WHERE d.embedding IS NOT NULL
    AND s.access_class IN ('public','internal')
    AND (
      s.review_status = 'approved'
      OR (s.review_status = 'reference'
          AND (filter ->> 'allow_reference') = 'true')
    )
    AND d.metadata @> (filter - 'allow_reference')
  ORDER BY d.embedding <=> query_embedding
  LIMIT LEAST(GREATEST(match_count, 1), 20);
$$;

-- Der API-Zugriff von anonymen oder eingeloggten Frontend-Nutzern wird
-- bewusst nicht freigegeben. n8n nutzt serverseitig einen geheimen Schlüssel.
ALTER TABLE public.ecomex_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ecomex_documents ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.ecomex_sources FROM anon, authenticated;
REVOKE ALL ON public.ecomex_documents FROM anon, authenticated;
REVOKE ALL ON FUNCTION public.ecomex_match_documents(extensions.vector,integer,jsonb) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.ecomex_match_documents(extensions.vector,integer,jsonb) TO service_role;
COMMIT;

-- WICHTIG: Noch kein Datenimport, keine Modell-API, kein öffentlicher Zugriff.
-- n8n-Vector-Store-Kompatibilität: Tabellenname ecomex_documents und
-- Funktionsname ecomex_match_documents in Node-Einstellungen konfigurieren.
-- Falls verwendete n8n-Version dies nicht unterstützt: eigenes Postgres/RPC-Node
-- oder gesonderter, getesteter Adapter statt öffentliche Tabellen umzubenennen.
