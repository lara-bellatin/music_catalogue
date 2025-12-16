-- Add more properties needed for classical music

alter table if exists works
    add column if not exists identifiers jsonb,
    drop column if exists normalized_title,
    add column if not exists titles jsonb,
    add column if not exists language text,
    drop column origin_year,
    add column origin_year_start int,
    add column origin_year_end int;

alter table if exists versions
    add column if not exists release_year int;

alter table if exists artists
    drop column if exists start_date,
    drop column if exists end_date,
    add column if not exists start_year int,
    add column if not exists end_year int;

alter table if exists artist_memberships
    drop column if exists start_date,
    drop column if exists end_date,
    add column if not exists start_year int,
    add column if not exists end_year int;

alter table if exists credits
    add column if not exists work_id uuid,
    alter column version_id drop not null,
    add constraint fk_credits_work_id foreign key (work_id) references works(work_id);