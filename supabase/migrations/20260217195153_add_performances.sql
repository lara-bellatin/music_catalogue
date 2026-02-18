-- Migration: 20260217195153_add_performances.sql
-- Add performances tables for tracking live concerts and classical programmes

-- Add 'performance' to entity_type enum
alter type public.entity_type add value 'performance';

-- Create performances table
create table if not exists performances (
    performance_id uuid primary key default gen_random_uuid(),
    name text not null,
    performance_date date,
    venue text,
    city text,
    country text,
    notes text,
    search_vector tsvector generated always as (
        to_tsvector('simple', trim(
            coalesce(name, '') || ' ' ||
            coalesce(venue, '') || ' ' ||
            coalesce(city, '')
        ))
    ) stored
);

create index if not exists performances_search_vector_idx on performances using gin (search_vector);

-- Create performance artists table
create table if not exists performance_artists (
    performance_artist_id uuid primary key default gen_random_uuid(),
    performance_id uuid not null,
    artist_id uuid,
    person_id uuid,
    role text,
    billing_order int,
    notes text,
    constraint fk_performance_artists_performance foreign key (performance_id) references performances(performance_id) on delete cascade,
    constraint fk_performance_artists_artist foreign key (artist_id) references artists(artist_id),
    constraint fk_performance_artists_person foreign key (person_id) references persons(person_id),
    constraint chk_performance_artists_one_entity check (
        (artist_id is not null and person_id is null) or
        (artist_id is null and person_id is not null)
    )
);

-- Create performance works table
create table if not exists performance_works (
    performance_work_id uuid primary key default gen_random_uuid(),
    performance_id uuid not null,
    work_id uuid,
    version_id uuid,
    set_order int,
    set_name text,
    notes text,
    constraint fk_performance_works_performance foreign key (performance_id) references performances(performance_id) on delete cascade,
    constraint fk_performance_works_work foreign key (work_id) references works(work_id),
    constraint fk_performance_works_version foreign key (version_id) references versions(version_id),
    constraint chk_performance_works_at_least_one check (
        work_id is not null or version_id is not null
    )
);

create unique index if not exists uq_performance_works_order on performance_works(performance_id, set_order);

-- Enable RLS
alter table if exists performances enable row level security;
alter table if exists performance_artists enable row level security;
alter table if exists performance_works enable row level security;
