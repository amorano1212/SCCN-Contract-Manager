import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ContractManager:
    def __init__(self):
        self.contracts: Dict[str, dict] = {}
        self.cleanup_expired_contracts()
    
    def create_contract(
        self,
        user_id: int,
        commodities: List[str],
        quantities: List[int],
        destination: str,
        primary_port: bool,
        days_left: Optional[int],
        quote_data: dict
    ) -> str:
        """Create a new contract and return contract ID"""
        contract_id = str(uuid.uuid4())[:8].upper()
        
        contract = {
            'contract_id': contract_id,
            'user_id': user_id,
            'commodities': commodities,
            'quantities': quantities,
            'destination': destination,
            'primary_port': primary_port,
            'days_left': days_left,
            'quote_data': quote_data,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'accepted_at': None,
            'completed_at': None
        }
        
        self.contracts[contract_id] = contract
        logger.info(f"Created contract {contract_id} for user {user_id}")
        
        return contract_id
    
    def get_contract(self, contract_id: str) -> Optional[dict]:
        """Get contract by ID"""
        self.cleanup_expired_contracts()
        return self.contracts.get(contract_id)
    
    def accept_contract(self, contract_id: str) -> bool:
        """Accept a contract"""
        contract = self.contracts.get(contract_id)
        if not contract or contract['status'] != 'pending':
            return False
        
        contract['status'] = 'accepted'
        contract['accepted_at'] = datetime.now().isoformat()
        
        logger.info(f"Contract {contract_id} accepted")
        return True
    
    def get_user_contracts(self, user_id: int) -> List[dict]:
        """Get all contracts for a user"""
        self.cleanup_expired_contracts()
        
        user_contracts = []
        for contract in self.contracts.values():
            if contract['user_id'] == user_id:
                user_contracts.append(contract)
        
        # Sort by creation date, newest first
        user_contracts.sort(
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        return user_contracts
    
    def update_contract_status(self, contract_id: str, status: str) -> bool:
        """Update contract status"""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False
        
        contract['status'] = status
        if status == 'delivered':
            contract['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"Contract {contract_id} status updated to {status}")
        return True
    
    def update_contract_thread(self, contract_id: str, thread_id: int) -> bool:
        """Update contract with thread ID"""
        if contract_id in self.contracts:
            self.contracts[contract_id]['thread_id'] = thread_id
            return True
        return False
    
    def cleanup_expired_contracts(self):
        """Remove expired pending contracts"""
        current_time = datetime.now()
        expired_contracts = []
        
        for contract_id, contract in self.contracts.items():
            if contract['status'] == 'pending':
                expires_at = datetime.fromisoformat(contract['expires_at'])
                if current_time > expires_at:
                    expired_contracts.append(contract_id)
        
        for contract_id in expired_contracts:
            del self.contracts[contract_id]
            logger.info(f"Removed expired contract {contract_id}")
    
    def get_contract_statistics(self) -> dict:
        """Get contract statistics"""
        stats = {
            'total_contracts': len(self.contracts),
            'pending': 0,
            'accepted': 0,
            'in_progress': 0,
            'delivered': 0,
            'cancelled': 0
        }
        
        for contract in self.contracts.values():
            status = contract['status']
            if status in stats:
                stats[status] += 1
        
        return stats
