import pytest
import schemathesis
from hypothesis import settings

from src.api import app

schema = schemathesis.from_wsgi("/openapi.json", app)


@schema.parametrize()
@settings(print_blob=True, report_multiple_bugs=False)
@pytest.mark.filterwarnings("ignore:Glyph:UserWarning")
def test_api(case):
    response = case.call_wsgi()
    case.validate_response(response)
