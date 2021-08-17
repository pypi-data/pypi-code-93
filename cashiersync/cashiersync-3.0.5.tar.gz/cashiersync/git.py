'''
Git-related operations
Potentially destructive, therefore removed from the API.
'''

# @app.route('/repo/pull', methods=['POST'])
# def repo_pull():
#     '''
#     Pull the changes in the repository.
#     Expects { repoPath: ... } parameter in JSON.
#     '''
#     from cashiersync.executor import Executor

#     json = request.get_json()
#     repo_path = json['repoPath']

#     # Execute git pull and return all the console results.
#     try:
#         executor = Executor(logger)
#         output = executor.run("git pull", repo_path)
#     except Exception as e:
#         output = f'Error: {str(e)}'

#     return output

# @app.route('/repo/commit', methods=['POST'])
# def repo_commit():
#     '''
#     Pull the changes in the repository.
#     Expects { repoPath: ... } parameter in JSON.
#     '''
#     from cashiersync.executor import Executor

#     json = request.get_json()
#     repo_path = json['repoPath']
#     message = json['commitMessage']

#     # Execute git pull and return all the console results.
#     try:
#         executor = Executor(logger)

#         # Add all the changes.
#         command = f"git add ."
#         output = executor.run(command, repo_path)

#         # Commit
#         command = f'git commit -m "{message}"'
#         output += executor.run(command, repo_path)
#     except Exception as e:
#         output = f'Error: {str(e)}'

#     return output

# @app.route('/repo/push', methods=['POST'])
# def repo_push():
#     '''
#     Push the changes in the repository.
#     Expects { repoPath: ... } parameter in JSON.
#     '''
#     from cashiersync.executor import Executor

#     json = request.get_json()
#     repo_path = json['repoPath']

#     # Execute git pull and return all the console results.
#     try:
#         executor = Executor(logger)
#         output = executor.run("git push", repo_path)
#     except Exception as e:
#         output = f'Error: {str(e)}'

#     return output

# @app.route('/append', methods=['POST'])
# def append():
#     ''' Append the text to the given (journal) file '''
#     from cashiersync.executor import Executor
#     import os.path

#     json = request.get_json()
#     file_path = json['filePath']
#     content = json['content']

#     # confirm that the file exists
#     if not os.path.isfile(file_path):
#         raise FileNotFoundError()
    
#     # save
#     with open(file_path, 'a') as destination:
#         destination.write(content)

#     return "Content written"

# @app.route('/repo/status')
# def repo_status():
#     from cashiersync.executor import Executor
    
#     repo_path = request.args.get('repoPath')
#     try:
#         executor = Executor(logger)
#         output = executor.run("git status", repo_path)
#     except Exception as e:
#         output = f'Error: {str(e)}'

#     return output
