def flow_selector(flow_name: str):
    if flow_name == "flow_demo":
        from flows.demo import flow_demo
        return flow_demo
