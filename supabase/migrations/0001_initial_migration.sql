-- Initial Migration

-- Create types
do $$
begin
    if not exists (select 1 from pg_type where typname = 'user_role' and typnamespace = 'public'::regnamespace) then
        create type public.user_role as enum ('member', 'moderator', 'admin');
    end if;

    if not exists (select 1 from pg_type where typname = 'artist_type' and typnamespace = 'public'::regnamespace) then
        create type public.artist_type as enum ('solo', 'group');
    end if;

    if not exists (select 1 from pg_type where typname = 'version_type' and typnamespace = 'public'::regnamespace) then
        create type public.version_type as enum ('original', 'cover', 'remix', 'live', 'parody', 'mashup', 'demo', 'radio_edit', 'other');
    end if;

    if not exists (select 1 from pg_type where typname = 'completeness_level' and typnamespace = 'public'::regnamespace) then
        create type public.completeness_level as enum ('sparse', 'partial', 'complete');
    end if;

    if not exists (select 1 from pg_type where typname = 'release_category' and typnamespace = 'public'::regnamespace) then
        create type public.release_category as enum ('single', 'ep', 'album', 'compilation', 'live', 'soundtrack', 'deluxe', 'other');
    end if;

    if not exists (select 1 from pg_type where typname = 'release_stage' and typnamespace = 'public'::regnamespace) then
        create type public.release_stage as enum ('initial', 'reissue', 'remaster', 'anniversary', 'other');
    end if;

    if not exists (select 1 from pg_type where typname = 'medium_type' and typnamespace = 'public'::regnamespace) then
        create type public.medium_type as enum ('digital', 'physical');
    end if;

    if not exists (select 1 from pg_type where typname = 'audio_channels' and typnamespace = 'public'::regnamespace) then
        create type public.audio_channels as enum ('mono', 'stereo', 'surround', 'dolby_atmos');
    end if;

    if not exists (select 1 from pg_type where typname = 'availability_status' and typnamespace = 'public'::regnamespace) then
        create type public.availability_status as enum ('in_print', 'limited', 'out_of_print', 'digital_only');
    end if;

    if not exists (select 1 from pg_type where typname = 'entity_type' and typnamespace = 'public'::regnamespace) then
        create type public.entity_type as enum ('person', 'artist', 'work', 'version', 'release', 'media_item', 'credit');
    end if;

    if not exists (select 1 from pg_type where typname = 'asset_type' and typnamespace = 'public'::regnamespace) then
        create type public.asset_type as enum ('mei', 'score_image', 'lead_sheet', 'lyrics', 'other');
    end if;

    if not exists (select 1 from pg_type where typname = 'contribution_status' and typnamespace = 'public'::regnamespace) then
        create type public.contribution_status as enum ('pending', 'approved', 'rejected');
    end if;

    if not exists (select 1 from pg_type where typname = 'collection_item_owner_type' and typnamespace = 'public'::regnamespace) then
        create type public.collection_item_owner_type as enum ('institution','collector');
    end if;
end $$;

begin;
-- Create tables
create table if not exists users (
    user_id uuid primary key default gen_random_uuid(),
    display_name text not null,
    email text not null unique,
    hashed_password text not null,
    trust_score int default 0,
    role public.user_role not null default 'member',
    created_at timestamp default now()
);

create table if not exists persons (
    person_id uuid primary key default gen_random_uuid(),
    legal_name text not null,
    birth_date date,
    death_date date,
    pronouns text,
    notes text
);

create table if not exists artists (
    artist_id uuid primary key default gen_random_uuid(),
    person_id uuid,
    artist_type public.artist_type not null,
    display_name text not null,
    sort_name text,
    start_date date,
    end_date date,
    alternative_names text[],
    notes text,
    constraint fk_artists_person foreign key (person_id) references persons(person_id)
);

create unique index uq_artists_person_display on artists(person_id, display_name);

create table if not exists artist_memberships (
    membership_id uuid primary key default gen_random_uuid(),
    group_id uuid,
    member_artist_id uuid,
    role text,
    start_date date,
    end_date date,
    notes text,
    constraint fk_artist_memberships_group foreign key (group_id) references artists(artist_id) on delete cascade,
    constraint fk_artist_memberships_member foreign key (member_artist_id) references persons(person_id) on delete cascade
);

create table if not exists works (
    work_id uuid primary key default gen_random_uuid(),
    title text not null,
    normalized_title text,
    description text,
    origin_year int,
    origin_country text,
    themes text[],
    sentiment text,
    notes text
);

create table if not exists versions (
    version_id uuid primary key default gen_random_uuid(),
    work_id uuid,
    title text not null,
    version_type public.version_type not null default 'original',
    based_on_version_id uuid,
    primary_artist_id uuid,
    release_date date,
    duration_seconds int,
    bpm int,
    key_signature text,
    lyrics_reference text,
    completeness_level public.completeness_level not null default 'complete',
    notes text,
    constraint fk_versions_work foreign key (work_id) references works(work_id) on delete cascade,
    constraint fk_versions_based_on foreign key (based_on_version_id) references versions(version_id),
    constraint fk_versions_primary_artist foreign key (primary_artist_id) references artists(artist_id)
);

create table if not exists releases (
    release_id uuid primary key default gen_random_uuid(),
    release_title text not null,
    release_date date,
    release_category public.release_category not null default 'single',
    catalog_number text,
    publisher_number text,
    label text,
    region text,
    release_stage public.release_stage not null default 'initial',
    cover_art_url text,
    total_discs int default 1,
    total_tracks int not null,
    notes text
);

