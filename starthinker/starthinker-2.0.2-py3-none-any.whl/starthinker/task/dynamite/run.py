from starthinker.util.dynamite import dynamite_write

def dynamite(config, task):
  if config.verbose:
    print('DYNAMITE')

  dynamite_write(
    config,
    task['room'],
    task['key'],
    task['token'],
    task['message']
  )
