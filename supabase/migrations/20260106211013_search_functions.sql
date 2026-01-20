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

-- Persisted search vectors and indexes for efficient lookups
alter table if exists works
    add column if not exists search_vector tsvector
        generated always as (to_tsvector('simple', trim(
            coalesce(title, '') || ' ' ||
            coalesce(titles::text, '') || ' ' ||
            coalesce(description, '') || ' ' ||
            coalesce(identifiers::text, '')
        ))) stored;
create index if not exists works_search_vector_idx on works using gin (search_vector);

alter table if exists versions
    add column if not exists search_vector tsvector
        generated always as (to_tsvector('simple', coalesce(title, ''))) stored;
create index if not exists versions_search_vector_idx on versions using gin (search_vector);

alter table if exists releases
    add column if not exists search_vector tsvector
        generated always as (to_tsvector('simple', trim(
            coalesce(release_title, '') || ' ' ||
            coalesce(catalog_number, '') || ' ' ||
            coalesce(publisher_number, '')
        ))) stored;
create index if not exists releases_search_vector_idx on releases using gin (search_vector);

alter table if exists artists
    add column if not exists search_vector tsvector
        generated always as (to_tsvector('simple', trim(
            coalesce(display_name, '') || ' ' ||
            coalesce(sort_name, '') || ' ' ||
            coalesce(alternative_names::text, '')
        ))) stored;
create index if not exists artists_search_vector_idx on artists using gin (search_vector);

alter table if exists persons
    add column if not exists search_vector tsvector
        generated always as (to_tsvector('simple', coalesce(legal_name, ''))) stored;
create index if not exists persons_search_vector_idx on persons using gin (search_vector);

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
    ),
    work_matches as (
        select 'work'::public.entity_type as entity_type,
               w.work_id as entity_id,
               w.title as display_text,
               ts_rank_cd(w.search_vector, q.tsq) as rank
        from works w, q
        where w.search_vector @@ q.tsq
        order by rank desc
        limit fetch_limit
    ),
    version_matches as (
        select 'version'::public.entity_type,
               v.version_id,
               v.title,
             ts_rank_cd(v.search_vector, q.tsq) as rank
        from versions v, q
        where v.search_vector @@ q.tsq
         order by rank desc
        limit fetch_limit
    ),
    release_matches as (
        select 'release'::public.entity_type,
               r.release_id,
               r.release_title,
             ts_rank_cd(r.search_vector, q.tsq) as rank
        from releases r, q
        where r.search_vector @@ q.tsq
         order by rank desc
        limit fetch_limit
    ),
    artist_matches as (
        select 'artist'::public.entity_type,
               a.artist_id,
               a.display_name,
             ts_rank_cd(a.search_vector, q.tsq) as rank
        from artists a, q
        where a.search_vector @@ q.tsq
         order by rank desc
        limit fetch_limit
    ),
    person_matches as (
        select 'person'::public.entity_type,
               p.person_id,
               p.legal_name,
             ts_rank_cd(p.search_vector, q.tsq) as rank
        from persons p, q
        where p.search_vector @@ q.tsq
         order by rank desc
        limit fetch_limit
    )
    select *
    from (
        select * from work_matches
        union all
        select * from version_matches
        union all
        select * from release_matches
        union all
        select * from artist_matches
        union all
        select * from person_matches
    ) as combined
    order by rank desc
    limit fetch_limit;
$$;