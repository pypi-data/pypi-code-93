META = {
    "models": {
        "QMarketModel": {
            "public": True,
            "params": ["agent_bus_map", "u_max", "u_min"],
            "attrs": [
                "grid_state",  # in
                "q_offers",  # in
                "q_accept",  # out
            ],
        },
    },
}