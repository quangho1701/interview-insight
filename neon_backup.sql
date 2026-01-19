--
-- PostgreSQL database dump
--

\restrict el2CjlITbkSatz9b4klR1cgJlPk0x17BsC8AWRV4dOx2SwutWdAGPsvSUfq5MFd

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: interview_analyses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interview_analyses (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    interviewer_id uuid NOT NULL,
    sentiment_score double precision NOT NULL,
    metrics_json jsonb,
    transcript_redacted text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    summary text
);


ALTER TABLE public.interview_analyses OWNER TO postgres;

--
-- Name: interviewers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interviewers (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    company character varying(255),
    profile_status character varying(20) DEFAULT 'hidden'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id uuid,
    email character varying
);


ALTER TABLE public.interviewers OWNER TO postgres;

--
-- Name: processing_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.processing_jobs (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    analysis_id uuid,
    s3_audio_key character varying(512) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    error_message text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    interviewer_id uuid
);


ALTER TABLE public.processing_jobs OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    provider character varying(20) NOT NULL,
    email character varying(255) NOT NULL,
    credits integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    hashed_password character varying(255),
    oauth_id character varying(255)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
d84fa060098e
\.


--
-- Data for Name: interview_analyses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interview_analyses (id, user_id, interviewer_id, sentiment_score, metrics_json, transcript_redacted, created_at, updated_at, summary) FROM stdin;
\.


--
-- Data for Name: interviewers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interviewers (id, name, company, profile_status, created_at, updated_at, user_id, email) FROM stdin;
3428f34a-5fdc-45b4-8975-096c815dcf0c	Anh	\N	HIDDEN	2026-01-18 23:31:40.097132	2026-01-18 23:31:40.097305	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N
8aa90543-a91c-4b50-886b-02e93884ff01	Anh Tri	\N	HIDDEN	2026-01-19 06:42:12.646572	2026-01-19 06:42:12.646724	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N
\.


--
-- Data for Name: processing_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.processing_jobs (id, user_id, analysis_id, s3_audio_key, status, error_message, created_at, updated_at, interviewer_id) FROM stdin;
466e5869-01e9-4324-896f-1a4972d17e5b	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/472a0263-4a5b-44ea-be7b-a1f8584f86ae/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-18 23:31:43.108289	2026-01-18 23:31:43.108672	\N
2de06feb-9247-4429-bfae-8bb19a8cfebe	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/8c3d88e2-0c4a-4998-9ee8-0840ee320d44/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-18 23:31:45.669932	2026-01-18 23:31:45.670185	\N
e9555a49-5aa7-424c-9fb7-bbdd3c87a4d2	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/0eb40fb1-76be-438f-8827-9cacbf236ac5/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-18 23:31:49.939634	2026-01-18 23:31:49.94	\N
b2b8009e-4b63-429e-a131-76fea57e0686	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/59a1cd7b-f7e2-4bde-b2c0-65e05f08b3a2/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:42:22.214765	2026-01-19 06:42:22.214935	\N
5adf3dfd-a8e8-4edf-ac73-cff0916e83b1	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/54591cd5-a218-495a-a0ea-6283d317e968/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:42:25.407113	2026-01-19 06:42:25.407279	\N
b353ce7c-c0e0-4b0f-96c4-ba9e805338c8	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/c28332a7-e2c8-4673-a3ab-8cd0d17379d3/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:42:27.535426	2026-01-19 06:42:27.535564	\N
eda84fe1-ccb5-40cc-bd42-8567109abb60	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/d40d1ad7-eaf1-40b7-ba09-6886e64c498e/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:45:23.985634	2026-01-19 06:45:23.9859	\N
72d48983-0022-488f-b362-53b9094b8645	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/f8d47ce2-dcc4-45db-996b-f0bf5662ec9a/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:45:26.192973	2026-01-19 06:45:26.193352	\N
f63f5d55-67a5-45dc-be0e-eea7e4da3209	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/fe58c654-fb63-4397-8784-a7fdb587da63/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:46:10.737822	2026-01-19 06:46:10.73811	\N
2a2aeb01-c851-4be8-8894-6838445c986d	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/59db9ee1-63df-4fe2-898f-7dc2231d3175/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:46:22.962991	2026-01-19 06:46:22.963184	\N
a248b691-af92-4fcb-ac69-c513573ede96	a20f008c-7c8c-4d8a-883a-ad56e1d16d59	\N	uploads/a20f008c-7c8c-4d8a-883a-ad56e1d16d59/1f29640a-7ef1-414e-8462-6978b9cee414/The Power of We [511j63ZjzoQ].mp3	PENDING	\N	2026-01-19 06:47:41.442003	2026-01-19 06:47:41.442193	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, provider, email, credits, created_at, updated_at, hashed_password, oauth_id) FROM stdin;
00000000-0000-0000-0000-000000000000	LOCAL	guest@vibecheck.dev	0	2026-01-18 22:46:29.013027	2026-01-18 22:46:29.013184	\N	\N
a20f008c-7c8c-4d8a-883a-ad56e1d16d59	LOCAL	test@example.com	0	2026-01-18 22:50:30.973691	2026-01-18 22:50:30.973825	$2b$12$F.UoixkJ09ZDvg1fSwsdk.UhTgsaWjo1UrIBkiXf6jh9KrtE4njmS	\N
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: interview_analyses interview_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_analyses
    ADD CONSTRAINT interview_analyses_pkey PRIMARY KEY (id);


