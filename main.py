from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import Dict
from mangum import Mangum
import hashlib


app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortening service",
    version="1.0.1"
)

# In-memory storage
url_store: Dict[str, str] = {}  # Maps short_code -> original_url
url_to_code: Dict[str, str] = {}  # Reverse lookup: original_url -> short_code


class URLEncodeRequest(BaseModel):
    url: HttpUrl


class URLEncodeResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str


class URLDecodeResponse(BaseModel):
    original_url: str


def generate_short_code(url: str) -> str:
    """
    Generate a short code from a URL using hash-based approach.
    Takes first 7 characters of SHA256 hash for a good balance of brevity and collision resistance.
    """
    hash_object = hashlib.sha256(url.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex[:7]


@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    """Health check endpoint."""
    return {"message": "URL Shortener API is running"}


@app.post("/encode", response_model=URLEncodeResponse, status_code=status.HTTP_201_CREATED)
async def encode_url(request: URLEncodeRequest) -> URLEncodeResponse:
    """
    Encode a long URL into a shortened version.

    Args:
        request: URLEncodeRequest containing the URL to shorten

    Returns:
        URLEncodeResponse with the short code and URLs
    """
    url_str = str(request.url)

    # Check if URL already exists in store using O(1) lookup
    if url_str in url_to_code:
        short_code = url_to_code[url_str]
        return URLEncodeResponse(
            short_code=short_code,
            short_url=f"/{short_code}",
            original_url=url_str
        )

    # Generate new short code
    short_code = generate_short_code(url_str)

    # Handle potential collision (very rare with 7 char hash)
    counter = 0
    original_short_code = short_code
    while short_code in url_store and url_store[short_code] != url_str:
        counter += 1
        short_code = f"{original_short_code}{counter}"

    # Store the mapping in both dictionaries
    url_store[short_code] = url_str
    url_to_code[url_str] = short_code

    return URLEncodeResponse(
        short_code=short_code,
        short_url=f"/{short_code}",
        original_url=url_str
    )


@app.get("/{short_code}", response_model=URLDecodeResponse, status_code=status.HTTP_200_OK)
async def get_url(short_code: str) -> URLDecodeResponse:
    """
    Retrieve the original URL from a short code.

    Args:
        short_code: The shortened URL code

    Returns:
        URLDecodeResponse with the original URL

    Raises:
        HTTPException: 404 if short code not found
    """
    if short_code not in url_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found"
        )

    original_url = url_store[short_code]

    return URLDecodeResponse(original_url=original_url)


# AWS Lambda handler
handler = Mangum(app)
