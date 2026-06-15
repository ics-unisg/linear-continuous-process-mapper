import dash
from dash import Input, Output, State
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from layout.main_layout import create_layout
from app.factory import create_process_analytics_service
from core.services.fold_manager import FoldManager
from core.constants import ACTIVITY_COL



def create_app(event_log):
    # Initial Setup
    try:

        service = create_process_analytics_service(event_log)
        initial_activities = service.get_all_activities()

    except Exception as e:
        print(f"Error during initial setup: {e}")
        service = None
        initial_activities = []

    # Dash App Initialization
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = create_layout()


    # Callbacks
    @app.callback(
        Output("activity-checklist", "options"),
        Output("activity-checklist", "value"),
        Output("fold-activities-dropdown", "options"),
        Input("log-store", "data"),
    )
    def populate_controls(_):
        """Populates the activity checklist when the app loads."""
        if not service:
            return [], [], []
        options = [{"label": act, "value": act} for act in initial_activities]
        return options, [], options


    @app.callback(
        Output("threshold-container", "style"),
        Input("simplify-viz-checkbox", "value"),
    )
    def toggle_threshold_input(simplify_enabled):
        """Toggles the visibility of the threshold input based on the checkbox state."""
        if "enabled" in simplify_enabled:
            return {"display": "block"}
        return {"display": "none"}


    @app.callback(
        Output("minimum-weight-threshold-input", "disabled"),
        Input("simplify-viz-checkbox", "value"),
    )
    def toggle_threshold_input_state(simplify_enabled):
        """Enables or disables the threshold input based on the checkbox state."""
        if "enabled" in simplify_enabled:
            return False  # False means enabled
        return True  # True means disabled


    @app.callback(
        Output("refr-vis-but", "disabled"),
        Input("activity-checklist", "value"),
        Input("builder-dropdown", "value"),
        Input("allow-loops-checkbox", "value"),
        Input("visualize-empty-traces-checkbox", "value"),
        Input("simplify-viz-checkbox", "value"),
        Input("minimum-weight-threshold-input", "value"),
        Input("refr-vis-but", "n_clicks"),
        prevent_initial_call=True
    )
    def update_button_state(
        selected_activities,
        builder_key,
        allow_loops_enabled,
        visualize_empty_cases_enabled,
        simplify_enabled,
        merge_threshold_val,
        n_clicks,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return True

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'refr-vis-but':
            return True
        
        return False


    @app.callback(
        Output("metrics-container", "style"),
        Input("show-metrics-checkbox", "value"),
    )
    def toggle_metrics_container(show_metrics_enabled):
        """Toggles the visibility of the metrics container."""
        if "enabled" in show_metrics_enabled:
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        Output("sankey-graph", "figure"),
        Output("pie-chart", "figure"),
        Output("metadata-table", "children"),
        Input('refr-vis-but', 'n_clicks'),
        State("activity-checklist", "value"),
        State("builder-dropdown", "value"),
        State("allow-loops-checkbox", "value"),
        State("simplify-viz-checkbox", "value"),
        State("minimum-weight-threshold-input", "value"),
        State("visualize-empty-traces-checkbox", "value"),
        State("folding-store", "data")
    )
    def update_sankey_visualization(
        _,
        selected_activities,
        builder_key,
        allow_loops_enabled,
        simplify_enabled,
        merge_threshold_val,
        visualize_empty_cases_value,
        folds
    ):
        """
        Main callback. Generates the Sankey figure based on user selections and updates the associated metrics elements.
        """
        if not service or not selected_activities:
            return go.Figure(layout={"title": "Please select activities to visualize."}), go.Figure(), None
        
        # generate alternative service based on folding
        if folds:
            # rename fold activities to fold names in event log
            folded_event_log = event_log.copy()
            for fold in folds:
                fold_name = fold["name"]
                mapping = {act: fold_name for act in fold["activities"]}
                folded_event_log[ACTIVITY_COL] = folded_event_log[ACTIVITY_COL].replace(mapping)
            rel_service = create_process_analytics_service(folded_event_log)
        else:
            rel_service = service


        merge_threshold = None
        if (
            "enabled" in simplify_enabled
            and merge_threshold_val is not None
            and merge_threshold_val != ""
        ):
            try:
                merge_threshold = int(merge_threshold_val)
            except (ValueError, TypeError):
                # Pass None if the input is not a valid number
                merge_threshold = None

        allow_loops = "enabled" in allow_loops_enabled
        
        visualize_empty_cases_enabled = "enabled" in visualize_empty_cases_value

        fig, metadata = rel_service.generate_sankey_figure(
            selected_activities=selected_activities,
            builder_key=builder_key,
            merge_threshold=merge_threshold,
            allow_loops=allow_loops,
            visualize_empty_cases=visualize_empty_cases_enabled,
        )

        return (fig,
                rel_service.generate_metadata_chart(metadata, visualize_empty_cases_enabled),
                rel_service.generate_metadata_table(metadata))


    @app.callback(
        Output('activity-folding-modal', 'visible'),
        Input('activity-folding-button', 'nClicks'),
        prevent_initial_call=True,
    )
    def modal_act_fold(nClicks):
        return True


    @app.callback(
        Output('folding-store', 'data'),
        Output('notification-empty-fold', 'children'),
        Output('fold-activities-dropdown', 'value'),
        Output('fold-name-input', 'value'),
        Input('add-fold-button', 'n_clicks'),
        State('folding-store', 'data'),
        State('fold-activities-dropdown', 'value'),
        State('fold-name-input', 'value'),
        prevent_initial_call=True,
    )
    def add_fold(_, existing_folds, fold_activities, fold_name):
        return FoldManager.add_fold(existing_folds, fold_activities, fold_name)


    @app.callback(
        Output('existing-folds-table', 'children'),
        Output("fold-activities-dropdown", "options", allow_duplicate=True),
        Input('folding-store', 'data'),
        prevent_initial_call=True,
    )
    def on_folding_store_change(folds):
        return FoldManager.on_folding_store_change(folds, initial_activities)

    @app.callback(
        Output('folding-store', 'data', allow_duplicate=True),
        Input({'type': 'delete-fold-button', 'index': dash.ALL}, 'nClicks'),
        State('folding-store', 'data'),
        prevent_initial_call=True,
    )
    def delete_fold(n_clicks_list, existing_folds):
        return FoldManager.delete_fold(n_clicks_list, existing_folds)

    @app.callback(
        Output("activity-checklist", "options", allow_duplicate=True),
        Output("activity-checklist", "value", allow_duplicate=True),
        Input('folding-store', 'data'),
        State("activity-checklist", "value"),
        prevent_initial_call=True,
    )
    def update_options_after_fold_change(folds, selected_activities):
        return FoldManager.update_options_after_fold_change(folds, selected_activities, service)
    
    return app

