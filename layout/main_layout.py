from dash import dcc, html
import dash_bootstrap_components as dbc
import feffery_antd_components as fac


def create_layout():
    return dbc.Container(
        [
            html.H1("Linear Continuous Process Mapper", className="my-4 text-center"),
            dcc.Store(id="log-store"),
            dcc.Store(id="folding-store"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H4("Controls", className="mb-0")),
                                    dbc.CardBody(
                                        [
                                            html.H5("Select Activities", className="mt-3"),
                                            dbc.Checklist(
                                                id="activity-checklist",
                                                options=[],
                                                value=[],
                                                className="mb-4",
                                            ),
                                            fac.AntdButton(
                                                "Activity Folding",
                                                id="activity-folding-button",
                                                color="primary",
                                                variant="outlined",
                                                className="mb-3",
                                                style={"width": "100%"},
                                            ),
                                            fac.AntdModal(
                                                id="activity-folding-modal",
                                                title="Fold Activities",
                                                children=[
                                                    html.Div(id='existing-folds-table'),
                                                    html.Hr(),
                                                    fac.AntdForm([
                                                        fac.AntdFormItem(
                                                            label="Activities to fold",
                                                            children=[
                                                                fac.AntdSelect(
                                                                    id="fold-activities-dropdown",
                                                                    options=[],
                                                                    mode="multiple",
                                                                    placeholder="Select activities to fold",
                                                                    style={"width": "100%"},
                                                                )
                                                            ],
                                                            required=True,
                                                        ),
                                                        fac.AntdFormItem(
                                                            label="Fold name",
                                                            children=[
                                                                fac.AntdInput(
                                                                    id="fold-name-input",
                                                                    placeholder="Enter fold name",
                                                                    style={"width": "100%"},
                                                                )
                                                            ],
                                                            required=True,
                                                        ),
                                                        dbc.Button(
                                                            "Add Fold",
                                                            id="add-fold-button",
                                                            color="secondary",
                                                            className="mt-2",
                                                            style={"width": "100%"},
                                                        ),

                                                    ])
                                                ]
                                            ),
                                            html.Div(id='notification-empty-fold'),
                                            html.Hr(),
                                            html.H5("Select Generic Map", className="mt-3"),
                                            dcc.Dropdown(
                                                id="builder-dropdown",
                                                options=[
                                                    {"label": "Set-Based", "value": "set_based"},
                                                    {"label": "Sequence-Based", "value": "sequence_based"},
                                                    {"label": "Last-Activity-Based", "value": "last_activity_based"},
                                                ],
                                                value="set_based",
                                                className="mb-3",
                                                clearable=False,
                                            ),
                                            dbc.Checklist(
                                                id="allow-loops-checkbox",
                                                options=[{"label": "Allow Self-Loops", "value": "enabled"}],
                                                value=["enabled"],
                                                className="mb-2",
                                                switch=True,
                                            ),
                                            dbc.Checklist(
                                                id="visualize-empty-traces-checkbox",
                                                options=[{"label": "Visualize Empty Traces", "value": "enabled"}],
                                                value=["enabled"],
                                                className="mb-3",
                                                switch=True,
                                            ),
                                            dbc.Accordion(
                                                [
                                                    dbc.AccordionItem(
                                                        title="Advanced/Dev Options",
                                                        children=[
                                                            html.Label("Visualization Simplification", className="fw-bold"),
                                                            dbc.Checklist(
                                                                id="simplify-viz-checkbox",
                                                                options=[{"label": "Enable Simplification", "value": "enabled"}],
                                                                value=[],
                                                                className="mb-2",
                                                                switch=True,
                                                            ),
                                                            html.Div(
                                                                id="threshold-container",
                                                                children=[
                                                                    html.Label("Minimum Weight Threshold:"),
                                                                    dbc.Input(
                                                                        id="minimum-weight-threshold-input",
                                                                        type="number",
                                                                        placeholder="Enter weight limit...",
                                                                        disabled=True,
                                                                        min=1,
                                                                    ),
                                                                ],
                                                                style={"display": "none"},
                                                            ),
                                                            html.Label("Metrics", className="fw-bold mt-3"),
                                                            dbc.Checklist(
                                                                id="show-metrics-checkbox",
                                                                options=[{"label": "Show Sankey graph metrics", "value": "enabled"}],
                                                                value=[],
                                                                className="mb-2",
                                                                switch=True,
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    )
                                                ],
                                                start_collapsed=True,
                                            ),
                                            dbc.Button(
                                                "Refresh Visualization",
                                                id="refr-vis-but",
                                                color="primary",
                                                className="w-100 mt-4",
                                                disabled=True,
                                            ),
                                        ]
                                    ),
                                ],
                                className="shadow-sm",
                            )
                        ],
                        xs=12,
                        lg=12,
                        xl=3,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        dcc.Loading(
                                            id="loading-sankey",
                                            type="circle",
                                            children=dcc.Graph(id="sankey-graph", style={"height": "85vh"}),
                                        )
                                    ]
                                ),
                                className="shadow-sm",
                            ),
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Sankey Graph Metrics", className="mb-0")),
                                    dbc.CardBody(
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dcc.Loading(
                                                        id="loading-pie-chart",
                                                        type="circle",
                                                        children=dcc.Graph(id="pie-chart")
                                                    ),
                                                    md=6
                                                ),
                                                dbc.Col(
                                                    dcc.Loading(
                                                        id="loading-metadata",
                                                        type="circle",
                                                        children=html.Div(id="metadata-table", className="mt-4")
                                                    ),
                                                    md=6
                                                ),
                                            ]
                                        )
                                    ),
                                ],
                                id="metrics-container",
                                className="shadow-sm mt-4",
                                style={"display": "none"},
                            ),
                        ],
                        xs=12,
                        lg=12,
                        xl=9,
                    ),
                ]
            ),
        ],
        fluid=True,
        className="p-4"
    )
