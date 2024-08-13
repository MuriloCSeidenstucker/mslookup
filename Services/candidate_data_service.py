import logging

from logger_config import main_logger
from search_in_smerp import SearchInSmerp
from search_in_open_data_anvisa import OpenDataAnvisa

class CandidateDataService:
    def __init__(self, anvisa_search: OpenDataAnvisa, smerp_search: SearchInSmerp):
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.anvisa_search = anvisa_search
        self.smerp_search = smerp_search
    
    def get_registration_data(self, description, laboratory, item):
        self.logger.info(f'Fetching registration data for item: {item}')
        reg_candidates = self.anvisa_search.get_register(description, laboratory)
        if reg_candidates:
            self.logger.info(f'Found {len(reg_candidates)} candidates in ANVISA data\n')
        else:
            self.logger.info('No candidates found in ANVISA data, searching in SMERP')
            reg_candidates = self.smerp_search.get_data_from_smerp(description, laboratory)
            if reg_candidates:
                self.logger.info(f'Found {len(reg_candidates)} candidates in SMERP data\n')
            else:
                self.logger.warning('No candidates found in both ANVISA and SMERP data\n')
        return reg_candidates
    
    def get_candidate_data(self, data):
        candidate_data = []
        for entry in data:
            candidate_data.append({
                'item': entry['item'],
                'description': entry['description'],
                'concentration': entry['concentration'],
                'laboratory': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                'reg_candidates': self.get_registration_data(entry['description'], entry['brand'], entry['item'])
            })
        self.logger.info('Candidate data generation complete\n\n')
        return candidate_data