--
-- Name: interviewers interviewers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviewers
    ADD CONSTRAINT interviewers_pkey PRIMARY KEY (id);


--
-- Name: processing_jobs processing_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.processing_jobs
    ADD CONSTRAINT processing_jobs_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_interview_analyses_interviewer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_interview_analyses_interviewer_id ON public.interview_analyses USING btree (interviewer_id);


--
-- Name: ix_interview_analyses_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_interview_analyses_user_id ON public.interview_analyses USING btree (user_id);


--
-- Name: ix_interviewers_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_interviewers_company ON public.interviewers USING btree (company);


--
-- Name: ix_interviewers_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_interviewers_name ON public.interviewers USING btree (name);


--
-- Name: ix_interviewers_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_interviewers_user_id ON public.interviewers USING btree (user_id);


--
-- Name: ix_processing_jobs_interviewer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_processing_jobs_interviewer_id ON public.processing_jobs USING btree (interviewer_id);


--
-- Name: ix_processing_jobs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_processing_jobs_status ON public.processing_jobs USING btree (status);


--
-- Name: ix_processing_jobs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_processing_jobs_user_id ON public.processing_jobs USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_oauth_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_oauth_id ON public.users USING btree (oauth_id);


--
-- Name: ix_users_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_provider ON public.users USING btree (provider);


--
-- Name: interviewers fk_interviewers_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviewers
    ADD CONSTRAINT fk_interviewers_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: processing_jobs fk_processing_jobs_interviewer_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.processing_jobs
    ADD CONSTRAINT fk_processing_jobs_interviewer_id FOREIGN KEY (interviewer_id) REFERENCES public.interviewers(id);


--
-- Name: interview_analyses interview_analyses_interviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_analyses
    ADD CONSTRAINT interview_analyses_interviewer_id_fkey FOREIGN KEY (interviewer_id) REFERENCES public.interviewers(id) ON DELETE CASCADE;


--
-- Name: interview_analyses interview_analyses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_analyses
    ADD CONSTRAINT interview_analyses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: processing_jobs processing_jobs_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.processing_jobs
    ADD CONSTRAINT processing_jobs_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.interview_analyses(id) ON DELETE SET NULL;


--
-- Name: processing_jobs processing_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.processing_jobs
    ADD CONSTRAINT processing_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict el2CjlITbkSatz9b4klR1cgJlPk0x17BsC8AWRV4dOx2SwutWdAGPsvSUfq5MFd

