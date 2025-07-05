import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from typing import List, Optional
from .contract_manager import ContractManager
from .pricing import PricingCalculator
from .validation import SystemValidator, CommodityValidator

logger = logging.getLogger(__name__)

# Global instances
contract_manager = ContractManager()
pricing_calculator = PricingCalculator()
system_validator = SystemValidator()
commodity_validator = CommodityValidator()

async def setup_commands(bot: commands.Bot):
    """Set up all bot commands"""
    
    @bot.tree.command(name="request_quote", description="Request a quote for colonization commodity delivery")
    @app_commands.describe(
        commodities="Comma-separated list of commodities (e.g., 'Food Cartridges, Medical Supplies')",
        quantities="Comma-separated list of quantities matching commodities (e.g., '100, 50')",
        destination="Destination system name",
        primary_port="Is this for a primary port on a timer? (true/false)",
        days_left="If primary port, how many days are left on the timer? (leave blank if not primary port)"
    )
    async def request_quote(
        interaction: discord.Interaction,
        commodities: str,
        quantities: str,
        destination: str,
        primary_port: bool = False,
        days_left: Optional[int] = None
    ):
        """Handle quote requests for commodity contracts"""
        await interaction.response.defer()
        
        try:
            # Parse and validate inputs
            commodity_list = [c.strip() for c in commodities.split(',')]
            quantity_list = [int(q.strip()) for q in quantities.split(',')]
            
            if len(commodity_list) != len(quantity_list):
                await interaction.followup.send(
                    "❌ **Error**: Number of commodities must match number of quantities!\n"
                    "Example: `/request_quote commodities:Food Cartridges,Medical Supplies quantities:100,50 destination:Colonia`"
                )
                return
            
            # Validate destination system (just check it's not empty)
            if not system_validator.is_valid_system(destination):
                await interaction.followup.send(
                    f"❌ **Error**: Please provide a valid system name for the destination."
                )
                return
            
            # Validate commodities
            invalid_commodities = []
            for commodity in commodity_list:
                if not commodity_validator.is_valid_commodity(commodity):
                    invalid_commodities.append(commodity)
            
            if invalid_commodities:
                await interaction.followup.send(
                    f"❌ **Error**: Invalid commodities: {', '.join(invalid_commodities)}\n"
                    "Use `/list_commodities` to see available commodities."
                )
                return
            
            # Validate quantities
            for i, qty in enumerate(quantity_list):
                if qty <= 0:
                    await interaction.followup.send(
                        f"❌ **Error**: Quantity for '{commodity_list[i]}' must be greater than 0."
                    )
                    return
            
            # Calculate quote
            quote_data = pricing_calculator.calculate_quote(
                commodity_list, quantity_list, destination, primary_port, days_left
            )
            
            # Create contract
            contract_id = contract_manager.create_contract(
                user_id=interaction.user.id,
                commodities=commodity_list,
                quantities=quantity_list,
                destination=destination,
                primary_port=primary_port,
                days_left=days_left,
                quote_data=quote_data
            )
            
            # Create embed response
            embed = discord.Embed(
                title="🚀 Colonization Contract Quote",
                description=f"**Contract ID**: `{contract_id}`",
                color=0x00ff00
            )
            
            # Add commodity details
            commodity_text = ""
            for commodity, quantity in zip(commodity_list, quantity_list):
                commodity_text += f"• **{commodity}**: {quantity:,} units\n"
            
            embed.add_field(
                name="📦 Commodities",
                value=commodity_text,
                inline=False
            )
            
            embed.add_field(
                name="🗺️ Destination",
                value=destination,
                inline=True
            )
            
            # Primary port info
            if primary_port:
                port_info = "Yes"
                if days_left is not None:
                    port_info += f" ({days_left} days left)"
                embed.add_field(
                    name="⏰ Primary Port Timer",
                    value=port_info,
                    inline=True
                )
            
            embed.add_field(
                name="💰 Total Cost",
                value=f"{quote_data['total_cost']:,} CR",
                inline=False
            )
            
            embed.set_footer(text="Use /accept_contract to accept this quote within 24 hours")
            
            await interaction.followup.send(embed=embed)
            
        except ValueError as e:
            await interaction.followup.send(
                f"❌ **Error**: Invalid quantity format. Please use numbers only.\n"
                f"Example: `100, 50, 200`"
            )
        except Exception as e:
            logger.error(f"Error in request_quote: {e}")
            await interaction.followup.send(
                "❌ **Error**: An unexpected error occurred. Please try again later."
            )
    
    @bot.tree.command(name="accept_contract", description="Accept a contract quote")
    @app_commands.describe(contract_id="The contract ID from your quote")
    async def accept_contract(interaction: discord.Interaction, contract_id: str):
        """Accept a contract quote"""
        await interaction.response.defer()
        
        try:
            contract = contract_manager.get_contract(contract_id)
            
            if not contract:
                await interaction.followup.send(
                    f"❌ **Error**: Contract `{contract_id}` not found or has expired."
                )
                return
            
            if contract['user_id'] != interaction.user.id:
                await interaction.followup.send(
                    "❌ **Error**: You can only accept your own contracts."
                )
                return
            
            if contract['status'] != 'pending':
                await interaction.followup.send(
                    f"❌ **Error**: Contract `{contract_id}` is already {contract['status']}."
                )
                return
            
            # Accept the contract
            contract_manager.accept_contract(contract_id)
            
            embed = discord.Embed(
                title="✅ Contract Accepted",
                description=f"**Contract ID**: `{contract_id}`\n**Status**: Accepted",
                color=0x00ff00
            )
            
            embed.add_field(
                name="💰 Total Cost",
                value=f"{contract['quote_data']['total_cost']:,} CR",
                inline=True
            )
            
            embed.add_field(
                name="⏱️ Estimated Delivery",
                value=f"{contract['quote_data']['estimated_delivery_hours']} hours",
                inline=True
            )
            
            embed.set_footer(text="You will be contacted for payment and delivery coordination.")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in accept_contract: {e}")
            await interaction.followup.send(
                "❌ **Error**: An unexpected error occurred. Please try again later."
            )
    
    @bot.tree.command(name="list_contracts", description="List your active contracts")
    async def list_contracts(interaction: discord.Interaction):
        """List user's contracts"""
        await interaction.response.defer()
        
        try:
            contracts = contract_manager.get_user_contracts(interaction.user.id)
            
            if not contracts:
                await interaction.followup.send(
                    "📋 You have no active contracts. Use `/request_quote` to create one!"
                )
                return
            
            embed = discord.Embed(
                title="📋 Your Active Contracts",
                color=0x0099ff
            )
            
            for contract in contracts[:10]:  # Limit to 10 contracts
                status_emoji = {
                    'pending': '⏳',
                    'accepted': '✅',
                    'in_progress': '🚚',
                    'delivered': '✅',
                    'cancelled': '❌'
                }.get(contract['status'], '❓')
                
                commodities_text = ', '.join([
                    f"{contract['commodities'][i]} ({contract['quantities'][i]})"
                    for i in range(len(contract['commodities']))
                ])
                
                embed.add_field(
                    name=f"{status_emoji} {contract['contract_id']}",
                    value=f"**To**: {contract['destination']}\n"
                          f"**Items**: {commodities_text}\n"
                          f"**Cost**: {contract['quote_data']['total_cost']:,} CR\n"
                          f"**Status**: {contract['status'].title()}",
                    inline=True
                )
            
            if len(contracts) > 10:
                embed.set_footer(text=f"Showing 10 of {len(contracts)} contracts")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in list_contracts: {e}")
            await interaction.followup.send(
                "❌ **Error**: An unexpected error occurred. Please try again later."
            )
    
    @bot.tree.command(name="list_commodities", description="List available colonization commodities")
    async def list_commodities(interaction: discord.Interaction):
        """List available commodities"""
        await interaction.response.defer()
        
        try:
            commodities = commodity_validator.get_all_commodities()
            
            embed = discord.Embed(
                title="📦 Available Colonization Commodities",
                description="These commodities are available for colonization contracts:",
                color=0x0099ff
            )
            
            # Group commodities by category
            categories = {}
            for commodity in commodities:
                category = commodity.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(commodity['name'])
            
            for category, items in categories.items():
                embed.add_field(
                    name=f"**{category}**",
                    value='\n'.join([f"• {item}" for item in sorted(items)]),
                    inline=True
                )
            
            embed.set_footer(text="Use these exact names in your /request_quote command")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in list_commodities: {e}")
            await interaction.followup.send(
                "❌ **Error**: An unexpected error occurred. Please try again later."
            )
    
    @bot.tree.command(name="help", description="Show help information for the bot")
    async def help_command(interaction: discord.Interaction):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 Elite Dangerous Colonization Bot Help",
            description="This bot helps you request quotes for colonization commodity deliveries.",
            color=0x0099ff
        )
        
        embed.add_field(
            name="📝 **Commands**",
            value=(
                "`/request_quote` - Request a quote for commodity delivery\n"
                "`/accept_contract` - Accept a contract quote\n"
                "`/list_contracts` - View your active contracts\n"
                "`/list_commodities` - See available commodities\n"
                "`/help` - Show this help message"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📋 **How to Request a Quote**",
            value=(
                "1. Use `/request_quote` with:\n"
                "   • **commodities**: List separated by commas\n"
                "   • **quantities**: Numbers separated by commas\n"
                "   • **destination**: Target system name\n"
                "   • **primary_port**: True if for primary port timer\n"
                "   • **days_left**: Days remaining if primary port\n\n"
                "**Example**: `/request_quote commodities:Aluminum,Steel quantities:100,50 destination:YourSystem primary_port:true days_left:5`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 **Tips**",
            value=(
                "• Use exact commodity names from `/list_commodities`\n"
                "• Quotes expire after 24 hours\n"
                "• Any system name can be used as destination\n"
                "• Standard rate: 60,000 CR per unit\n"
                "• Primary port urgent (≤10 days): 80,000 CR per unit"
            ),
            inline=False
        )
        
        embed.set_footer(text="For support, contact the bot administrator")
        
        await interaction.followup.send(embed=embed)

    logger.info("Commands setup completed")
