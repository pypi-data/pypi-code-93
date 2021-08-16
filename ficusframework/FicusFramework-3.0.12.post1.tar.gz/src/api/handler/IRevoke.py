from abc import abstractmethod


class IRevoke:

    @abstractmethod
    def revoke_handler(self, actor_code, actor_handler, code, project, site, log_id, job_id, message_id, is_expire):
        pass
