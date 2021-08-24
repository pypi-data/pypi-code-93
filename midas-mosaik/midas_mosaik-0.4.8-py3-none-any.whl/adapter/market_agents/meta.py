META = {
    "api_version": "2.4",
    "models": {
        "MarketAgentModel": {
            "public": True,
            "params": ["eid", "unit_type", "s_max", "start_date", "step_size"],
            "attrs": [
                "schedule",
                "reactive_power_offer",
                "q_set_minutes_15_to_30",
                "set_q_schedule",
            ],
        },
    },
}