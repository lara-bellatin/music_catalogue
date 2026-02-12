-- Improve the unified search function to include secondary display text that provides more context for the search result

-- Drop first to modify return type
drop function if exists unified_search;

-- Create modified version
create function unified_search(query_text text, fetch_limit int default 20)
returns table (
    entity_type public.entity_type,
    entity_id uuid,
    display_text text,
    secondary_text text,
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
               array_to_string(array[w.origin_year_start, w.origin_year_end], '-') as secondary_text,
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
               a.display_name as secondary_text,
               ts_rank_cd(v.search_vector, q.tsq) as rank
        from versions v
        cross join q
        left join artists a on v.primary_artist_id = a.artist_id
        where v.search_vector @@ q.tsq
        order by rank desc
        limit fetch_limit
    ),
    release_matches as (
        select 'release'::public.entity_type,
               r.release_id,
               r.release_title,
               r.release_category::text as secondary_text,
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
               a.artist_type::text as secondary_text,
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
               array_to_string(array[extract(year from p.birth_date)::int::text, coalesce(extract(year from p.death_date)::int::text, 'Alive')], '-') as secondary_text,
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
