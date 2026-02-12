"""Unit tests for CatalogueModel base class."""

from typing import ClassVar, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.types import EntityType


# Concrete subclass for testing
class FakeEntity(CatalogueModel):
    table_name: ClassVar[str] = "fake_entities"
    pk_column: ClassVar[str] = "fake_id"
    query: ClassVar[str] = "fake_id, name"
    search_query: ClassVar[Optional[str]] = "fake_id, name"
    entity_type: ClassVar[Optional[EntityType]] = EntityType.WORK

    id: str
    name: str
    external_links: Optional[List[ExternalLink]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "FakeEntity":
        return cls(id=data["fake_id"], name=data["name"])


class FakeEntityCreate(BaseModel):
    name: str
    external_links: Optional[list] = None


def _mock_supabase():
    """Create a MagicMock Supabase client with chained query builder."""
    mock = MagicMock()
    builder = MagicMock()
    builder.select.return_value = builder
    builder.eq.return_value = builder
    builder.single.return_value = builder
    builder.insert.return_value = builder
    builder.delete.return_value = builder
    builder.text_search.return_value = builder
    mock.table.return_value = builder
    return mock, builder


class TestFromDict:
    """Tests for CatalogueModel.from_dict base behavior."""

    def test_from_dict_raises_not_implemented(self):
        with pytest.raises(NotImplementedError) as exc_info:
            CatalogueModel.from_dict({"some": "data"})

        assert "CatalogueModel must implement from_dict" in str(exc_info.value)


class TestGetById:
    """Tests for CatalogueModel.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, sample_uuid):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data={"fake_id": sample_uuid, "name": "Test"}))

        with (
            patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch.object(FakeEntity, "_get_external_links", new_callable=AsyncMock) as mock_links,
        ):
            mock_get_supabase.return_value = mock_supabase
            mock_links.return_value = []

            result = await FakeEntity.get_by_id(sample_uuid)

            assert result is not None
            assert result.id == sample_uuid
            assert result.name == "Test"
            mock_supabase.table.assert_called_once_with("fake_entities")

    @pytest.mark.asyncio
    async def test_get_by_id_not_found_empty_data(self, sample_uuid):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=None))

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            result = await FakeEntity.get_by_id(sample_uuid)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_not_found_pgrst116(self, sample_uuid):
        from supabase import PostgrestAPIError

        mock_supabase, builder = _mock_supabase()
        error = PostgrestAPIError({"message": "not found", "code": "PGRST116"})
        builder.execute = AsyncMock(side_effect=error)

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            result = await FakeEntity.get_by_id(sample_uuid)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_invalid_uuid_raises(self, invalid_uuid):
        with pytest.raises(ValueError) as exc_info:
            await FakeEntity.get_by_id(invalid_uuid)

        assert "Invalid UUID" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_api_error_raises(self, sample_uuid):
        from supabase import PostgrestAPIError

        mock_supabase, builder = _mock_supabase()
        error = PostgrestAPIError({"message": "server error", "code": "PGRST500"})
        builder.execute = AsyncMock(side_effect=error)

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(APIError):
                await FakeEntity.get_by_id(sample_uuid)

    @pytest.mark.asyncio
    async def test_get_by_id_fetches_external_links(self, sample_uuid):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data={"fake_id": sample_uuid, "name": "Test"}))
        mock_links = [ExternalLink(label="Link", url="https://example.com", source_verified=False)]

        with (
            patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch.object(FakeEntity, "_get_external_links", new_callable=AsyncMock) as mock_get_links,
        ):
            mock_get_supabase.return_value = mock_supabase
            mock_get_links.return_value = mock_links

            result = await FakeEntity.get_by_id(sample_uuid)

            assert result.external_links == mock_links
            mock_get_links.assert_awaited_once_with(sample_uuid)


class TestSearch:
    """Tests for CatalogueModel.search."""

    @pytest.mark.asyncio
    async def test_search_success(self):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(
            return_value=MagicMock(
                data=[
                    {"fake_id": "id-1", "name": "Result 1"},
                    {"fake_id": "id-2", "name": "Result 2"},
                ]
            )
        )

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            results = await FakeEntity.search("test query")

            assert len(results) == 2
            assert results[0].id == "id-1"
            assert results[1].name == "Result 2"
            builder.text_search.assert_called_once_with("search_text", "test+query")

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=[]))

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            results = await FakeEntity.search("no matches")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_api_error_raises(self):
        from supabase import PostgrestAPIError

        mock_supabase, builder = _mock_supabase()
        error = PostgrestAPIError({"message": "search failed", "code": "PGRST500"})
        builder.execute = AsyncMock(side_effect=error)

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(APIError):
                await FakeEntity.search("test")


class TestCreate:
    """Tests for CatalogueModel.create."""

    @pytest.mark.asyncio
    async def test_create_success(self, sample_uuid):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=[{"fake_id": sample_uuid}]))
        created_entity = FakeEntity(id=sample_uuid, name="Created")

        with (
            patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch.object(FakeEntity, "get_by_id", new_callable=AsyncMock) as mock_get_by_id,
            patch("music_catalogue.crud.assets.bulk_create_external_links", new_callable=AsyncMock),
        ):
            mock_get_supabase.return_value = mock_supabase
            mock_get_by_id.return_value = created_entity

            data = FakeEntityCreate(name="Created")
            result = await FakeEntity.create(data)

            assert result.id == sample_uuid
            assert result.name == "Created"
            mock_get_by_id.assert_awaited_once_with(sample_uuid)

    @pytest.mark.asyncio
    async def test_create_no_id_returned_raises(self):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=[{}]))

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(APIError) as exc_info:
                await FakeEntity.create(FakeEntityCreate(name="No ID"))

            assert "No ID returned" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_empty_data_raises(self):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=None))

        with patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(APIError) as exc_info:
                await FakeEntity.create(FakeEntityCreate(name="Empty"))

            assert "No ID returned" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_with_external_links(self, sample_uuid):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=[{"fake_id": sample_uuid}]))
        created_entity = FakeEntity(id=sample_uuid, name="With Links")

        with (
            patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch.object(FakeEntity, "get_by_id", new_callable=AsyncMock) as mock_get_by_id,
            patch("music_catalogue.crud.assets.bulk_create_external_links", new_callable=AsyncMock) as mock_bulk_create,
        ):
            mock_get_supabase.return_value = mock_supabase
            mock_get_by_id.return_value = created_entity

            links = [{"label": "Link", "url": "https://example.com"}]
            data = FakeEntityCreate(name="With Links", external_links=links)
            result = await FakeEntity.create(data)

            assert result.id == sample_uuid
            mock_bulk_create.assert_awaited_once_with(links, EntityType.WORK, sample_uuid)

    @pytest.mark.asyncio
    async def test_create_excludes_fields(self, sample_uuid):
        mock_supabase, builder = _mock_supabase()
        builder.execute = AsyncMock(return_value=MagicMock(data=[{"fake_id": sample_uuid}]))

        with (
            patch("music_catalogue.models.base.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch.object(FakeEntity, "get_by_id", new_callable=AsyncMock) as mock_get_by_id,
            patch("music_catalogue.crud.assets.bulk_create_external_links", new_callable=AsyncMock),
        ):
            mock_get_supabase.return_value = mock_supabase
            mock_get_by_id.return_value = FakeEntity(id=sample_uuid, name="Excluded")

            data = FakeEntityCreate(name="Excluded", external_links=["link"])
            await FakeEntity.create(data, exclude={"external_links"})

            insert_call = builder.insert.call_args[0][0]
            assert "external_links" not in insert_call
