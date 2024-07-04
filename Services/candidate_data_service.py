class CandidateDataService:
    def __init__(self, anvisa_search, smerp_search):
        self.anvisa_search = anvisa_search
        self.smerp_search = smerp_search
    
    def get_registration_data(self, description, laboratory):
        reg_candidates = self.anvisa_search.get_register(description, laboratory)
        if not reg_candidates:
            reg_candidates = self.smerp_search.get_data_from_smerp(description, laboratory)
        return reg_candidates
    
    def get_candidate_data(self, data):
        candidate_data = []
        for entry in data:
            if entry['item'] == 26:
                pass
            candidate_data.append({
                'item': entry['item'],
                'description': entry['description'],
                'concentration': entry['concentration'],
                'laboratory': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                'reg_candidates': self.get_registration_data(entry['description'], entry['brand'])
            })
        return candidate_data