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
    
    # Default Multi-tenant settings
    DEFAULT_TENANT: str = os.getenv("DEFAULT_TENANT", "nexus_corp")
    
    @classmethod
    def get_graph_name(cls, tenant_id: str, graph_type: str = "brain") -> str:
        """
        Generates FalkorDB graph names using multi-graph topology.
        e.g. tenant_nexus_corp_brain, tenant_nexus_corp_memory
        """
        clean_tenant = tenant_id.strip().lower().replace("-", "_")
        return f"tenant_{clean_tenant}_{graph_type}"

settings = Settings()
