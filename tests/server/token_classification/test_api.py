from time import sleep

from fastapi.testclient import TestClient
from rubrix.server.commons.models import BulkResponse
from rubrix.server.server import app
from rubrix.server.text_classification.api import TextClassificationRecordsBulk
from rubrix.server.text_classification.model import TextClassificationRecord
from rubrix.server.token_classification.api import TokenClassificationRecordsBulk
from rubrix.server.token_classification.model import (
    SearchResults,
    TokenClassificationRecord,
)

client = TestClient(app)


def test_create_records_for_token_classification():
    dataset = "test_create_records_for_token_classification"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    records = [
        TokenClassificationRecord.parse_obj(data)
        for data in [
            {
                "tokens": "This is a text".split(" "),
                "metadata": {"field_one": "value one", "field_two": "value 2"},
            },
            {
                "tokens": "This is a text".split(" "),
                "metadata": {"field_one": "value one", "field_two": "value 2"},
            },
        ]
    ]
    response = client.post(
        "/api/token-classification/datasets/:bulk-records",
        json=TokenClassificationRecordsBulk(
            name=dataset,
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    bulk_response = BulkResponse.parse_obj(response.json())
    assert bulk_response.dataset == dataset
    assert bulk_response.failed == 0
    assert bulk_response.processed == 2


def test_records_with_default_tokenization():
    dataset = "test_records_with_default_tokenization"
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    records = [
        TextClassificationRecord.parse_obj(data)
        for data in [
            {"text": {"t": "This is a text"}},
        ]
    ]
    response = client.post(
        "/api/classification/datasets/:bulk-records",
        json=TextClassificationRecordsBulk(
            name=dataset,
            records=records,
        ).dict(by_alias=True),
    )

    assert response.status_code == 200, response.json()
    sleep(1)

    response = client.post(
        f"/api/token-classification/datasets/{dataset}/:search", json={}
    )
    results = SearchResults.parse_obj(response.json())
    assert results.total == 1
    for record in results.records:
        assert record.tokens == "This is a text".split(" ")
        assert record.raw_text == "This is a text"
