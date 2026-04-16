"""
Models for meal processing job tracking
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ChatMessageRequest(BaseModel):
    """Request model for chat message"""
    user_id: str = Field(..., description="User ID (UUID) - must match authenticated user", min_length=1)
    message: str = Field(..., description="Chat message from user", min_length=1, max_length=5000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Berapa kalori dalam 100g ayam goreng?"
            }
        }




class ChatMessageResponse(BaseModel):
    """Response model for chat message"""
    job_id: str = Field(..., description="Job ID for tracking")
    status: str = Field(..., description="Initial status (PENDING)")
    message: str = Field(default="Job queued for processing", description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PENDING",
                "message": "Job queued for processing"
            }
        }


class MealProcessingJobResponse(BaseModel):
    """Response model for job status"""
    id: str = Field(..., description="Job ID")
    user_id: str = Field(..., description="User ID (UUID)")
    status: str = Field(..., description="Job status")
    progress_message: str = Field(..., description="Current progress message")
    content: Optional[str] = Field(None, description="User's question/message content")
    result: Optional[Dict[str, Any]] = Field(None, description="Processing result (JSONB)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "status": "COMPLETED",
                "progress_message": "Analisis selesai",
                "content": "Berapa kalori dalam 100g ayam goreng?",
                "result": {
                    "food_items": [
                        {
                            "name": "Ayam Goreng",
                            "quantity": "100g",
                            "calories": 250,
                            "protein": 25,
                            "fat": 15,
                            "carbs": 0
                        }
                    ],
                    "total_calories": 250
                },
                "created_at": "2026-04-09T12:00:00+07:00",
                "updated_at": "2026-04-09T12:05:00+07:00"
            }
        }


class JobProgressUpdate(BaseModel):
    """Request model to update job progress from n8n"""
    job_id: str = Field(..., description="Job ID (UUID)")
    status: str = Field(..., description="New status (PROCESSING, COMPLETED, FAILED)")
    progress_message: Optional[str] = Field(None, description="Progress message")
    result: Optional[Dict[str, Any]] = Field(None, description="Processing result (JSONB)")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PROCESSING",
                "progress_message": "Menganalisis nutrisi...",
                "result": None
            }
        }


class N8NWebhookPayload(BaseModel):
    """Payload to send to n8n webhook"""
    job_id: str
    user_id: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-123",
                "message": "Berapa kalori dalam 100g ayam goreng?"
            }
        }
