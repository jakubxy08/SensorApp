import base64
import io
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

# app set up
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

# create html template
app.layout = html.Div([
    html.H1(children='AGHSS: Application for vizualize and analyse data'),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    dcc.Graph(id='Mygraph'),
    html.Div(id='output-data-upload'),
    html.Div([html.Label('Index of sensor'), dcc.Input(id='my-input', value='0', type='text')]),
    html.Div(id='my-output'),
    html.Div([html.Label('Value of "a" parameter'), dcc.Input(id='my-input2', value='1', type='text')]),
    html.Div(id='my-output2'),
    html.Div([html.Label('Value of "b" parameter'), dcc.Input(id='my-input3', value='1', type='text')]),
    html.Div(id='my-output3')
])


@app.callback(
    Output(component_id='my-output', component_property='children'),
    [Input(component_id='my-input', component_property='value')]
)
def update_output_div(input_value):
    return 'Output: {}'.format(input_value)


# parse data from file
def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


# Avoid blank input error
def integ(x):
    if len(x) == 0:
        return 0
    else:
        return int(x)


# Update graph chart from chosen values
@app.callback(Output('Mygraph', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input(component_id='my-input', component_property='value'),
                Input(component_id='my-input2', component_property='value'),
                Input(component_id='my-input3', component_property='value')
            ])
def update_graph(contents, filename, input_value, input_value2, input_value3):
    fig = go.Figure()
    val = 0
    a = 1
    b = 1
    # check & convert string value to int
    if(input_value is not None):
        if (isinstance(input_value, int)):
            val = input_value
        else:
            val = integ(input_value)

    if (input_value2 is not None):
        if (isinstance(input_value2, int)):
            a = input_value2
        else:
            a = integ(input_value2)

    if (input_value3 is not None):
        if (isinstance(input_value3, int)):
            b = input_value3
        else:
            b = integ(input_value3)

    # Processing data
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df2 = df.copy()
        dfx1 = df2.loc[df2['Index'] == val]
        dfx1.loc[:, 'Value'] = dfx1.loc[:, 'Value'] * a + b

        fig = go.Figure(data=go.Scatter(
            x=dfx1['Timestep'],
            y=dfx1['Value'],
            mode='markers'
        ))

    return fig


# Update table with sensors
@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()

    if contents:
        contents = contents[1]
        filename = filename[1]
        df = parse_data(contents, filename)

        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),
            html.Hr()
        ])

    return table


if __name__ == '__main__':
    app.run_server(debug=True)
