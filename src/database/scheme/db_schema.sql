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
-- Name: redditposts; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.redditposts (
    ticker character varying NOT NULL,
    created_utc timestamp without time zone NOT NULL,
    comment character varying NOT NULL
);


ALTER TABLE public.redditposts OWNER TO admin;

--
-- Data for Name: redditposts; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.redditposts (ticker, created_utc, comment) FROM stdin;
\.


--
-- Name: redditposts redditposts_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.redditposts
    ADD CONSTRAINT redditposts_pkey PRIMARY KEY (ticker, created_utc);


--
-- PostgreSQL database dump complete
--
