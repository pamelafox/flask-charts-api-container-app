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


def send_figure_as_png(fig: Figure) -> Response:
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, download_name="chart.png", mimetype="image/png")


class ImageOutSchema(Schema):
    pass


class BarChartParams(Schema):
    title = String(required=False, validate=Length(0, 30))
    xlabel = String(required=False, validate=Length(0, 30))
    ylabel = String(required=False, validate=Length(0, 30))
    xvalues = DelimitedList(String, required=True)
    yvalues = DelimitedList(Number, required=True)


@app.get("/charts/bar")
@app.input(BarChartParams, location="query")
@app.output(ImageOutSchema, content_type="image/png")
def bar_chart(query_data: dict):
    fig = Figure()
    axes: Axes = fig.add_subplot()
    axes.bar(query_data["xvalues"], query_data["yvalues"])
    axes.set_xlabel(query_data.get("xlabel", ""))
    axes.set_ylabel(query_data.get("ylabel", ""))
    axes.set_title(query_data.get("title", ""))
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
@app.output(ImageOutSchema, content_type="image/png")
def pie_chart(query_data: dict):
    fig = Figure()
    axes: Axes = fig.add_subplot()
    axes.pie(query_data["values"], labels=query_data.get("labels"))
    axes.set_title(query_data.get("title"))
    return send_figure_as_png(fig)
