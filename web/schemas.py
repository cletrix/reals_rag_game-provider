"""
Pydantic schemas para validação e documentação da API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# --- Settings Schemas ---

class SettingsResponse(BaseModel):
    """Resposta com todas as configurações do sistema"""
    llm_provider: str = Field(description="Provider de LLM: 'groq' ou 'ollama'")
    groq_model: Optional[str] = Field(default=None, description="Modelo Groq configurado")
    ollama_model: Optional[str] = Field(default=None, description="Modelo Ollama configurado")
    similarity_top_k: str = Field(default="2", description="Número de documentos similares a retornar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "llm_provider": "ollama",
                "groq_model": None,
                "ollama_model": "qwen2.5:7b-instruct",
                "similarity_top_k": "2"
            }
        }
    )


class SettingsUpdate(BaseModel):
    """Schema para atualização de configurações"""
    llm_provider: Optional[str] = Field(default=None, description="Provider de LLM: 'groq' ou 'ollama'")
    groq_model: Optional[str] = Field(default=None, description="Modelo Groq configurado")
    ollama_model: Optional[str] = Field(default=None, description="Modelo Ollama configurado")
    similarity_top_k: Optional[str] = Field(default=None, description="Número de documentos similares a retornar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "llm_provider": "ollama",
                "ollama_model": "qwen2.5:7b-instruct",
                "similarity_top_k": "3"
            }
        }
    )


# --- Query/History Schemas ---

class Source(BaseModel):
    """Fonte de documento recuperado"""
    file: str = Field(description="Nome do arquivo")
    page: str = Field(default="", description="Número da página ou seção")
    score: float = Field(description="Score de similaridade (0-1)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file": "documento.md",
                "page": "1",
                "score": 0.85
            }
        }
    )


class QueryResponse(BaseModel):
    """Resposta de uma query individual"""
    id: str = Field(description="ID único da query")
    question: str = Field(description="Pergunta feita")
    answer_preview: str = Field(description="Preview da resposta (primeiros 120 caracteres)")
    elapsed_ms: Optional[int] = Field(default=None, description="Tempo de execução em milissegundos")
    llm_provider: str = Field(description="Provider de LLM utilizado")
    llm_model: Optional[str] = Field(default=None, description="Modelo de LLM utilizado")
    created_at: str = Field(description="Timestamp de criação (ISO 8601)")
    conversation_id: Optional[str] = Field(default=None, description="ID da conversa associada")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "question": "Como funciona o sistema?",
                "answer_preview": "O sistema utiliza RAG para responder perguntas...",
                "elapsed_ms": 1500,
                "llm_provider": "ollama",
                "llm_model": "qwen2.5:7b-instruct",
                "created_at": "2026-05-20T18:00:00+00:00",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }
    )


class QueryDetail(BaseModel):
    """Detalhes completos de uma query"""
    id: str = Field(description="ID único da query")
    question: str = Field(description="Pergunta feita")
    answer: str = Field(description="Resposta completa")
    sources: List[Source] = Field(default_factory=list, description="Lista de fontes utilizadas")
    elapsed_ms: Optional[int] = Field(default=None, description="Tempo de execução em milissegundos")
    llm_provider: str = Field(description="Provider de LLM utilizado")
    llm_model: Optional[str] = Field(default=None, description="Modelo de LLM utilizado")
    tokens_total: Optional[int] = Field(default=None, description="Total de tokens utilizados")
    created_at: str = Field(description="Timestamp de criação (ISO 8601)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "question": "Como funciona o sistema?",
                "answer": "O sistema utiliza RAG para responder perguntas baseadas em documentos indexados...",
                "sources": [
                    {"file": "documento.md", "page": "1", "score": 0.85}
                ],
                "elapsed_ms": 1500,
                "llm_provider": "ollama",
                "llm_model": "qwen2.5:7b-instruct",
                "tokens_total": 500,
                "created_at": "2026-05-20T18:00:00+00:00"
            }
        }
    )


# --- Stats Schemas ---

class StatsResponse(BaseModel):
    """Estatísticas do sistema"""
    total_queries: int = Field(description="Total de queries realizadas")
    total_tokens: int = Field(description="Total de tokens consumidos")
    groq_api_usage: Optional[str] = Field(default=None, description="Uso da API Groq (se aplicável)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_queries": 150,
                "total_tokens": 75000,
                "groq_api_usage": None
            }
        }
    )


# --- Conversation Schemas ---

class ConversationResponse(BaseModel):
    """Resposta de uma conversa"""
    id: str = Field(description="ID único da conversa")
    title: Optional[str] = Field(default=None, description="Título da conversa")
    created_at: str = Field(description="Timestamp de criação (ISO 8601)")
    updated_at: str = Field(description="Timestamp de atualização (ISO 8601)")
    message_count: int = Field(description="Número de mensagens na conversa")
    preview: Optional[str] = Field(default=None, description="Preview da última mensagem")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Como funciona o sistema?",
                "created_at": "2026-05-20T18:00:00+00:00",
                "updated_at": "2026-05-20T18:05:00+00:00",
                "message_count": 3,
                "preview": "Qual o seu nome?"
            }
        }
    )


class ConversationDetail(BaseModel):
    """Detalhes completos de uma conversa"""
    id: str = Field(description="ID único da conversa")
    title: Optional[str] = Field(default=None, description="Título da conversa")
    created_at: str = Field(description="Timestamp de criação (ISO 8601)")
    updated_at: str = Field(description="Timestamp de atualização (ISO 8601)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Como funciona o sistema?",
                "created_at": "2026-05-20T18:00:00+00:00",
                "updated_at": "2026-05-20T18:05:00+00:00"
            }
        }
    )


class ConversationUpdate(BaseModel):
    """Schema para atualização de conversa"""
    title: Optional[str] = Field(default=None, description="Novo título da conversa")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Novo título da conversa"
            }
        }
    )


class MessageResponse(BaseModel):
    """Resposta de uma mensagem (query) dentro de uma conversa"""
    id: str = Field(description="ID único da mensagem")
    question: str = Field(description="Pergunta feita")
    answer: str = Field(description="Resposta completa")
    sources: List[Source] = Field(default_factory=list, description="Lista de fontes utilizadas")
    elapsed_ms: Optional[int] = Field(default=None, description="Tempo de execução em milissegundos")
    llm_provider: str = Field(description="Provider de LLM utilizado")
    llm_model: Optional[str] = Field(default=None, description="Modelo de LLM utilizado")
    tokens_total: Optional[int] = Field(default=None, description="Total de tokens utilizados")
    created_at: str = Field(description="Timestamp de criação (ISO 8601)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "question": "Como funciona o sistema?",
                "answer": "O sistema utiliza RAG para responder perguntas...",
                "sources": [{"file": "documento.md", "page": "1", "score": 0.85}],
                "elapsed_ms": 1500,
                "llm_provider": "ollama",
                "llm_model": "qwen2.5:7b-instruct",
                "tokens_total": 500,
                "created_at": "2026-05-20T18:00:00+00:00"
            }
        }
    )


# --- Chat Request Schema ---

class ChatRequest(BaseModel):
    """Request para endpoint de chat streaming"""
    question: str = Field(..., min_length=1, max_length=10000, description="Pergunta a ser feita")
    conversation_id: Optional[str] = Field(default=None, description="ID da conversa (opcional, cria nova se não fornecido)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "Como funciona o sistema?",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )


# --- Health Check Schemas ---

class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str = Field(description="Status do sistema: 'healthy' ou 'unhealthy'")
    timestamp: str = Field(description="Timestamp do check (ISO 8601)")
    services: Dict[str, str] = Field(description="Status dos serviços dependentes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2026-05-20T18:00:00+00:00",
                "services": {
                    "postgres": "healthy",
                    "qdrant": "healthy",
                    "ollama": "healthy"
                }
            }
        }
    )


# --- Error Schemas ---

class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    error: str = Field(description="Tipo do erro")
    message: str = Field(description="Mensagem detalhada do erro")
    detail: Optional[str] = Field(default=None, description="Detalhes adicionais do erro")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "ValidationError",
                "message": "Invalid input",
                "detail": "question field is required"
            }
        }
    )
