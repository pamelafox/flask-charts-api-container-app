from io import BytesIO

from apiflask import APIFlask, Schema
from apiflask.fields import DelimitedList, Number, String
from apiflask.validators import Length, Range
from flask import Response, send_file
from marshmallow import ValidationError, validates_schema
from matplotlib.axes import Axes
from matplotlib.figure import Figure

app = APIFlask(__name__, docs_path=None)
# Default browser cache to 5 minutes
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300


# Needed due to https://github.com/apiflask/apiflask/issues/357
@app.spec_processor
def update_spec(spec):
    for path in spec["paths"]:
        spec["paths"][path]["get"]["responses"]["200"]["content"] = {
            "image/png": {
                "schema": {
                    "type": "string",
                }
            }
        }
    return spec


def send_figure_as_png(fig: Figure) -> Response:
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, download_name="chart.png", mimetype="image/png")


class BarChartParams(Schema):
    title = String(required=False, validate=Length(0, 30))
    xlabel = String(required=False, validate=Length(0, 30))
    ylabel = String(required=False, validate=Length(0, 30))
    xvalues = DelimitedList(String, required=True)
    yvalues = DelimitedList(Number, required=True)


@app.get("/charts/bar")
@app.input(BarChartParams, location="query")
def bar_chart(data: dict):
    fig = Figure()
    axes: Axes = fig.subplots(squeeze=False)[0][0]
    axes.bar(data["xvalues"], data["yvalues"])
    axes.set_xlabel(data.get("xlabel", ""))
    axes.set_ylabel(data.get("ylabel", ""))
    axes.set_title(data.get("title", ""))
    axes.set_ylim(bottom=0)
    return send_figure_as_png(fig)


class PieChartParams(Schema):
    title = String(required=False, validate=Length(0, 30))
    values = DelimitedList(Number(validate=Range(min=0, max=3.4028235e38)), required=True)
    labels = DelimitedList(String)

    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if "labels" in data and len(data["labels"]) != len(data["values"]):
            raise ValidationError("Labels must be specified for each value")
        if len(data["values"]) == 1 and data["values"][0] == 0:
            raise ValidationError("Cannot create a pie chart with single value of 0")


@app.get("/charts/pie")
@app.input(PieChartParams, location="query")
def pie_chart(data: dict):
    fig = Figure()
    axes: Axes = fig.subplots(squeeze=False)[0][0]
    axes.pie(data["values"], labels=data.get("labels"))
    axes.set_title(data.get("title"))
    return send_figure_as_png(fig)
