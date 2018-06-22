from components.avature import _fetch_req

class CiscoJobsMixin(object):

    def __init__(self, req_id):
        self.text = self.fetch_req(req_id)

    @staticmethod
    def fetch_req(req_id):
        job_text = _fetch_req(req_id)
        return job_text