-- Add release_id to credits table so credits can be associated with releases
alter table if exists credits
add column if not exists release_id uuid,
add constraint fk_credits_release foreign key (release_id) references releases (release_id) on delete cascade;

-- Add primary_artist_id to releases table
alter table if exists releases
add column if not exists primary_artist_id uuid,
add constraint fk_releases_primary_artist foreign key (primary_artist_id) references artists (artist_id);

-- Add identifiers to release_tracks table
alter table if exists release_tracks
add column if not exists identifiers jsonb;
