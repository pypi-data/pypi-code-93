import pandas as pd


def get_total_workflows_weights(
    so_workflows: pd.DataFrame,
    so_states: pd.DataFrame,
    so_state_action_associations: pd.DataFrame,
    so_actions: pd.DataFrame,
) -> pd.DataFrame:
    so_states = so_states.rename(columns={"id": "so_state_id"})
    so_actions = so_actions.rename(columns={"id": "so_action_id"})
    so_state_action_associations = so_state_action_associations.rename(columns={"id": "so_state_action_association_id"})
    so_workflows = pd.merge(so_workflows, so_states, how="left", left_on="id", right_on="so_workflow_id")
    so_workflows = pd.merge(so_workflows, so_state_action_associations, how="left", on="so_state_id")
    so_workflows = pd.merge(so_workflows, so_actions, how="left", on="so_action_id")
    so_workflows = so_workflows.loc[:, ["id", "weight"]].groupby(by="id").sum()
    return so_workflows


def so_workflows_weights(
    so_workflows: pd.DataFrame,
    so_states: pd.DataFrame,
    so_state_action_associations: pd.DataFrame,
    so_actions: pd.DataFrame,
) -> pd.DataFrame:
    so_workflows_weight = get_total_workflows_weights(
        so_workflows=so_workflows,
        so_states=so_states,
        so_state_action_associations=so_state_action_associations,
        so_actions=so_actions,
    )
    so_workflows = pd.merge(so_workflows, so_workflows_weight, on="id", how="left")
    so_workflows_weight = so_workflows.rename(columns={"weight": "total_workflow_weight"})
    return so_workflows_weight.loc[:, ["id", "name", "total_workflow_weight"]]
