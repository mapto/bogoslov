--
-- PostgreSQL database cluster dump
--

--
-- Name: bogoslov; Type: DATABASE; Schema: -; Owner: bogoslov
--

\connect bogoslov

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: verses; Type: TABLE; Schema: public; Owner: bogoslov
--

CREATE TABLE public.verses (
    id SERIAL PRIMARY KEY,
    path character varying,
    filename character varying,
    address character varying,
    text character varying,
    lemmas character varying,
    UNIQUE (path, filename, address)
);


ALTER TABLE public.verses OWNER TO bogoslov;

--
-- Name: ngrams; Type: TABLE; Schema: public; Owner: bogoslov
--

CREATE TABLE public.ngrams (
    id SERIAL PRIMARY KEY,
    lemmas character varying,
    text character varying,
    n integer,
    pos integer,
    verse_id integer REFERENCES public.verses (id),
    UNIQUE (verse_id, pos, n)
);


ALTER TABLE public.ngrams OWNER TO bogoslov;

--
-- Name: embeddings; Type: TABLE; Schema: public; Owner: bogoslov
--

CREATE TABLE public.embeddings (
    id SERIAL PRIMARY KEY,
    model character varying,
    vector public.vector(768),
    verse_id integer REFERENCES public.verses (id),
    UNIQUE (verse_id, model)
);


ALTER TABLE public.embeddings OWNER TO bogoslov;