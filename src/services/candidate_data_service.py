import logging

from typing import List, Dict, Any

from src.logger_config import main_logger
from src.search_in_smerp import SearchInSmerp
from src.search_in_open_data_anvisa import OpenDataAnvisa

class CandidateDataService:
    def __init__(self, anvisa_search: OpenDataAnvisa, smerp_search: SearchInSmerp, checkpoint_manager):
        self.logger = logging.getLogger(f'main_logger.{self.__class__.__name__}')
        self.anvisa_search = anvisa_search
        self.smerp_search = smerp_search
        
        self.checkpoint_manager = checkpoint_manager
        self.checkpoint_interval = 10
    
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
    
    def get_candidate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidate_data = []
        
        current_identifier = self.checkpoint_manager.generate_identifier(data)
        checkpoint, saved_identifier = self.checkpoint_manager.load_checkpoint(stage='candidate_service')
        if saved_identifier == current_identifier:
            candidate_data.extend(checkpoint['data'])
            start_index = len(candidate_data)
        else:
            start_index = 0
        
        for index, entry in enumerate(data[start_index:], start=start_index):
            candidate_data.append({
                'item': entry['item'],
                'origin_description': entry['origin_description'],
                'description': entry['description'],
                'concentration': entry['concentration'],
                'laboratory': entry['brand'] if isinstance(entry['brand'], str) else entry['brand']['Name'],
                'reg_candidates': self.get_registration_data(entry['description'], entry['brand'], entry['item'])
            })
                                    
            if len(candidate_data) % self.checkpoint_interval == 0:
                self.checkpoint_manager.save_checkpoint(candidate_data, 'candidate_service', current_identifier)
            
        self.checkpoint_manager.save_checkpoint(candidate_data, 'candidate_service', current_identifier)
        
        self.logger.info('Candidate data generation complete\n\n')
        return candidate_data