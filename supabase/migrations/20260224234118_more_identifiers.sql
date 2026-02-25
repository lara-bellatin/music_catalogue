-- Migration 20260224234118_more_identifiers.sql
-- Add an identifiers column to tables persons, versions, releases, etc.

alter table public.persons add column identifiers jsonb;

alter table public.versions add column identifiers jsonb;

alter table public.releases add column identifiers jsonb;

alter table public.release_media_items add column identifiers jsonb;

alter table public.collection_items add column identifiers jsonb;

alter table public.evidence add column identifiers jsonb;