create table if not exists release_media_items (
    media_item_id uuid primary key default gen_random_uuid(),
    release_id uuid,
    medium_type public.medium_type not null,
    format_name text not null,
    platform_or_vendor text,
    bitrate_kbps int,
    sample_rate_hz int,
    bit_depth int,
    rpm numeric(4,1),
    channels public.audio_channels,
    packaging text,
    accessories text,
    pressing_details jsonb,
    sku text,
    barcode text,
    catalog_variation text,
    availability_status public.availability_status not null default 'in_print',
    notes text,
    constraint fk_release_media_items_release foreign key (release_id) references releases(release_id) on delete cascade
);

create table if not exists release_tracks (
    release_track_id uuid primary key default gen_random_uuid(),
    release_id uuid,
    version_id uuid,
    disc_number int default 1,
    track_number int not null,
    side text,
    is_hidden_track boolean default false,
    notes text,
    constraint fk_release_tracks_release foreign key (release_id) references releases(release_id) on delete cascade,
    constraint fk_release_tracks_version foreign key (version_id) references versions(version_id)
);

create unique index uq_release_tracks_position on release_tracks(release_id, disc_number, track_number);

create table if not exists credits (
    credit_id uuid primary key default gen_random_uuid(),
    version_id uuid not null,
    artist_id uuid,
    person_id uuid,
    role text not null,
    is_primary boolean default false,
    credit_order int,
    instruments text[],
    notes text,
    constraint fk_credits_version foreign key (version_id) references versions(version_id) on delete cascade,
    constraint fk_credits_artist foreign key (artist_id) references artists(artist_id),
    constraint fk_credits_person foreign key (person_id) references persons(person_id)
);

create table if not exists genres (
    genre_id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text
);

create table if not exists work_genres (
    work_id uuid not null,
    genre_id uuid not null,
    primary key (work_id, genre_id),
    constraint fk_work_genres_work foreign key (work_id) references works(work_id),
    constraint fk_work_genres_genre foreign key (genre_id) references genres(genre_id)
);

create table if not exists tags (
    tag_id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text
);

create table if not exists tag_assignments (
    tag_assignment_id uuid primary key default gen_random_uuid(),
    tag_id uuid,
    entity_type public.entity_type not null,
    entity_id uuid not null,
    user_id uuid not null,
    confidence smallint check (confidence between 1 and 5),
    created_at timestamp default now(),
    constraint fk_tag_assignments_tag foreign key (tag_id) references tags(tag_id),
    constraint fk_tag_assignments_user foreign key (user_id) references users(user_id)
);

create table if not exists external_links (
    link_id uuid primary key default gen_random_uuid(),
    entity_type public.entity_type not null,
    entity_id uuid not null,
    label text not null,
    url text not null,
    source_verified boolean default false,
    added_by uuid,
    created_at timestamp default now(),
    constraint fk_external_links_user foreign key (added_by) references users(user_id)
);

create table if not exists evidence (
    evidence_id uuid primary key default gen_random_uuid(),
    entity_type public.entity_type not null,
    entity_id uuid not null,
    source_type text,
    source_detail text,
    file_url text,
    uploaded_by uuid,
    verified boolean default false,
    created_at timestamp default now(),
    constraint fk_evidence_uploaded_by foreign key (uploaded_by) references users(user_id)
);

create table if not exists notation_assets (
    asset_id uuid primary key default gen_random_uuid(),
    entity_type public.entity_type,
    entity_id uuid not null,
    asset_type public.asset_type not null,
    file_url text not null,
    mime_type text,
    uploaded_by uuid,
    created_at timestamp default now(),
    constraint fk_notation_assets_uploaded_by foreign key (uploaded_by) references users(user_id)
);

create table if not exists contributions (
    contribution_id uuid primary key default gen_random_uuid(),
    user_id uuid,
    entity_type public.entity_type,
    entity_id uuid,
    change_summary text,
    status public.contribution_status not null default 'pending',
    created_at timestamp default now(),
    reviewed_by uuid,
    constraint fk_contributions_user foreign key (user_id) references users(user_id),
    constraint fk_contributions_reviewed_by foreign key (reviewed_by) references users(user_id)
);

create table if not exists collection_items (
    collection_item_id uuid primary key default gen_random_uuid(),
    media_item_id uuid,
    owner_type public.collection_item_owner_type not null default 'collector',
    owner_name text,
    location text,
    condition_grade text,
    acquisition_date date,
    notes text,
    constraint fk_collection_items_media foreign key (media_item_id) references release_media_items(media_item_id) on delete cascade
);

alter table if exists users enable row level security;
alter table if exists persons enable row level security;
alter table if exists artists enable row level security;
alter table if exists artist_memberships enable row level security;
alter table if exists works enable row level security;
alter table if exists versions enable row level security;
alter table if exists releases enable row level security;
alter table if exists release_media_items enable row level security;
alter table if exists release_tracks enable row level security;
alter table if exists credits enable row level security;
alter table if exists genres enable row level security;
alter table if exists work_genres enable row level security;
alter table if exists tags enable row level security;
alter table if exists tag_assignments enable row level security;
alter table if exists external_links enable row level security;
alter table if exists evidence enable row level security;
alter table if exists notation_assets enable row level security;
alter table if exists contributions enable row level security;
alter table if exists collection_items enable row level security;

commit;