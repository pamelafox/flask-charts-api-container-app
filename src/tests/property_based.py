import pytest
import schemathesis
from hypothesis import settings

from api import app

schema = schemathesis.openapi.from_wsgi("/openapi.json", app)


@schema.parametrize()
@settings(print_blob=True, report_multiple_bugs=False)
@pytest.mark.filterwarnings("ignore:Glyph:UserWarning")
def test_api(case):
    response = schema.transport.send(case, app=app)
    case.validate_response(response)
