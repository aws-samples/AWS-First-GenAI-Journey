#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import base64
import os
import json
from typing import List, Dict, Any, Optional
import boto3
from langchain_aws import ChatBedrock as BedrockChat
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import CallbackManager
from langchain_core.outputs import ChatGenerationChunk

class ClaudeOCRProcessor:
    """Handles OCR processing using Claude 3.5 Sonnet"""
    
    DEFAULT_MODEL = 'anthropic.claude-sonnet-4-6'
    
    def __init__(
        self,
        model_id: Optional[str] = None,
        region_name: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0,
        top_p: float = 0.999,
        top_k: int = 250
    ):
        """
        Initialize the OCR processor with custom settings
        
        Args:
            model_id: Claude model identifier
            region_name: AWS region name
            max_tokens: Maximum tokens in response
            temperature: Model temperature (0-1)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
        """
        self.model_id = model_id or os.environ.get('MODEL_ID', self.DEFAULT_MODEL)
        self.region_name = region_name or boto3.Session().region_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.llm = self._build_chain()

    def _build_chain(self) -> BedrockChat:
        """
        Build the Claude chain with specified parameters
        
        Returns:
            BedrockChat: Configured Claude chat instance
        """
        try:
            llm = BedrockChat(
                model_id=self.model_id,
                model_kwargs={
                    'max_tokens': self.max_tokens,
                    'temperature': self.temperature,
                    'top_p': self.top_p,
                    'top_k': self.top_k,
                },
                region_name=self.region_name,
                streaming=True,
                callback_manager=CallbackManager([])
            )
            return llm
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Claude: {str(e)}")

    def process_image(
        self,
        image_data: str,
        mode: str = "general",
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Process an image and extract text based on specified mode
        
        Args:
            image_data: Base64 encoded image data
            mode: Processing mode ("general", "document", "id_card")
            language: Target language for extraction
            
        Returns:
            Dict containing extracted text and metadata
        """
        prompts = {
            "general": "Extract all text from the image and separate each line with a newline character.",
            "document": """Analyze this document and extract:
                1. All text content with proper formatting
                2. Key fields and their values
                3. Any tables or structured data
                Return the results in a structured format.""",
            "id_card": """Analyze this ID card and extract:
                1. Document type
                2. ID number
                3. Personal information (name, DOB, gender)
                4. Address information
                5. Validity dates
                Return the results in a structured JSON format."""
        }
        
        # Select appropriate prompt
        prompt = prompts.get(mode, prompts["general"])
        if language != "auto":
            prompt += f"\nPlease extract text in {language}."
        
        try:
            messages = [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                )
            ]
            
            # Process image with streaming support
            response_chunks = []
            for chunk in self.llm.stream(messages):
                if isinstance(chunk, ChatGenerationChunk):
                    response_chunks.append(chunk.text)
            
            full_response = "".join(response_chunks)
            
            # Try to parse as JSON if structured response
            try:
                if mode in ["document", "id_card"]:
                    extracted_data = json.loads(full_response)
                else:
                    extracted_data = {"text": full_response}
            except json.JSONDecodeError:
                extracted_data = {"text": full_response}
            
            return {
                "status": "success",
                "mode": mode,
                "language": language,
                "data": extracted_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "mode": mode,
                "language": language,
                "error": str(e)
            }

    @staticmethod
    def encode_image(image_path: str) -> str:
        """
        Encode an image file to base64
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise IOError(f"Failed to encode image: {str(e)}")

def main():
    """CLI interface for testing"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude 3.5 Sonnet OCR Processor")
    parser.add_argument("image_path", help="Path to image file")
    parser.add_argument("--mode", choices=["general", "document", "id_card"],
                      default="general", help="Processing mode")
    parser.add_argument("--language", default="auto", help="Target language")
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = ClaudeOCRProcessor()
        
        # Encode image
        base64_image = processor.encode_image(args.image_path)
        
        # Process image
        result = processor.process_image(
            base64_image,
            mode=args.mode,
            language=args.language
        )
        
        # Print results
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()