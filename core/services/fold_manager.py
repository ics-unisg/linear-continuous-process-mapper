

import dash
from dash import html
import dash_bootstrap_components as dbc
import feffery_antd_components as fac


class FoldManager:

    @staticmethod
    def add_fold(existing_folds, fold_activities, fold_name) -> tuple:
    # check that fold name and activities are provided
        if fold_activities == [] or fold_activities is None or fold_name is None or fold_name.strip() == "":
            print("Fold name or activities not provided.")
            return dash.no_update, fac.AntdNotification(
                id="fold-add-error-notification",
                message="Error",
                description="Please select activities and provide a fold name.",
                type="error",
                duration=5,
            ), dash.no_update, dash.no_update
        # check for duplicate fold name
        if existing_folds and any(fold["name"] == fold_name for fold in existing_folds):
            return dash.no_update, fac.AntdNotification(
                id="fold-add-duplicate-notification",
                message="Error",
                description=f"A fold with the name '{fold_name}' already exists. Please choose a different name.",
                type="error",
                duration=5,
            ), dash.no_update, dash.no_update
        # check that no fold already contains any of the selected activities
        if existing_folds:
            for fold in existing_folds:
                if any(act in fold["activities"] for act in fold_activities):
                    print(f"One or more selected activities are already part of an existing fold '{fold['name']}'.")
                    return dash.no_update, fac.AntdNotification(
                        id="fold-add-activity-conflict-notification",
                        message="Error",
                        description=f"One or more selected activities are already part of an existing fold '{fold['name']}'. Please select different activities.",
                        type="error",
                        duration=5,
                    ), dash.no_update, dash.no_update
        folds = list(existing_folds) if existing_folds else []
        folds.append({"name": fold_name, "activities": fold_activities})
        return folds, fac.AntdNotification(
            id="fold-add-success-notification",
            message="Success",
            description=f"Fold '{fold_name}' added successfully.",
            type="success",
            duration=5,
        ), [], ""
    
    @staticmethod
    def on_folding_store_change(folds, initial_activities):
        if not folds:
            all_options = [{"label": act, "value": act} for act in initial_activities]
            return fac.AntdAlert(
                id="no-folds-alert",
                message="No folds defined yet.",
                type="info",
                showIcon=True,
            ), all_options

        table_header = [html.Thead(html.Tr([html.Th("Fold Name"), html.Th("Activities"), html.Th("Delete")]))]
        table_rows = [
            html.Tr([
                html.Td(fold["name"]),
                html.Td(", ".join(fold["activities"])),
                html.Td(fac.AntdButton(id={"type": "delete-fold-button", "index": i}, size="sm", icon=fac.AntdIcon(icon="antd-delete"), danger=True))
            ]) for i, fold in enumerate(folds)]
        table_body = [html.Tbody(table_rows)]

        fold_activities = set(act for fold in folds for act in fold["activities"]) if folds else set()
        dropdown_options = [{"label": act, "value": act} for act in sorted(set(initial_activities) - fold_activities)]

        return dbc.Table(table_header + table_body, bordered=True, hover=True, size="sm"), dropdown_options
    
    @staticmethod
    def delete_fold(n_clicks_list, existing_folds):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        triggered_id = ctx.triggered_id
        if triggered_id is None or not isinstance(triggered_id, dict) or triggered_id.get('type') != 'delete-fold-button':
            return dash.no_update

        fold_index = triggered_id.get('index')
        if existing_folds is not None and fold_index is not None and 0 <= fold_index < len(existing_folds):
            if not any(n_clicks_list):
                return dash.no_update
            print(f"Deleting fold: {existing_folds[fold_index]['name']}")
            new_folds = list(existing_folds)
            new_folds.pop(fold_index)
            return new_folds

        return dash.no_update
    
    @staticmethod
    def update_options_after_fold_change(folds, selected_activities, service):
        if not service:
            return dash.no_update, dash.no_update
        all_activities = set(service.get_all_activities())
        folded_activities = set(act for fold in folds for act in fold["activities"]) if folds else set()
        available_activities = all_activities - folded_activities
        options = [{"label": act, "value": act} for act in sorted(available_activities)]
        fold_names = set(fold["name"] for fold in folds) if folds else set()
        options += [{"label": fold_name, "value": fold_name} for fold_name in fold_names]
        new_selected_activities = [act for act in selected_activities if act in available_activities] if selected_activities else []
        return options, new_selected_activities