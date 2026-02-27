-- Migration: 20260227000809_work_derivation.sql
-- Add based_on_work_id to works table

alter table if exists works
add column if not exists based_on_work_id uuid,
add constraint fk_works_based_on_work foreign key (based_on_work_id) references works (work_id);
