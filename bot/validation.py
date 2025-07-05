import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SystemValidator:
    def __init__(self):
        self.systems = self.load_systems()
    
    def load_systems(self) -> Dict[str, Any]:
        """Load system data from JSON file"""
        try:
            with open('data/systems.json', 'r') as f:
                data = json.load(f)
                return {system['name']: system for system in data['systems']}
        except FileNotFoundError:
            logger.warning("Systems data file not found, using default systems")
            return self.get_default_systems()
    
    def get_default_systems(self) -> Dict[str, Any]:
        """Default systems if data file is not available"""
        default_systems = [
            'Sol', 'Alpha Centauri', 'Barnard\'s Star', 'Wolf 359', 'Lalande 21185',
            'Sirius', 'Ross 154', 'Epsilon Eridani', 'Lacaille 9352', 'Ross 128',
            'EZ Aquarii', 'Procyon', 'Luyten 726-8', 'Tau Ceti', 'Epsilon Indi',
            'Colonia', 'Sagittarius A*', 'Beagle Point', 'Shinrarta Dezhra',
            'LHS 3447', 'Eravate', 'Matet', 'Kremainn', 'Beta Hydri', 'Wolf 397',
            'LTT 15574', 'Hutton Orbital', 'Farseer Inc', 'Deciat', 'Maia',
            'Merope', 'Electra', 'Asterope', 'Taygeta', 'Celaeno', 'Atlas',
            'Pleione', 'HIP 22460', 'Witch Head Nebula', 'California Nebula',
            'Heart Nebula', 'Soul Nebula', 'Rosette Nebula', 'Eagle Nebula',
            'Horsehead Nebula', 'Orion Nebula', 'Flame Nebula', 'Bubble Nebula'
        ]
        
        return {name: {'name': name, 'type': 'system'} for name in default_systems}
    
    def is_valid_system(self, system_name: str) -> bool:
        """Check if a system name is valid"""
        if not system_name or not isinstance(system_name, str):
            return False
        
        # Accept any non-empty string as a valid system name
        # This allows users to specify any system without restriction
        return len(system_name.strip()) > 0
    
    def get_system_suggestions(self, partial_name: str, limit: int = 5) -> List[str]:
        """Get system name suggestions based on partial input"""
        if not partial_name:
            return []
        
        suggestions = []
        partial_lower = partial_name.lower()
        
        # Exact matches first
        for system in self.systems:
            if system.lower().startswith(partial_lower):
                suggestions.append(system)
        
        # Partial matches
        if len(suggestions) < limit:
            for system in self.systems:
                if partial_lower in system.lower() and system not in suggestions:
                    suggestions.append(system)
                    if len(suggestions) >= limit:
                        break
        
        return suggestions[:limit]

class CommodityValidator:
    def __init__(self):
        self.commodities = self.load_commodities()
    
    def load_commodities(self) -> Dict[str, Any]:
        """Load commodity data from JSON file"""
        try:
            with open('data/commodities.json', 'r') as f:
                data = json.load(f)
                return {item['name']: item for item in data['commodities']}
        except FileNotFoundError:
            logger.warning("Commodities data file not found, using default commodities")
            return self.get_default_commodities()
    
    def get_default_commodities(self) -> Dict[str, Any]:
        """Default commodities if data file is not available"""
        default_commodities = {
            'Aluminum': {'name': 'Aluminum', 'category': 'Metals', 'base_price': 340, 'rarity': 'common'},
            'Ceramic Composites': {'name': 'Ceramic Composites', 'category': 'Industrial Materials', 'base_price': 232, 'rarity': 'common'},
            'CMM Composites': {'name': 'CMM Composites', 'category': 'Industrial Materials', 'base_price': 3132, 'rarity': 'uncommon'},
            'Computer Components': {'name': 'Computer Components', 'category': 'Technology', 'base_price': 513, 'rarity': 'common'},
            'Copper': {'name': 'Copper', 'category': 'Metals', 'base_price': 481, 'rarity': 'common'},
            'Food Cartridges': {'name': 'Food Cartridges', 'category': 'Foods', 'base_price': 105, 'rarity': 'common'},
            'Fruit and Vegetables': {'name': 'Fruit and Vegetables', 'category': 'Foods', 'base_price': 312, 'rarity': 'common'},
            'Insulating Membrane': {'name': 'Insulating Membrane', 'category': 'Industrial Materials', 'base_price': 7837, 'rarity': 'rare'},
            'Liquid Oxygen': {'name': 'Liquid Oxygen', 'category': 'Chemicals', 'base_price': 263, 'rarity': 'common'},
            'Medical Diagnostic Equipment': {'name': 'Medical Diagnostic Equipment', 'category': 'Medicines', 'base_price': 2848, 'rarity': 'uncommon'},
            'Non-Lethal Weapons': {'name': 'Non-Lethal Weapons', 'category': 'Weapons', 'base_price': 1837, 'rarity': 'uncommon'},
            'Polymers': {'name': 'Polymers', 'category': 'Industrial Materials', 'base_price': 171, 'rarity': 'common'},
            'Power Generators': {'name': 'Power Generators', 'category': 'Machinery', 'base_price': 458, 'rarity': 'common'},
            'Semiconductors': {'name': 'Semiconductors', 'category': 'Technology', 'base_price': 967, 'rarity': 'uncommon'},
            'Steel': {'name': 'Steel', 'category': 'Metals', 'base_price': 335, 'rarity': 'common'},
            'Superconductors': {'name': 'Superconductors', 'category': 'Technology', 'base_price': 6609, 'rarity': 'rare'},
            'Titanium': {'name': 'Titanium', 'category': 'Metals', 'base_price': 1006, 'rarity': 'uncommon'},
            'Water': {'name': 'Water', 'category': 'Chemicals', 'base_price': 120, 'rarity': 'common'},
            'Water Purifiers': {'name': 'Water Purifiers', 'category': 'Machinery', 'base_price': 258, 'rarity': 'common'}
        }
        
        return default_commodities
    
    def is_valid_commodity(self, commodity_name: str) -> bool:
        """Check if a commodity name is valid"""
        if not commodity_name or not isinstance(commodity_name, str):
            return False
        
        # Check exact match first
        if commodity_name in self.commodities:
            return True
        
        # Check case-insensitive match
        for commodity in self.commodities:
            if commodity.lower() == commodity_name.lower():
                return True
        
        return False
    
    def get_commodity_suggestions(self, partial_name: str, limit: int = 5) -> List[str]:
        """Get commodity name suggestions based on partial input"""
        if not partial_name:
            return []
        
        suggestions = []
        partial_lower = partial_name.lower()
        
        # Exact matches first
        for commodity in self.commodities:
            if commodity.lower().startswith(partial_lower):
                suggestions.append(commodity)
        
        # Partial matches
        if len(suggestions) < limit:
            for commodity in self.commodities:
                if partial_lower in commodity.lower() and commodity not in suggestions:
                    suggestions.append(commodity)
                    if len(suggestions) >= limit:
                        break
        
        return suggestions[:limit]
    
    def get_all_commodities(self) -> List[Dict[str, Any]]:
        """Get all available commodities"""
        return list(self.commodities.values())
    
    def get_commodities_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get commodities by category"""
        return [
            commodity for commodity in self.commodities.values()
            if commodity.get('category', '').lower() == category.lower()
        ]
