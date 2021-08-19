def asteroidsAfterCollisions(asteroids):
    left_to_right_collision = [0] * len(asteroids)
    max_right_moving_ast = 0

    for i in range(len(asteroids)):
        if asteroids[i] > 0:
            max_right_moving_ast = max(max_right_moving_ast, asteroids[i])
        else:
            left_to_right_collision[i] = 0 if max_right_moving_ast >= abs(asteroids[i]) else asteroids[i]

    right_to_left_collision = [0] * len(asteroids)
    max_left_moving_ast = 0

    for i in range(len(asteroids) - 1, -1, -1):
        if asteroids[i] < 0:
            max_left_moving_ast = max(max_left_moving_ast, abs(asteroids[i])
            else:
                right_to_left_collision[i] = 0 if max_left_moving_ast >= asteroids[i] else asteroids[i]

    return [min(left_to_right_collision[i], right_to_left_collision[i]) for i in range(len(asteroids))]