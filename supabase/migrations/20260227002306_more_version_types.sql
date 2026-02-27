-- Migration: 20260227002306_more_version_types.sql
-- Add new version types to accomodate more types of derivation

alter type public.version_type add value if not exists 'acoustic';

alter type public.version_type add value if not exists 'instrumental';

alter type public.version_type add value if not exists 'a_cappella';

alter type public.version_type add value if not exists 'extended';

alter type public.version_type add value if not exists 'remaster';

alter type public.version_type add value if not exists 'arrangement';

alter type public.version_type add value if not exists 'transcription';

alter type public.version_type add value if not exists 'excerpt';

alter type public.version_type add value if not exists 'medley';
