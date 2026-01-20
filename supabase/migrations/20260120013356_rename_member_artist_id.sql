-- Migration: 20260120013356_rename_member_artist_id.sql
-- Rename column member_artist_id to person_id in artist_memberships table

alter table public.artist_memberships
    rename column member_artist_id to person_id;
