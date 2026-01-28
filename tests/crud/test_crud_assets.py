"""
Unit tests for CRUD operations on assets CRUD module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from music_catalogue.crud import assets
from music_catalogue.models.types import EntityType


class TestAssetsCRUD:
    """Tests for assets CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_external_links_success(self):
        """Test successfully retrieving external links for an entity."""
        entity_type = EntityType.WORK
        entity_id = "work-1"
        mock_links_data = [
            {
                "link_id": "link-1",
                "entity_type": "work",
                "entity": {"work_id": entity_id},
                "label": "IMSLP",
                "url": "https://imslp.org/work",
                "added_by": {"user_id": "user-1"},
                "created_at": "2025-01-26",
                "source_verified": True,
            },
            {
                "link_id": "link-2",
                "entity_type": "work",
                "entity": {"work_id": entity_id},
                "label": "Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Work",
                "added_by": {"user_id": "user-2"},
                "created_at": "2025-01-25",
                "source_verified": False,
            },
        ]

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_links_data))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.assets.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.assets.validate_uuid", return_value=None) as mock_validate_uuid,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await assets.get_external_links_raw(entity_type, entity_id)

            assert result is mock_links_data
            mock_validate_uuid.assert_called_once_with(entity_id)
            mock_supabase.table.assert_called_once_with("external_links")

    @pytest.mark.asyncio
    async def test_get_external_links_empty_result(self):
        """Test retrieving external links when none exist for an entity."""
        entity_type = EntityType.ARTIST
        entity_id = "artist-1"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.assets.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.assets.validate_uuid", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await assets.get_external_links_raw(entity_type, entity_id)

            assert result == []
