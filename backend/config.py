import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "FalkorNexus"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "Autonomous Enterprise Brain & Multi-Agent Operations Command powered by FalkorDB"
    
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # FalkorDB settings
    FALKORDB_HOST: str = os.getenv("FALKORDB_HOST", "localhost")
    FALKORDB_PORT: int = int(os.getenv("FALKORDB_PORT", "6379"))
    FALKORDB_PASSWORD: str = os.getenv("FALKORDB_PASSWORD", "")
    FALKORDB_URL: str = os.getenv("FALKORDB_URL", "")
    
    # LLM Settings (OpenAI / Ollama / Gemini / LiteLLM)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Default Multi-tenant settings
    DEFAULT_TENANT: str = os.getenv("DEFAULT_TENANT", "nexus_corp")
    
    @classmethod
    def get_graph_name(cls, tenant_id: str, graph_type: str = "brain") -> str:
        clean_tenant = tenant_id.strip().lower().replace("-", "_")
        return f"tenant_{clean_tenant}_{graph_type}"

settings = Settings()
