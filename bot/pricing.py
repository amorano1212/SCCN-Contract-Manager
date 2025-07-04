import json
import math
import random
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class PricingCalculator:
    def __init__(self):
        self.commodity_prices = self.load_commodity_prices()
        self.system_distances = self.load_system_distances()
        
        # Pricing parameters
        self.base_transport_rate = 50  # CR per ton per LY
        self.risk_premium_rate = 0.15  # 15% risk premium
        self.fuel_cost_per_ly = 100  # Base fuel cost per LY
        self.time_value_multiplier = 0.02  # 2% per hour premium for long routes
    
    def load_commodity_prices(self) -> Dict[str, Dict[str, Any]]:
        """Load commodity pricing data"""
        try:
            with open('data/commodities.json', 'r') as f:
                data = json.load(f)
                return {item['name']: item for item in data['commodities']}
        except FileNotFoundError:
            logger.warning("Commodities data file not found, using default pricing")
            return self.get_default_commodity_prices()
    
    def load_system_distances(self) -> Dict[str, Dict[str, float]]:
        """Load system distance data"""
        try:
            with open('data/systems.json', 'r') as f:
                data = json.load(f)
                return data.get('distances', {})
        except FileNotFoundError:
            logger.warning("Systems data file not found, using estimated distances")
            return {}
    
    def get_default_commodity_prices(self) -> Dict[str, Dict[str, Any]]:
        """Default commodity prices if data file is not available"""
        return {
            'Aluminum': {'base_price': 340, 'category': 'Metals', 'rarity': 'common'},
            'Ceramic Composites': {'base_price': 232, 'category': 'Industrial Materials', 'rarity': 'common'},
            'CMM Composites': {'base_price': 3132, 'category': 'Industrial Materials', 'rarity': 'uncommon'},
            'Computer Components': {'base_price': 513, 'category': 'Technology', 'rarity': 'common'},
            'Copper': {'base_price': 481, 'category': 'Metals', 'rarity': 'common'},
            'Food Cartridges': {'base_price': 105, 'category': 'Foods', 'rarity': 'common'},
            'Fruit and Vegetables': {'base_price': 312, 'category': 'Foods', 'rarity': 'common'},
            'Insulating Membrane': {'base_price': 7837, 'category': 'Industrial Materials', 'rarity': 'rare'},
            'Liquid Oxygen': {'base_price': 263, 'category': 'Chemicals', 'rarity': 'common'},
            'Medical Diagnostic Equipment': {'base_price': 2848, 'category': 'Medicines', 'rarity': 'uncommon'},
            'Non-Lethal Weapons': {'base_price': 1837, 'category': 'Weapons', 'rarity': 'uncommon'},
            'Polymers': {'base_price': 171, 'category': 'Industrial Materials', 'rarity': 'common'},
            'Power Generators': {'base_price': 458, 'category': 'Machinery', 'rarity': 'common'},
            'Semiconductors': {'base_price': 967, 'category': 'Technology', 'rarity': 'uncommon'},
            'Steel': {'base_price': 335, 'category': 'Metals', 'rarity': 'common'},
            'Superconductors': {'base_price': 6609, 'category': 'Technology', 'rarity': 'rare'},
            'Titanium': {'base_price': 1006, 'category': 'Metals', 'rarity': 'uncommon'},
            'Water': {'base_price': 120, 'category': 'Chemicals', 'rarity': 'common'},
            'Water Purifiers': {'base_price': 258, 'category': 'Machinery', 'rarity': 'common'},
        }
    
    def calculate_quote(
        self,
        commodities: List[str],
        quantities: List[int],
        destination: str,
        source: str = None
    ) -> Dict[str, Any]:
        """Calculate a complete quote for commodity delivery"""
        
        # Determine source system
        if not source:
            source = self.get_nearest_supply_hub(destination)
        
        # Calculate distance
        distance = self.calculate_distance(source, destination)
        
        # Calculate commodity costs and transport fees
        commodity_costs = []
        commodity_prices = []
        total_commodity_cost = 0
        total_tonnage = 0
        
        for i, (commodity, quantity) in enumerate(zip(commodities, quantities)):
            commodity_data = self.commodity_prices.get(commodity, {})
            base_price = commodity_data.get('base_price', 500)  # Default if not found
            rarity = commodity_data.get('rarity', 'common')
            
            # Apply market fluctuation (±10%)
            price_variation = random.uniform(0.9, 1.1)
            unit_price = int(base_price * price_variation)
            
            # Apply rarity multiplier
            rarity_multiplier = {'common': 1.0, 'uncommon': 1.3, 'rare': 1.8}.get(rarity, 1.0)
            unit_price = int(unit_price * rarity_multiplier)
            
            commodity_cost = unit_price * quantity
            commodity_costs.append(commodity_cost)
            commodity_prices.append(unit_price)
            total_commodity_cost += commodity_cost
            
            # Assume 1 unit = 1 ton for simplicity
            total_tonnage += quantity
        
        # Calculate transport fee
        base_transport_fee = int(total_tonnage * distance * self.base_transport_rate)
        
        # Distance-based multiplier
        distance_multiplier = 1.0
        if distance > 500:
            distance_multiplier = 1.2
        elif distance > 1000:
            distance_multiplier = 1.5
        elif distance > 2000:
            distance_multiplier = 2.0
        
        transport_fee = int(base_transport_fee * distance_multiplier)
        
        # Calculate risk premium
        risk_premium = int(total_commodity_cost * self.risk_premium_rate)
        
        # Add fuel costs
        fuel_cost = int(distance * self.fuel_cost_per_ly)
        
        # Calculate estimated delivery time
        estimated_hours = self.calculate_delivery_time(distance, total_tonnage)
        
        # Time-based premium for long deliveries
        time_premium = 0
        if estimated_hours > 24:
            time_premium = int(total_commodity_cost * self.time_value_multiplier * (estimated_hours / 24))
        
        # Calculate totals
        total_cost = total_commodity_cost + transport_fee + risk_premium + fuel_cost + time_premium
        
        quote_data = {
            'source': source,
            'destination': destination,
            'distance': distance,
            'commodities': commodities,
            'quantities': quantities,
            'commodity_prices': commodity_prices,
            'commodity_costs': commodity_costs,
            'commodity_cost': total_commodity_cost,
            'transport_fee': transport_fee,
            'risk_premium': risk_premium,
            'fuel_cost': fuel_cost,
            'time_premium': time_premium,
            'total_cost': total_cost,
            'total_tonnage': total_tonnage,
            'estimated_delivery_hours': estimated_hours,
            'distance_multiplier': distance_multiplier
        }
        
        return quote_data
    
    def calculate_distance(self, source: str, destination: str) -> float:
        """Calculate distance between two systems"""
        # Try to get actual distance from data
        if source in self.system_distances:
            if destination in self.system_distances[source]:
                return self.system_distances[source][destination]
        
        # Fall back to estimated distance based on known systems
        return self.estimate_distance(source, destination)
    
    def estimate_distance(self, source: str, destination: str) -> float:
        """Estimate distance between systems"""
        # Known system distances from Sol
        known_distances = {
            'Sol': 0,
            'Colonia': 22000,
            'Sagittarius A*': 25900,
            'Beagle Point': 65279,
            'Hutton Orbital': 6784,  # Alpha Centauri
            'Barnard\'s Star': 5.95,
            'Wolf 359': 7.86,
            'Lalande 21185': 8.29,
            'Sirius': 8.59,
            'Ross 154': 9.69,
            'Epsilon Eridani': 10.52,
            'Lacaille 9352': 10.74,
            'Ross 128': 11.03,
            'EZ Aquarii': 11.27,
            'Procyon': 11.46,
            'Luyten 726-8': 12.39,
            'Tau Ceti': 11.94,
            'Epsilon Indi': 11.82
        }
        
        source_dist = known_distances.get(source, random.uniform(50, 500))
        dest_dist = known_distances.get(destination, random.uniform(50, 500))
        
        # Simple estimation - could be improved with actual coordinates
        if source == destination:
            return 0
        
        # If one is Sol, return the other's distance
        if source == 'Sol':
            return dest_dist
        if destination == 'Sol':
            return source_dist
        
        # Otherwise, estimate based on triangle inequality
        estimated_distance = abs(dest_dist - source_dist)
        if estimated_distance < 10:  # Minimum distance
            estimated_distance = random.uniform(10, 50)
        
        return estimated_distance
    
    def get_nearest_supply_hub(self, destination: str) -> str:
        """Get the nearest supply hub to a destination"""
        # Major supply hubs in Elite Dangerous
        supply_hubs = [
            'Sol', 'Shinrarta Dezhra', 'Jameson Memorial',
            'LHS 3447', 'Eravate', 'Matet', 'Kremainn',
            'Beta Hydri', 'Wolf 397', 'LTT 15574'
        ]
        
        min_distance = float('inf')
        nearest_hub = 'Sol'  # Default
        
        for hub in supply_hubs:
            distance = self.calculate_distance(hub, destination)
            if distance < min_distance:
                min_distance = distance
                nearest_hub = hub
        
        return nearest_hub
    
    def calculate_delivery_time(self, distance: float, tonnage: int) -> int:
        """Calculate estimated delivery time in hours"""
        # Base time calculation
        # Assume average jump distance of 30 LY and 5 minutes per jump
        jumps = math.ceil(distance / 30)
        jump_time = jumps * 5  # minutes
        
        # Loading/unloading time based on tonnage
        loading_time = tonnage * 0.5  # 30 seconds per ton
        
        # Add buffer time for refueling, repairs, etc.
        buffer_time = jumps * 2  # 2 minutes per jump for misc activities
        
        total_minutes = jump_time + loading_time + buffer_time
        
        # Convert to hours and round up
        hours = max(1, math.ceil(total_minutes / 60))
        
        return hours
