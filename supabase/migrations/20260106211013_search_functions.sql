-- Create search functions for artists, persons, work and combinations for unified search

-- Work Search
create or replace function search_text(works) returns text as $$
    select
        trim(
            coalesce($1.title, '') || ' ' ||
            coalesce($1.titles::text, '') || ' ' ||
            coalesce($1.description, '') || ' ' ||
            coalesce($1.identifiers::text, '')
        );
$$ language sql immutable;

-- Version Search
create or replace function search_text(versions) returns text as $$
    select
        trim(
            coalesce($1.title, '')
        );
$$ language sql immutable;

-- Release Search
create or replace function search_text(releases) returns text as $$
    select
        trim(
            coalesce($1.release_title, '') || ' ' ||
            coalesce($1.catalog_number, '') || ' ' ||
            coalesce($1.publisher_number, '')
        );
$$ language sql immutable;

-- Artist Search
create or replace function search_text(artists) returns text as $$
    select
        trim(
            coalesce($1.display_name, '') || ' ' ||
            coalesce($1.sort_name, '') || ' ' ||
            coalesce($1.alternative_names::text, '')
        );
$$ language sql immutable;

-- Person Search
create or replace function search_text(persons) returns text as $$
    select
        trim(
            coalesce($1.legal_name, '')
        );
$$ language sql immutable;

-- Unified Search (all entity types minus media item, credit and genre)
create or replace function unified_search(query_text text, fetch_limit int default 20)
returns table (
    entity_type public.entity_type,
    entity_id uuid,
    display_text text,
    rank real
)
language sql
as $$
    with q as (
        select websearch_to_tsquery('simple', query_text) as tsq
    )
    select 'work'::public.entity_type as entity_type,
           w.work_id as entity_id,
           w.title as display_text,
           ts_rank_cd(to_tsvector('simple', search_text(w)), q.tsq) as rank
    from works w, q
    where to_tsvector('simple', search_text(w)) @@ q.tsq

    union all

    select 'version'::public.entity_type,
           v.version_id,
           v.title,
           ts_rank_cd(to_tsvector('simple', search_text(v)), q.tsq)
    from versions v, q
    where to_tsvector('simple', search_text(v)) @@ q.tsq

    union all

    select 'release'::public.entity_type,
           r.release_id,
           r.release_title,
           ts_rank_cd(to_tsvector('simple', search_text(r)), q.tsq)
    from releases r, q
    where to_tsvector('simple', search_text(r)) @@ q.tsq

    union all

    select 'artist'::public.entity_type,
           a.artist_id,
           a.display_name,
           ts_rank_cd(to_tsvector('simple', search_text(a)), q.tsq)
    from artists a, q
    where to_tsvector('simple', search_text(a)) @@ q.tsq

    union all

    select 'person'::public.entity_type,
           p.person_id,
           p.legal_name,
           ts_rank_cd(to_tsvector('simple', search_text(p)), q.tsq)
    from persons p, q
    where to_tsvector('simple', search_text(p)) @@ q.tsq

    order by rank desc
    limit fetch_limit;
$$;