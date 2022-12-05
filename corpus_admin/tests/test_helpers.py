import pytest

from corpus_admin.helpers import get_corpus_info
from elasticsearch import exceptions as es_exceptions

TEST_INDEX_NAME = "test-index"
ELASTIC_URL = "http://test-url:9200/"

TEST_DOC_INFO = {
    "name": "My document name",
    "file": "doc.pdf",
    "id": "doc-id-1",
}


BUCKETS_RESPONSE = [
    {"doc_count": 10, "key": "doc-id-1"}, 
    {"doc_count": 10, "key": "doc-id-2"}, 
]

INDEX_AGG_RESPONSE = {
    "aggregations": {
        "ids": {
            "buckets": BUCKETS_RESPONSE,
        }
    }
}

@pytest.fixture
def mock_elasticsearch_corpus_info(mocker):
    return mocker.patch("elasticsearch.Elasticsearch.search", return_value=INDEX_AGG_RESPONSE)


@pytest.fixture
def mock_elasticsearch_corpus_info_connection_exception(mocker):
    return mocker.patch("elasticsearch.Elasticsearch.search", side_effect=es_exceptions.ConnectionError)


@pytest.fixture
def mock_django_messages_info(mocker):
    return mocker.patch("corpus_admin.helpers.messages.info", return_value=None)


@pytest.fixture
def mock_django_messages_warning(mocker):
    return mocker.patch("corpus_admin.helpers.messages.warning", return_value=None)


@pytest.fixture
def mock_django_messages_error(mocker):
    return mocker.patch("corpus_admin.helpers.messages.error", return_value=None)


@pytest.fixture
def mock_get_document_info(mocker):
    return mocker.patch("corpus_admin.helpers.get_document_info", return_value=TEST_DOC_INFO)


@pytest.fixture
def mock_index_name(mocker):
    return mocker.patch("corpus_admin.helpers.settings.INDEX", TEST_INDEX_NAME)


@pytest.fixture
def mock_elasticsearch_url(mocker):
    return mocker.patch("corpus_admin.helpers.settings.ELASTIC_URL", ELASTIC_URL)


def test_get_corpus_info_ok(
        mock_elasticsearch_corpus_info,
        mock_get_document_info,
        mock_index_name,
        caplog):
    doc_info_response = {
        "name": "My document name",
        "file": "doc.pdf",
        "id": "doc-id-1",
        "count": 10,
    }
    total, docs = get_corpus_info(request={"data": "something"})
    assert mock_elasticsearch_corpus_info.call_count == 1
    assert mock_get_document_info.call_count == 2
    assert total == 20
    assert len(docs) == 2
    assert docs[0] == doc_info_response
    assert f"Documentos actuales::{len(BUCKETS_RESPONSE)}" in caplog.text


def test_get_corpus_info_connection_exception(
        mock_elasticsearch_corpus_info_connection_exception,
        mock_get_document_info,
        mock_django_messages_info,
        mock_django_messages_error,
        mock_index_name,
        mock_elasticsearch_url,
        caplog):
    total, docs = get_corpus_info(request={"data": "something"})
    assert mock_elasticsearch_corpus_info_connection_exception.call_count == 1
    assert mock_get_document_info.call_count == 0
    assert total == 0
    assert docs == []
    assert f"Connection error to elasticsearch index::{TEST_INDEX_NAME} URL::{ELASTIC_URL}" in caplog.text 
    mock_django_messages_error.assert_called_once_with(
        # Request
        {"data": "something"},
        # Message
        f"No se pudo conectar al índice: <i>{TEST_INDEX_NAME}</i>"
    )
    mock_django_messages_info.assert_called_once_with(
        {"data": "something"},
        "TIP: ¿Está corriendo la instancia de Elasticsearch? ¿Existe el \
        índice?"
    )
    
