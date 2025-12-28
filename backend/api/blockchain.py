"""
Blockchain API - On-chain operations for Grammy Engine
Handles NFT minting, transfers, and marketplace operations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from services.web3_service import (
    mint_nft,
    transfer_nft,
    get_nft_owner,
    get_nft_metadata,
    get_wallet_balance,
    estimate_gas_fee,
    is_blockchain_enabled
)
from services.supabase_client import get_supabase

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class MintNFTRequest(BaseModel):
    track_id: str = Field(..., description="Track ID to mint as NFT")
    owner_address: str = Field(..., description="Wallet address of track owner")
    metadata_uri: str = Field(..., description="IPFS/HTTP URI to track metadata")
    royalty_percentage: int = Field(10, ge=0, le=100, description="Royalty percentage (0-100)")


class MintNFTResponse(BaseModel):
    success: bool
    transaction_hash: str
    token_id: Optional[int]
    block_number: int
    gas_used: int
    owner: str
    metadata_uri: str
    message: str


class TransferNFTRequest(BaseModel):
    token_id: int = Field(..., description="NFT token ID to transfer")
    from_address: str = Field(..., description="Current owner address")
    to_address: str = Field(..., description="New owner address")


class TransferNFTResponse(BaseModel):
    success: bool
    transaction_hash: str
    block_number: int
    gas_used: int
    message: str


class NFTInfoResponse(BaseModel):
    token_id: int
    track_id: str
    owner: str
    metadata_uri: str
    chain_id: int
    contract_address: str


class WalletBalanceResponse(BaseModel):
    address: str
    balance: float
    currency: str


class GasFeeEstimate(BaseModel):
    gas_price_gwei: float
    estimated_gas_units: int
    total_fee_eth: float
    transaction_type: str


@router.get("/status")
async def blockchain_status():
    """
    Get blockchain integration status
    """
    enabled = is_blockchain_enabled()
    
    return {
        "blockchain_enabled": enabled,
        "message": "Blockchain features are active" if enabled else "Blockchain not configured"
    }


@router.post("/nft/mint", response_model=MintNFTResponse)
async def mint_track_nft(request: MintNFTRequest):
    """
    Mint NFT for a music track on-chain
    
    This creates an ERC721 NFT on the blockchain representing ownership
    of the music track. The NFT includes:
    - Ownership record
    - Metadata URI (IPFS/HTTP link to track info)
    - Built-in royalty support
    
    **On-chain operation** - requires blockchain connection
    """
    try:
        # Check if blockchain is enabled
        if not is_blockchain_enabled():
            raise HTTPException(
                status_code=503,
                detail="Blockchain features not configured. Please set WEB3_RPC_URL and WEB3_PRIVATE_KEY"
            )
        
        logger.info(f"Minting NFT for track {request.track_id}")
        
        # Convert royalty percentage to basis points (10000 = 100%)
        royalty_bp = request.royalty_percentage * 100
        
        # Mint NFT on-chain
        result = await mint_nft(
            track_id=request.track_id,
            owner_address=request.owner_address,
            metadata_uri=request.metadata_uri,
            royalty_percentage=royalty_bp
        )
        
        # Update database with NFT info
        supabase = get_supabase()
        if supabase:
            try:
                supabase.table("tracks").update({
                    "nft_token_id": result.get("token_id"),
                    "nft_transaction_hash": result.get("transaction_hash"),
                    "nft_minted": True,
                    "nft_owner": request.owner_address
                }).eq("id", request.track_id).execute()
            except Exception as e:
                logger.warning(f"Failed to update database with NFT info: {e}")
        
        return MintNFTResponse(
            success=True,
            transaction_hash=result["transaction_hash"],
            token_id=result.get("token_id"),
            block_number=result["block_number"],
            gas_used=result["gas_used"],
            owner=result["owner"],
            metadata_uri=result["metadata_uri"],
            message="NFT minted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NFT minting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mint NFT: {str(e)}")


@router.post("/nft/transfer", response_model=TransferNFTResponse)
async def transfer_track_nft(request: TransferNFTRequest):
    """
    Transfer NFT ownership on-chain
    
    Transfers ownership of a track NFT from one wallet to another.
    
    **On-chain operation** - requires blockchain connection
    """
    try:
        # Check if blockchain is enabled
        if not is_blockchain_enabled():
            raise HTTPException(
                status_code=503,
                detail="Blockchain features not configured"
            )
        
        logger.info(f"Transferring NFT {request.token_id}")
        
        # Transfer NFT on-chain
        result = await transfer_nft(
            token_id=request.token_id,
            from_address=request.from_address,
            to_address=request.to_address
        )
        
        # Update database
        supabase = get_supabase()
        if supabase:
            try:
                supabase.table("tracks").update({
                    "nft_owner": request.to_address,
                    "nft_transfer_hash": result.get("transaction_hash")
                }).eq("nft_token_id", request.token_id).execute()
            except Exception as e:
                logger.warning(f"Failed to update database with transfer info: {e}")
        
        return TransferNFTResponse(
            success=True,
            transaction_hash=result["transaction_hash"],
            block_number=result["block_number"],
            gas_used=result["gas_used"],
            message="NFT transferred successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NFT transfer failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to transfer NFT: {str(e)}")


@router.get("/nft/{token_id}", response_model=NFTInfoResponse)
async def get_nft_info(token_id: int):
    """
    Get NFT information from blockchain
    
    Retrieves on-chain information about a track NFT including:
    - Current owner
    - Metadata URI
    - Track ID
    
    **On-chain read operation** - requires blockchain connection
    """
    try:
        # Check if blockchain is enabled
        if not is_blockchain_enabled():
            raise HTTPException(
                status_code=503,
                detail="Blockchain features not configured"
            )
        
        # Get NFT info from blockchain
        owner = await get_nft_owner(token_id)
        metadata_uri = await get_nft_metadata(token_id)
        
        # Get track ID from database
        supabase = get_supabase()
        track_id = None
        
        if supabase:
            try:
                result = supabase.table("tracks").select("id").eq("nft_token_id", token_id).single().execute()
                if result.data:
                    track_id = result.data.get("id")
            except Exception as e:
                logger.warning(f"Failed to get track ID: {e}")
        
        import os
        
        return NFTInfoResponse(
            token_id=token_id,
            track_id=track_id or "unknown",
            owner=owner,
            metadata_uri=metadata_uri,
            chain_id=int(os.getenv("WEB3_CHAIN_ID", "1")),
            contract_address=os.getenv("NFT_CONTRACT_ADDRESS", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get NFT info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get NFT info: {str(e)}")


@router.get("/wallet/{address}/balance", response_model=WalletBalanceResponse)
async def get_balance(address: str):
    """
    Get wallet balance
    
    Returns the ETH/MATIC balance of a wallet address.
    
    **On-chain read operation** - requires blockchain connection
    """
    try:
        # Check if blockchain is enabled
        if not is_blockchain_enabled():
            raise HTTPException(
                status_code=503,
                detail="Blockchain features not configured"
            )
        
        balance = await get_wallet_balance(address)
        
        import os
        chain_id = int(os.getenv("WEB3_CHAIN_ID", "1"))
        currency = "ETH" if chain_id == 1 else "MATIC" if chain_id == 137 else "ETH"
        
        return WalletBalanceResponse(
            address=address,
            balance=balance,
            currency=currency
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get wallet balance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get wallet balance: {str(e)}")


@router.get("/gas/estimate", response_model=GasFeeEstimate)
async def estimate_gas(transaction_type: str = "mint"):
    """
    Estimate gas fee for transaction
    
    Returns estimated gas costs for different transaction types:
    - mint: Minting a new NFT
    - transfer: Transferring an NFT
    - approve: Approving a marketplace
    
    **On-chain read operation** - requires blockchain connection
    """
    try:
        # Check if blockchain is enabled
        if not is_blockchain_enabled():
            raise HTTPException(
                status_code=503,
                detail="Blockchain features not configured"
            )
        
        estimate = await estimate_gas_fee(transaction_type)
        
        return GasFeeEstimate(
            gas_price_gwei=float(estimate["gas_price_gwei"]),
            estimated_gas_units=estimate["estimated_gas_units"],
            total_fee_eth=estimate["total_fee_eth"],
            transaction_type=transaction_type
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to estimate gas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to estimate gas: {str(e)}")


@router.get("/tracks/minted")
async def get_minted_tracks(skip: int = 0, limit: int = 20):
    """
    Get list of tracks that have been minted as NFTs
    
    **Off-chain operation** - reads from database
    """
    try:
        supabase = get_supabase()
        
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Query tracks with NFTs
        result = supabase.table("tracks").select("*").eq("nft_minted", True).range(skip, skip + limit - 1).execute()
        
        tracks = result.data if result.data else []
        
        return {
            "total": len(tracks),
            "tracks": tracks,
            "skip": skip,
            "limit": limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get minted tracks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get minted tracks: {str(e)}")
