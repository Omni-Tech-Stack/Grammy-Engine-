// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title GrammyNFT
 * @dev NFT contract for Grammy Engine music tracks
 * Features:
 * - ERC721 standard NFT
 * - Metadata storage (IPFS/HTTP URIs)
 * - Built-in royalty support (EIP-2981)
 * - Track ownership and transfers
 * - Marketplace integration ready
 */
contract GrammyNFT is ERC721, ERC721URIStorage, ERC721Royalty, Ownable {
    using Counters for Counters.Counter;
    
    // Token ID counter
    Counters.Counter private _tokenIdCounter;
    
    // Mapping from token ID to track ID (off-chain reference)
    mapping(uint256 => string) private _trackIds;
    
    // Mapping from track ID to token ID (reverse lookup)
    mapping(string => uint256) private _trackToToken;
    
    // Mapping to track minting timestamps
    mapping(uint256 => uint256) private _mintTimestamps;
    
    // Events
    event TrackMinted(
        uint256 indexed tokenId,
        string trackId,
        address indexed owner,
        string metadataURI,
        uint96 royaltyPercentage
    );
    
    event TrackTransferred(
        uint256 indexed tokenId,
        address indexed from,
        address indexed to
    );
    
    /**
     * @dev Constructor
     */
    constructor() ERC721("Grammy Engine Track", "GRMY") Ownable(msg.sender) {
        // Start token IDs at 1
        _tokenIdCounter.increment();
    }
    
    /**
     * @dev Mint a new NFT for a music track
     * @param to Address to mint NFT to
     * @param trackId Unique track identifier (off-chain reference)
     * @param metadataURI IPFS or HTTP URI to track metadata
     * @param royaltyPercentage Royalty percentage (0-10000, where 10000 = 100%)
     */
    function mintTrack(
        address to,
        string memory trackId,
        string memory metadataURI,
        uint96 royaltyPercentage
    ) public onlyOwner returns (uint256) {
        require(to != address(0), "Cannot mint to zero address");
        require(bytes(trackId).length > 0, "Track ID cannot be empty");
        require(_trackToToken[trackId] == 0, "Track already minted");
        require(royaltyPercentage <= 10000, "Royalty too high");
        
        // Get next token ID
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        // Mint NFT
        _safeMint(to, tokenId);
        
        // Set metadata URI
        _setTokenURI(tokenId, metadataURI);
        
        // Set royalty (if > 0)
        if (royaltyPercentage > 0) {
            _setTokenRoyalty(tokenId, to, royaltyPercentage);
        }
        
        // Store track mapping
        _trackIds[tokenId] = trackId;
        _trackToToken[trackId] = tokenId;
        _mintTimestamps[tokenId] = block.timestamp;
        
        emit TrackMinted(tokenId, trackId, to, metadataURI, royaltyPercentage);
        
        return tokenId;
    }
    
    /**
     * @dev Mint NFT with default 10% royalty
     */
    function mintTrack(
        address to,
        string memory trackId,
        string memory metadataURI
    ) public onlyOwner returns (uint256) {
        return mintTrack(to, trackId, metadataURI, 1000); // 10% default
    }
    
    /**
     * @dev Get track ID for token
     */
    function getTrackId(uint256 tokenId) public view returns (string memory) {
        require(_exists(tokenId), "Token does not exist");
        return _trackIds[tokenId];
    }
    
    /**
     * @dev Get token ID for track
     */
    function getTokenId(string memory trackId) public view returns (uint256) {
        uint256 tokenId = _trackToToken[trackId];
        require(tokenId != 0, "Track not minted");
        return tokenId;
    }
    
    /**
     * @dev Get mint timestamp for token
     */
    function getMintTimestamp(uint256 tokenId) public view returns (uint256) {
        require(_exists(tokenId), "Token does not exist");
        return _mintTimestamps[tokenId];
    }
    
    /**
     * @dev Check if track is minted
     */
    function isTrackMinted(string memory trackId) public view returns (bool) {
        return _trackToToken[trackId] != 0;
    }
    
    /**
     * @dev Get total number of minted tracks
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current() - 1;
    }
    
    /**
     * @dev Override transfer to emit custom event
     */
    function _transfer(
        address from,
        address to,
        uint256 tokenId
    ) internal override {
        super._transfer(from, to, tokenId);
        emit TrackTransferred(tokenId, from, to);
    }
    
    /**
     * @dev Override to support both URIStorage and Royalty
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    /**
     * @dev Override to support both URIStorage and Royalty
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, ERC721Royalty)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
    /**
     * @dev Internal function to check if token exists
     */
    function _exists(uint256 tokenId) internal view returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }
    
    /**
     * @dev Override _burn to support both URIStorage and Royalty
     */
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage, ERC721Royalty) {
        super._burn(tokenId);
        
        // Clean up track mapping
        string memory trackId = _trackIds[tokenId];
        delete _trackIds[tokenId];
        delete _trackToToken[trackId];
        delete _mintTimestamps[tokenId];
    }
    
    /**
     * @dev Burn token (only owner can burn their own tokens)
     */
    function burn(uint256 tokenId) public {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        _burn(tokenId);
    }
}
