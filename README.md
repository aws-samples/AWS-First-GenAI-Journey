# AWS First GenAI Journey

A comprehensive collection of Generative AI projects powered by Amazon Bedrock, showcasing diverse applications across industries. This repository contains ready-to-deploy solutions for various use cases, from translation and education to financial analysis and HR management.

> ⚠️ **Security Notice**: These are sample/demo applications intended for learning and experimentation. Before deploying to production, please implement additional security measures including: input validation and rate limiting, [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) for prompt injection defense, PII detection and redaction for sensitive data, proper authentication and authorization, and data encryption at rest and in transit. See the `shared/security_utils.py` module for basic input sanitization utilities included in this repo.

## Projects Overview 

### Text and Language Processing
1. **AWS-AI-Powered-Translation-Assistant**
   - Real-time, multi-language translation with contextual awareness
   - Built with Amazon Bedrock, LLMs, and Streamlit frontend

2. **AWS-Educational-Assistant**
   - AI-powered educational support system
   - Generates summaries, explanations, and study plans
   - Uses Claude model on Amazon Bedrock with Streamlit interface

3. **Claude Wisdom AI**
   - Knowledge extraction and summarization tool
   - Processes large texts to extract key insights
   - Powered by Claude model on Amazon Bedrock

### Financial Applications
4. **AWS-GenAI-Market-Sage**
   - Financial market insights generator
   - Real-time data integration for market analysis
   - Combines Bedrock with financial APIs

5. **AWS-Stock-Agent-with-Bedrock**
   - Real-time stock analysis and recommendations
   - Provides market trends and stock insights
   - Integrates with stock APIs for live data

### HR and Career Tools
6. **CV-Maestro-Elevate-Your-Career-Narrative**
   - Smart CV content generator
   - Optimizes resumes based on job descriptions
   - Uses LLM for content generation

7. **HR-Luminary-with-Amazon-Bedrock**
   - Comprehensive HR assistant
   - Handles resume screening and performance analysis
   - Features HR-optimized LLM and dashboard

8. **GenAI-HR-Luminary**
   - Specialized HR analysis tool
   - Focuses on employee evaluations and hiring insights
   - Built with HR-specific LLM models

### Image Processing and Generation
9. **AWS-First-Cloud-Journey-Uniform-Detection**
   - AI-powered uniform detection system
   - Uses image processing and analysis
   - Built on Bedrock's image analysis capabilities

10. **Generate Images using Amazon Bedrock**
    - Text-to-image generation using Stability Diffusion
    - Creates custom images from text prompts
    - Features Streamlit-based UI

11. **Stable Diffusion UI for Text-to-Image**
    - User-friendly interface for image generation
    - Built on Stability Diffusion model
    - Includes input prompting and image display

### Document and Content Processing
12. **OCR-GenAI**
    - Advanced OCR assistant with GenAI capabilities
    - Extracts text from documents and images
    - Features user-friendly upload interface

13. **AWS-OCR-with-Amazon-Bedrock**
    - Specialized OCR implementation
    - Optimized for document text extraction
    - Includes document processing pipeline

14. **Content-Moderation-with-Amazon-Bedrock**
    - AI-powered content moderation system
    - Reviews text and images for compliance
    - Features moderation dashboard

### Multi-Modal and Specialized Applications
15. **PolyClaude**
    - Multi-modal AI assistant
    - Handles text and image analysis
    - Built on Claude model with Streamlit frontend

16. **Product-Description-Generator**
    - Automated product description creation
    - Uses LLM for feature-based content generation
    - Includes product input form

17. **Location-Analysis-System**
    - Geospatial data analysis tool
    - Provides demographic and business insights
    - Features location data visualization

18. **TapVision**
    - Customer sentiment analysis system
    - Extracts insights from feedback
    - Includes sentiment visualization dashboard

19. **Amazon-Bedrock-Claude3-Image-Analysis**
    - Advanced image analysis with Claude3
    - Extracts context and details from images
    - Features comprehensive analysis dashboard

20. **GenAI-Model-Evaluator**
    - Model performance evaluation tool
    - Benchmarks various GenAI models
    - Includes detailed metrics and comparisons

## Additional Components

21. **QnABot-Conversational-AI**
    - Conversational AI implementation with Amazon Lex
    - Features Alexa integration capabilities

22. **Slack-gateway-for-Amazon-Q-Business**
    - Business integration tool for Slack
    - Connects with Amazon Q services

23. **Amazon-Bedrock-All-Text-Generator**
    - Comprehensive text generation utility
    - Supports multiple use cases and formats

24. **Amazon-Bedrock-Model-Evaluator**
    - Advanced model evaluation framework
    - Includes performance metrics and analytics

## Setup and Installation

Each project includes detailed setup instructions in its respective directory. Generally, projects require:
1. Amazon Bedrock access and configuration
2. Relevant API keys and permissions
3. Python environment setup
4. Frontend deployment (where applicable)

## Security

This repo includes a `shared/security_utils.py` module with:
- **Input sanitization** — escapes prompt-breaking XML tags, enforces length limits
- **Prompt injection detection** — regex-based pattern matching
- **Amazon Bedrock Guardrails integration** — `BedrockGuardrail` class wrapping the ApplyGuardrail API for content filtering, prompt attack detection, and PII protection

To enable Bedrock Guardrails, set `BEDROCK_GUARDRAIL_ID` environment variable. See the [Educational-Assistant](AWS-Educational-Assistant/) for a working integration example.

**References:**
- [OWASP Top 10 for LLM & Agentic Applications (2026)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Amazon Bedrock AgentCore Security](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-security/introduction.html)
- [AWS Security Reference Architecture – AI Security (Feb 2026)](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture-generative-ai/introduction.html)

See also [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for reporting security issues.


# Contributors
[![contributors](https://contrib.rocks/image?repo=aws-samples/AWS-First-GenAI-Journey&max=2000)](https://github.com/aws-samples/AWS-First-GenAI-Journey/graphs/contributors)

## License

This project is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file for details.
