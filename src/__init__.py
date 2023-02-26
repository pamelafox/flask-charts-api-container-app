from io import BytesIO

from flask import send_file
from apiflask import APIFlask, Schema
from apiflask.fields import Number, String, DelimitedList
from apiflask.validators import Length

from matplotlib.figure import Figure
from matplotlib.axes import Axes

app = APIFlask(__name__, docs_path=None)
# Default browser cache to 5 minutes
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300


class BarChartParams(Schema):
    title = String(required=False, validate=Length(0, 30), load_default="Bar chart")
    xlabel = String(required=False, validate=Length(0, 30), load_default="Categories")
    ylabel = String(required=False, validate=Length(0, 30), load_default="Values")
    xvalues = DelimitedList(String, required=True)
    yvalues = DelimitedList(Number, required=True)


@app.get("/bar_chart")
@app.input(BarChartParams, location="query")
def bar_chart(data):
    print(data)
    # Generate the figure **without using pyplot**.
    fig = Figure()
    axes: Axes = fig.subplots(squeeze=False)[0][0]
    axes.bar(data["xvalues"], data["yvalues"])
    axes.set_xlabel(data["xlabel"])
    axes.set_ylabel(data["ylabel"])
    axes.set_title(data["title"])
    axes.set_ylim(bottom=0)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, download_name="chart.png", mimetype="image/png")
