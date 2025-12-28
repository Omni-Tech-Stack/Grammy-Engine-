"""
Web3 Service - Blockchain integration for Grammy Engine
Handles on-chain operations including NFT minting, ownership, and marketplace
"""
import os
import logging
from typing import Optional, Dict, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json

logger = logging.getLogger(__name__)

# Configuration
RPC_URL = os.getenv("WEB3_RPC_URL", "https://mainnet.infura.io/v3/YOUR-PROJECT-ID")
CHAIN_ID = int(os.getenv("WEB3_CHAIN_ID", "1"))  # 1 = Ethereum Mainnet, 137 = Polygon
PRIVATE_KEY = os.getenv("WEB3_PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS", "")

# Global Web3 instance
w3: Optional[Web3] = None
account: Optional[Account] = None


def init_web3() -> Web3:
    """
    Initialize Web3 connection to blockchain
    """
    global w3, account
    
    if not RPC_URL:
        logger.warning("Web3 RPC URL not configured")
        return None
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        # Add PoA middleware for networks like Polygon
        if CHAIN_ID in [137, 80001]:  # Polygon mainnet/testnet
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check connection
        if not w3.is_connected():
            logger.error("Failed to connect to blockchain")
            return None
        
        # Load account if private key is provided
        if PRIVATE_KEY:
            account = Account.from_key(PRIVATE_KEY)
            logger.info(f"Web3 account loaded: {account.address}")
        
        logger.info(f"Web3 initialized on chain {CHAIN_ID}")
        return w3
    
    except Exception as e:
        logger.error(f"Failed to initialize Web3: {e}")
        raise


def get_web3() -> Web3:
    """
    Get Web3 instance
    """
    global w3
    
    if w3 is None or not w3.is_connected():
        w3 = init_web3()
    
    return w3


def get_contract(contract_address: str = None, abi: list = None):
    """
    Get smart contract instance
    
    Args:
        contract_address: Contract address (uses env default if None)
        abi: Contract ABI (loads from file if None)
    
    Returns:
        Contract instance
    """
    try:
        web3 = get_web3()
        
        if not web3:
            raise ValueError("Web3 not initialized")
        
        # Use provided address or default
        address = contract_address or CONTRACT_ADDRESS
        
        if not address:
            raise ValueError("Contract address not provided")
        
        # Load ABI if not provided
        if abi is None:
            # Load from contracts directory
            abi_path = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "contracts", 
                "GrammyNFT.json"
            )
            
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    contract_data = json.load(f)
                    abi = contract_data.get('abi', [])
            else:
                logger.warning(f"ABI file not found: {abi_path}")
                abi = []
        
        # Create contract instance
        contract = web3.eth.contract(address=address, abi=abi)
        
        return contract
    
    except Exception as e:
        logger.error(f"Failed to get contract: {e}")
        raise


