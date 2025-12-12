"""
OpenAI Service - GPT-powered prompt enhancement and analysis
"""
import openai
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")


async def enhance_prompt(
    user_input: str,
    style: Optional[str] = None,
    mood: Optional[str] = None,
    tempo: Optional[int] = None,
    instruments: Optional[List[str]] = None
) -> Dict:
    """
    Transform user's simple prompt into detailed music production prompt
    """
    try:
        # Build enhancement system prompt
        system_prompt = """You are an expert music producer and prompt engineer for AI music generation.
        Transform user's simple music ideas into detailed, production-ready prompts that include:
        - Genre and sub-genre
        - Tempo (BPM)
        - Musical key
        - Mood and emotion
        - Instrumentation
        - Song structure
        - Production style
        
        Return a JSON object with these fields:
        - enhanced_prompt: detailed prompt text
        - genre: primary genre
        - mood: emotional tone
        - tempo: BPM (integer)
        - key: musical key
        - structure: song structure (e.g., "Intro-Verse-Chorus-Verse-Chorus-Bridge-Chorus")
        - confidence_score: 0-1 float indicating how well-defined the input was
        """
        
        # Build user message with context
        user_message = f"User input: {user_input}\n"
        if style:
            user_message += f"Preferred style: {style}\n"
        if mood:
            user_message += f"Desired mood: {mood}\n"
        if tempo:
            user_message += f"Target tempo: {tempo} BPM\n"
        if instruments:
            user_message += f"Preferred instruments: {', '.join(instruments)}\n"
        
        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=800
        )
        
        result = response.choices[0].message.content
        
        import json
        enhanced_data = json.loads(result)
        
        logger.info(f"Enhanced prompt: {enhanced_data.get('enhanced_prompt')}")
        
        return enhanced_data
    
    except Exception as e:
        logger.error(f"Prompt enhancement failed: {e}")
        raise


async def analyze_genre(prompt: str) -> Dict:
    """
    Analyze a prompt to extract musical characteristics
    """
    try:
        system_prompt = """Analyze this music prompt and extract:
        - Primary genre
        - Sub-genres (list)
        - Suggested tempo range
        - Suggested key
        - Instrumentation
        - Mood/emotion
        - Target audience
        - Commercial viability (0-10 score)
        
        Return as JSON.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        import json
        analysis = json.loads(response.choices[0].message.content)
        
        return analysis
    
    except Exception as e:
        logger.error(f"Genre analysis failed: {e}")
        raise


async def generate_lyrics(
    theme: str,
    style: str = "pop",
    structure: str = "verse-chorus-verse-chorus-bridge-chorus",
    length: str = "medium"
) -> str:
    """
    Generate song lyrics based on theme and style
    """
    try:
        system_prompt = f"""You are a professional songwriter. Generate lyrics for a {style} song.
        Structure: {structure}
        Length: {length}
        
        Follow these guidelines:
        - Create compelling, radio-ready lyrics
        - Use modern, relatable language
        - Include proper verse/chorus/bridge markers
        - Match the genre style and conventions
        """
        
        user_prompt = f"Write lyrics about: {theme}"
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        lyrics = response.choices[0].message.content
        
        return lyrics
    
    except Exception as e:
        logger.error(f"Lyric generation failed: {e}")
        raise
