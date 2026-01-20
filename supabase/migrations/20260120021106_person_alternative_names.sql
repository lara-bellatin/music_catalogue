-- Migration: 20260120021106_person_alternative_names.sql
-- Add column alternative_names to persons table to log nicknames and name changes

alter table public.persons
    add column if not exists alternative_names jsonb,
    alter column search_vector set expression as (to_tsvector('simple', trim(
            coalesce(legal_name, '') || ' ' ||
            coalesce(alternative_names::text, '')
        )));

create or replace function search_text(persons) returns text as $$
    select
        trim(
            coalesce($1.legal_name, '') || ' ' ||
            coalesce($1.alternative_names::text, '')
        );
$$ language sql immutable;

