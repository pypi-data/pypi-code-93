'''
The ledger executor.
Runs ledger-cli to fetch the data.
'''

class LedgerExecutor:
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def run(self, parameters) -> str:
        ''' Execute ledger command '''
        import subprocess
        from cashiersync.config import Configuration

        cfg = Configuration()
        cwd=cfg.ledger_working_dir

        command = f"ledger {parameters}"
        result = subprocess.run(command, shell=True, encoding="utf-8", capture_output=True,
            cwd=cwd)

        # if self.logger:
        #     self.logger.debug(result)

        if result.returncode != 0:
            output = result.stderr
            raise Exception('Ledger error', output)
        else:
            output = result.stdout
        
        #output = self.split_lines(output)

        return output

    def split_lines(self, output):
        rows = output.strip().split('\n')

        for i, item in enumerate(rows):
            rows[i] = rows[i].strip()
        
        return rows
