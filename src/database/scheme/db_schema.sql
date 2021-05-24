--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3 (Debian 13.3-1.pgdg100+1)
-- Dumped by pg_dump version 13.3 (Debian 13.3-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: redditpost; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.redditpost (
    ticker character varying NOT NULL,
    created_utc timestamp without time zone NOT NULL,
    comment character varying NOT NULL
);


ALTER TABLE public.redditpost OWNER TO admin;

--
-- Name: redditposts; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.redditposts (
    ticker character varying NOT NULL,
    created_utc timestamp without time zone NOT NULL,
    comment character varying NOT NULL,
    passed_filter_checks boolean,
    sentiment double precision
);


ALTER TABLE public.redditposts OWNER TO admin;

--
-- Name: redditpost redditpost_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.redditpost
    ADD CONSTRAINT redditpost_pkey PRIMARY KEY (ticker, created_utc);


--
-- Name: redditposts redditposts_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.redditposts
    ADD CONSTRAINT redditposts_pkey PRIMARY KEY (ticker, created_utc);


--
-- PostgreSQL database dump complete
--
