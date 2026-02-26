-- Migration: 20260226021820_performance_identifiers.sql
-- Add identifiers column to performances

alter table public.performances add column identifiers jsonb;
