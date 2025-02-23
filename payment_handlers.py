from web3 import Web3
from solana.rpc.api import Client
from binance.client import Client as BinanceClient
from datetime import datetime
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PaymentProcessor:
    def __init__(self, config):
        self.config = config
        # Initialize Web3 for Ethereum/MetaMask
        self.web3 = Web3(Web3.HTTPProvider(config.ETH_RPC_URL))
        # Initialize Solana client for Phantom
        self.solana_client = Client(config.SOLANA_RPC_URL)
        # Initialize Binance client
        self.binance_client = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        
        # Smart contract ABI and addresses
        self.payment_contract = self.web3.eth.contract(
            address=config.ETH_CONTRACT_ADDRESS,
            abi=config.ETH_CONTRACT_ABI
        )
    
    async def generate_payment_options(self, user_id: int, amount_usd: float) -> Dict:
        """Generate payment addresses and amounts for different methods"""
        try:
            # Get current prices
            eth_price = float(self.binance_client.get_symbol_ticker(symbol="ETHUSDT")['price'])
            sol_price = float(self.binance_client.get_symbol_ticker(symbol="SOLUSDT")['price'])
            bnb_price = float(self.binance_client.get_symbol_ticker(symbol="BNBUSDT")['price'])
            
            # Calculate amounts in different cryptocurrencies
            eth_amount = amount_usd / eth_price
            sol_amount = amount_usd / sol_price
            bnb_amount = amount_usd / bnb_price
            
            # Generate unique payment addresses for this transaction
            eth_address = self.generate_eth_address(user_id)
            sol_address = self.generate_sol_address(user_id)
            bnb_address = self.generate_binance_pay_qr(user_id, amount_usd)
            
            return {
                'metamask': {
                    'address': eth_address,
                    'amount': eth_amount,
                    'currency': 'ETH'
                },
                'phantom': {
                    'address': sol_address,
                    'amount': sol_amount,
                    'currency': 'SOL'
                },
                'binance': {
                    'qr_code': bnb_address,
                    'amount': bnb_amount,
                    'currency': 'BNB'
                }
            }
        except Exception as e:
            logger.error(f"Error generating payment options: {str(e)}")
            return None
    
    def generate_eth_address(self, user_id: int) -> str:
        """Generate ETH payment address"""
        # Create a unique payment address or use smart contract method
        account = self.web3.eth.account.create()
        return account.address
    
    def generate_sol_address(self, user_id: int) -> str:
        """Generate Solana payment address"""
        # Create a unique Solana payment address
        # This is a simplified example - implement proper Solana wallet generation
        return "SOLANA_ADDRESS"
    
    def generate_binance_pay_qr(self, user_id: int, amount_usd: float) -> str:
        """Generate Binance Pay QR code"""
        try:
            # Create Binance Pay merchant order
            order = self.binance_client.create_pay_order(
                merchant_id=self.config.BINANCE_MERCHANT_ID,
                amount=amount_usd,
                currency='USDT',
                order_id=f"premium_sub_{user_id}_{int(datetime.utcnow().timestamp())}"
            )
            return order['qrcode']
        except Exception as e:
            logger.error(f"Error generating Binance Pay QR: {str(e)}")
            return None
    
    async def verify_payment(self, payment_data: Dict) -> bool:
        """Verify payment across different methods"""
        try:
            if payment_data['method'] == 'metamask':
                return await self.verify_eth_payment(
                    payment_data['tx_hash'],
                    payment_data['amount']
                )
            elif payment_data['method'] == 'phantom':
                return await self.verify_sol_payment(
                    payment_data['tx_hash'],
                    payment_data['amount']
                )
            elif payment_data['method'] == 'binance':
                return await self.verify_binance_payment(
                    payment_data['order_id']
                )
            return False
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return False
    
    async def verify_eth_payment(self, tx_hash: str, expected_amount: float) -> bool:
        """Verify Ethereum payment"""
        try:
            tx = await self.web3.eth.get_transaction(tx_hash)
            if tx and tx['value'] >= self.web3.toWei(expected_amount, 'ether'):
                confirmations = await self.web3.eth.get_block_number() - tx['blockNumber']
                return confirmations >= 3  # Wait for 3 confirmations
            return False
        except Exception as e:
            logger.error(f"Error verifying ETH payment: {str(e)}")
            return False
    
    async def verify_sol_payment(self, tx_hash: str, expected_amount: float) -> bool:
        """Verify Solana payment"""
        try:
            tx = await self.solana_client.get_confirmed_transaction(tx_hash)
            # Implement Solana-specific verification logic
            return True if tx else False
        except Exception as e:
            logger.error(f"Error verifying SOL payment: {str(e)}")
            return False
    
    async def verify_binance_payment(self, order_id: str) -> bool:
        """Verify Binance Pay payment"""
        try:
            order_status = self.binance_client.get_pay_order(order_id)
            return order_status['status'] == 'PAID'
        except Exception as e:
            logger.error(f"Error verifying Binance payment: {str(e)}")
            return False