--
-- PostgreSQL database dump
--

\restrict 64Mc1VdHtpcriF50bJjjngKeKUs4hk1yQhEEJJXcv9ZNRq6Ve4CcjDkYYP8m9fK

-- Dumped from database version 18.6 (Postgres.app)
-- Dumped by pg_dump version 18.6 (Homebrew)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: gassco_umm_import; Type: TABLE; Schema: raw; Owner: -
--

CREATE TABLE raw.gassco_umm_import (
    message_id text,
    asset text,
    event_status text,
    unavailability_type text,
    event_type text,
    publication_time timestamp without time zone,
    event_start timestamp without time zone,
    event_stop timestamp without time zone,
    unit text,
    technical_capacity numeric,
    available_capacity numeric,
    unavailable_capacity numeric,
    reason text,
    remarks text,
    balancing_zone text,
    market_participant text,
    market_participant_code text,
    asset_eic_code text,
    source_year smallint,
    source_file text,
    source_excel_row integer
);


--
-- Name: gassco_umm_messages; Type: VIEW; Schema: core; Owner: -
--

CREATE VIEW core.gassco_umm_messages AS
 SELECT message_id,
    asset,
    event_status,
    unavailability_type,
    event_type,
    publication_time,
    event_start,
    event_stop,
    unit,
    technical_capacity,
    available_capacity,
    unavailable_capacity,
    reason,
    remarks,
    balancing_zone,
    market_participant,
    market_participant_code,
    asset_eic_code,
    source_year,
    source_file,
    source_excel_row,
    regexp_replace(message_id, '_+[0-9]{3}$'::text, ''::text) AS event_key,
    ("substring"(message_id, '([0-9]{3})$'::text))::integer AS revision,
    (EXTRACT(epoch FROM (event_start - publication_time)) / 3600.0) AS lead_hours,
    (EXTRACT(epoch FROM (event_stop - event_start)) / 3600.0) AS duration_hours,
    (technical_capacity - available_capacity) AS calculated_unavailable_capacity,
    (unavailable_capacity - (technical_capacity - available_capacity)) AS capacity_reporting_gap,
    (unavailable_capacity < (0)::numeric) AS negative_unavailable_flag
   FROM raw.gassco_umm_import;


--
-- Name: gassco_umm_events_audited; Type: VIEW; Schema: core; Owner: -
--

CREATE VIEW core.gassco_umm_events_audited AS
 WITH audited AS (
         SELECT m.message_id,
            m.asset,
            m.event_status,
            m.unavailability_type,
            m.event_type,
            m.publication_time,
            m.event_start,
            m.event_stop,
            m.unit,
            m.technical_capacity,
            m.available_capacity,
            m.unavailable_capacity,
            m.reason,
            m.remarks,
            m.balancing_zone,
            m.market_participant,
            m.market_participant_code,
            m.asset_eic_code,
            m.source_year,
            m.source_file,
            m.source_excel_row,
            m.event_key,
            m.revision,
            m.lead_hours,
            m.duration_hours,
            m.calculated_unavailable_capacity,
            m.capacity_reporting_gap,
            m.negative_unavailable_flag,
            (m.technical_capacity - m.available_capacity) AS expected_unavailable_msm3d,
            (m.unavailable_capacity - (m.technical_capacity - m.available_capacity)) AS capacity_gap_msm3d,
                CASE
                    WHEN ((m.technical_capacity IS NULL) OR (m.available_capacity IS NULL) OR (m.unavailable_capacity IS NULL)) THEN 'missing_capacity'::text
                    WHEN (abs((m.unavailable_capacity - (m.technical_capacity - m.available_capacity))) <= 0.11) THEN 'valid_within_rounding'::text
                    WHEN (abs((m.unavailable_capacity - (m.available_capacity - m.technical_capacity))) <= 0.11) THEN 'reversed_sign'::text
                    ELSE 'inconsistent_amount'::text
                END AS capacity_quality_status
           FROM core.gassco_umm_messages m
        )
 SELECT message_id,
    asset,
    event_status,
    unavailability_type,
    event_type,
    publication_time,
    event_start,
    event_stop,
    unit,
    technical_capacity,
    available_capacity,
    unavailable_capacity,
    reason,
    remarks,
    balancing_zone,
    market_participant,
    market_participant_code,
    asset_eic_code,
    source_year,
    source_file,
    source_excel_row,
    event_key,
    revision,
    lead_hours,
    duration_hours,
    calculated_unavailable_capacity,
    capacity_reporting_gap,
    negative_unavailable_flag,
    expected_unavailable_msm3d,
    capacity_gap_msm3d,
    capacity_quality_status,
        CASE
            WHEN ((capacity_quality_status = 'valid_within_rounding'::text) AND (unavailable_capacity > (0)::numeric)) THEN 'capacity_reduction'::text
            WHEN ((capacity_quality_status = 'valid_within_rounding'::text) AND (unavailable_capacity < (0)::numeric)) THEN 'capacity_increase'::text
            WHEN ((capacity_quality_status = 'valid_within_rounding'::text) AND (unavailable_capacity = (0)::numeric)) THEN 'no_capacity_change'::text
            ELSE 'unresolved'::text
        END AS capacity_direction,
        CASE
            WHEN ((capacity_quality_status = 'valid_within_rounding'::text) AND (unavailable_capacity > (0)::numeric)) THEN unavailable_capacity
            ELSE NULL::numeric
        END AS outage_size_msm3d,
        CASE
            WHEN ((capacity_quality_status = 'valid_within_rounding'::text) AND (unavailable_capacity < (0)::numeric)) THEN abs(unavailable_capacity)
            ELSE NULL::numeric
        END AS capacity_increase_msm3d
   FROM audited;


--
-- Name: gassco_primary_reduction_events; Type: VIEW; Schema: mart; Owner: -
--

CREATE VIEW mart.gassco_primary_reduction_events AS
 SELECT event_key,
    message_id,
    asset,
    event_type,
    unavailability_type,
    event_status,
    publication_time,
    event_start,
    event_stop,
    lead_hours,
    duration_hours,
    technical_capacity,
    available_capacity,
    unavailable_capacity,
    outage_size_msm3d,
    reason,
    remarks,
    source_year,
    source_file,
    source_excel_row,
    revision,
        CASE
            WHEN (lead_hours < (0)::numeric) THEN 'published_after_start'::text
            ELSE 'published_before_or_at_start'::text
        END AS publication_timing_group
   FROM core.gassco_umm_events_audited
  WHERE ((revision = 1) AND (event_status <> 'Dismissed'::text) AND (capacity_quality_status = 'valid_within_rounding'::text) AND (capacity_direction = 'capacity_reduction'::text));


--
-- PostgreSQL database dump complete
--

\unrestrict 64Mc1VdHtpcriF50bJjjngKeKUs4hk1yQhEEJJXcv9ZNRq6Ve4CcjDkYYP8m9fK

