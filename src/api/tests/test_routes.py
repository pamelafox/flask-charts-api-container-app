import io
import math

import PIL
from src.api import app

client = app.test_client()


def assert_image_equal(response_data, baseline_filename):
    image1 = PIL.Image.open(io.BytesIO(response_data))
    image2 = PIL.Image.open(f"src/api/tests/saved_images/{baseline_filename}")
    assert image1.size == image2.size
    assert image1.mode == image2.mode
    # Based on https://stackoverflow.com/a/55251080/1347623
    diff = PIL.ImageChops.difference(image1, image2).histogram()
    sq = (value * (i % 256) ** 2 for i, value in enumerate(diff))
    rms = math.sqrt(sum(sq) / float(image1.size[0] * image1.size[1]))
    assert rms < 90


def test_bar_chart_required_only():
    response = client.get(
        "/charts/bar",
        query_string={
            "xvalues": "a,b,c",
            "yvalues": "1,2,3",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"
    assert_image_equal(response.data, "bar_chart_required_only.png")


def test_bar_chart_all_specified():
    response = client.get(
        "/charts/bar",
        query_string={
            "xvalues": "a,b,c",
            "yvalues": "1,2,3",
            "title": "My Chart",
            "xlabel": "X Axis",
            "ylabel": "Y Axis",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"
    assert_image_equal(response.data, "bar_chart_all_specified.png")


def test_pie_chart_required_only():
    response = client.get(
        "/charts/pie",
        query_string={
            "values": "1,2,3",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"
    assert_image_equal(response.data, "pie_chart_required_only.png")


def test_pie_chart_all_params():
    response = client.get(
        "/charts/pie",
        query_string={
            "values": "1,2,3",
            "labels": "a,b,c",
            "title": "My Chart",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"
    assert_image_equal(response.data, "pie_chart_all_params.png")


def test_pie_chart_invalid_labels():
    response = client.get(
        "/charts/pie",
        query_string={
            "values": "1,2,3",
            "labels": "a,b",
            "title": "My Chart",
        },
    )
    assert response.status_code == 422
    assert response.json["detail"]["query"]["_schema"][0] == "Labels must be specified for each value"


def test_pie_chart_invalid_value():
    response = client.get(
        "/charts/pie",
        query_string={"values": "0.0"},
    )
    assert response.status_code == 422
    assert response.json["detail"]["query"]["_schema"][0] == "Cannot create a pie chart with single value of 0"


def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "image/png" in response.json["paths"]["/charts/bar"]["get"]["responses"]["200"]["content"]
    assert "image/png" in response.json["paths"]["/charts/pie"]["get"]["responses"]["200"]["content"]