async def mint_nft(
    track_id: str,
    owner_address: str,
    metadata_uri: str,
    royalty_percentage: int = 10
) -> Dict[str, Any]:
    """
    Mint NFT for a music track on-chain
    
    Args:
        track_id: Unique track identifier
        owner_address: Wallet address of track owner
        metadata_uri: IPFS/HTTP URI to track metadata
        royalty_percentage: Royalty percentage (0-100)
    
    Returns:
        Transaction receipt and token ID
    """
    try:
        logger.info(f"Minting NFT for track {track_id}")
        
        web3 = get_web3()
        
        if not web3:
            raise ValueError("Web3 not initialized")
        
        if not account:
            raise ValueError("Web3 account not configured")
        
        # Get contract
        contract = get_contract()
        
        # Prepare transaction
        nonce = web3.eth.get_transaction_count(account.address)
        
        # Build mint transaction
        mint_tx = contract.functions.mintTrack(
            owner_address,
            metadata_uri,
            royalty_percentage
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 500000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
        })
        
        # Sign transaction
        signed_tx = web3.eth.account.sign_transaction(mint_tx, PRIVATE_KEY)
        
        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"NFT mint transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        # Extract token ID from logs
        token_id = None
        if tx_receipt.logs:
            # Parse Transfer event to get token ID
            try:
                transfer_event = contract.events.Transfer().process_receipt(tx_receipt)
                if transfer_event:
                    token_id = transfer_event[0]['args']['tokenId']
            except Exception as e:
                logger.warning(f"Could not parse token ID from logs: {e}")
        
        result = {
            "success": True,
            "transaction_hash": tx_hash.hex(),
            "token_id": token_id,
            "block_number": tx_receipt['blockNumber'],
            "gas_used": tx_receipt['gasUsed'],
            "owner": owner_address,
            "metadata_uri": metadata_uri
        }
        
        logger.info(f"NFT minted successfully: Token ID {token_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"NFT minting failed: {e}")
        raise


async def transfer_nft(
    token_id: int,
    from_address: str,
    to_address: str
) -> Dict[str, Any]:
    """
    Transfer NFT ownership on-chain
    
    Args:
        token_id: NFT token ID
        from_address: Current owner address
        to_address: New owner address
    
    Returns:
        Transaction receipt
    """
    try:
        logger.info(f"Transferring NFT {token_id} from {from_address} to {to_address}")
        
        web3 = get_web3()
        
        if not web3 or not account:
            raise ValueError("Web3 not initialized")
        
        # Get contract
        contract = get_contract()
        
        # Prepare transaction
        nonce = web3.eth.get_transaction_count(account.address)
        
        # Build transfer transaction
        transfer_tx = contract.functions.transferFrom(
            from_address,
            to_address,
            token_id
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
        })
        
        # Sign and send
        signed_tx = web3.eth.account.sign_transaction(transfer_tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Transfer transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        result = {
            "success": True,
            "transaction_hash": tx_hash.hex(),
            "block_number": tx_receipt['blockNumber'],
            "gas_used": tx_receipt['gasUsed']
        }
        
        logger.info(f"NFT transferred successfully")
        
        return result
    
    except Exception as e:
        logger.error(f"NFT transfer failed: {e}")
        raise


async def get_nft_owner(token_id: int) -> str:
    """
    Get current owner of NFT
    
    Args:
        token_id: NFT token ID
    
    Returns:
        Owner wallet address
    """
    try:
        web3 = get_web3()
        
        if not web3:
            raise ValueError("Web3 not initialized")
        
        contract = get_contract()
        
        owner = contract.functions.ownerOf(token_id).call()
        
        return owner
    
    except Exception as e:
        logger.error(f"Failed to get NFT owner: {e}")
        raise


async def get_nft_metadata(token_id: int) -> str:
    """
    Get NFT metadata URI
    
    Args:
        token_id: NFT token ID
    
    Returns:
        Metadata URI
    """
    try:
        web3 = get_web3()
        
        if not web3:
            raise ValueError("Web3 not initialized")
        
        contract = get_contract()
        
        metadata_uri = contract.functions.tokenURI(token_id).call()
        
        return metadata_uri
    
    except Exception as e:
        logger.error(f"Failed to get NFT metadata: {e}")
        raise


async def get_wallet_balance(address: str) -> float:
    """
    Get ETH/MATIC balance of wallet
    
    Args:
        address: Wallet address
    
    Returns:
        Balance in ETH/MATIC
    """
    try:
        web3 = get_web3()
        
        if not web3:
            raise ValueError("Web3 not initialized")
        
        balance_wei = web3.eth.get_balance(address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
        
        return float(balance_eth)
    
    except Exception as e:
        logger.error(f"Failed to get wallet balance: {e}")
        raise


async def estimate_gas_fee(transaction_type: str = "mint") -> Dict[str, float]:
    """
    Estimate gas fee for transaction
    
    Args:
        transaction_type: Type of transaction (mint, transfer)
    
    Returns:
        Gas estimates in Wei and ETH/MATIC
    """
    try:
        web3 = get_web3()
        
        if not web3:
            raise ValueError("Web3 not initialized")
        
        # Get current gas price
        gas_price = web3.eth.gas_price
        
        # Estimate gas units based on transaction type
        gas_units = {
            "mint": 500000,
            "transfer": 200000,
            "approve": 100000
        }
        
        estimated_gas = gas_units.get(transaction_type, 200000)
        
        # Calculate total fee
        total_fee_wei = gas_price * estimated_gas
        total_fee_eth = web3.from_wei(total_fee_wei, 'ether')
        
        return {
            "gas_price_wei": gas_price,
            "gas_price_gwei": web3.from_wei(gas_price, 'gwei'),
            "estimated_gas_units": estimated_gas,
            "total_fee_wei": total_fee_wei,
            "total_fee_eth": float(total_fee_eth)
        }
    
    except Exception as e:
        logger.error(f"Failed to estimate gas fee: {e}")
        raise


def is_blockchain_enabled() -> bool:
    """
    Check if blockchain features are enabled
    
    Returns:
        True if Web3 is configured and connected
    """
    try:
        web3 = get_web3()
        return web3 is not None and web3.is_connected()
    except Exception:
        return False
