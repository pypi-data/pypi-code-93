def load_multiple_ecs_tasks(config, operator):
    """
    Designed to load an nth amount of ECS tasks in a single dag
    based on the configuration that hosts multiple verticals:
        <vertical name>>:
          solution: ''
          tags:
            - Key: 'developer'
              Value: ''
          ecs:
            task_cluster: ''
            security_groups:
              - ''
            subnets:
              - ''
            task_definition_names:
              - <here is where all tasks are loaded as a list>
    """
    for task_defintiton_name in config['ecs']['task_definition_names']:
        yield operator(
            task_id=f"run_ecs_task_{task_defintiton_name}",
            config={
                'task_definition_name': task_defintiton_name,
                'task_cluster': config['ecs']['task_cluster'],
                'security_groups': config['ecs']['security_groups'],
                'subnets': config['ecs']['subnets']
            }
        )
