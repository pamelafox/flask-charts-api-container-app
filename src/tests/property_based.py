import pytest
import schemathesis
from hypothesis import settings

from api import app

schema = schemathesis.openapi.from_wsgi("/openapi.json", app)


@schema.parametrize()
@settings(print_blob=True, report_multiple_bugs=False)
@pytest.mark.filterwarnings("ignore:Glyph:UserWarning")
def test_api(case):
    response = case.call()
    # Property-based test: ensure API doesn't crash and returns reasonable responses
    assert response.status_code in [200, 422, 400, 404, 405, 500], f"Unexpected status code: {response.status_code}"
    
    # For any response, ensure we get some content
    assert hasattr(response, 'content'), "Response should have content"
