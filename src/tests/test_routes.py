from src import app

client = app.test_client()


def test_bar_chart_required_only():
    response = client.get(
        "/bar_chart",
        query_string={
            "xvalues": "a,b,c",
            "yvalues": "1,2,3",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"


def test_bar_chart_all_specified():
    response = client.get(
        "/bar_chart",
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


def test_pie_chart_required_only():
    response = client.get(
        "/pie_chart",
        query_string={
            "values": "1,2,3",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"


def test_pie_chart_all_params():
    response = client.get(
        "/pie_chart",
        query_string={
            "values": "1,2,3",
            "labels": "a,b,c",
            "title": "My Chart",
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Disposition"] == "inline; filename=chart.png"


def test_pie_chart_invalid_labels():
    response = client.get(
        "/pie_chart",
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
        "/pie_chart",
        query_string={"values": "0.0"},
    )
    assert response.status_code == 422
    assert response.json["detail"]["query"]["_schema"][0] == "Cannot create a pie chart with single value of 0"


def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "image/png" in response.json["paths"]["/bar_chart"]["get"]["responses"]["200"]["content"]
    assert "image/png" in response.json["paths"]["/pie_chart"]["get"]["responses"]["200"]["content"]
