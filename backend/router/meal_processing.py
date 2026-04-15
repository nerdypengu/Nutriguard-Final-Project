"""
Chat-based meal processing endpoints
Handles job creation and status tracking for nutrition analysis
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Query, Depends
from typing import Optional
import httpx
from core.config import N8N_WEBHOOK_URL
from core.security import get_current_user, TokenData
from models.meal_processing import (
    ChatMessageRequest,
    ChatMessageResponse,
    MealProcessingJobResponse,
    JobProgressUpdate,
    N8NWebhookPayload
)
from services.meal_processing import MealProcessingJobService


router = APIRouter(
    prefix="/api/meal-processing",
    tags=["meal_processing"],
    responses={404: {"description": "Not found"}},
)


async def trigger_n8n_webhook(job_id: str, user_id: str, message: str):
    """
    Background task to trigger n8n webhook asynchronously
    
    Args:
        job_id: Meal processing job ID
        user_id: User ID
        message: Chat message
    """
    try:
        payload = N8NWebhookPayload(
            job_id=job_id,
            user_id=user_id,
            message=message
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload.model_dump(),
                timeout=30.0
            )
            response.raise_for_status()

    except httpx.RequestError as e:
        print(f"Error triggering n8n webhook for job {job_id}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in n8n webhook trigger: {str(e)}")


@router.post("/chat", response_model=ChatMessageResponse)
async def create_meal_processing_job(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a meal processing job from chat message
    
    - Requires authentication (JWT token in Authorization header)
    - user_id must match the authenticated user
    - Saves job to database with PENDING status
    - Triggers n8n webhook asynchronously with message content
    - Returns job_id immediately for polling
    
    Example:
        POST /api/meal-processing/chat
        Headers: Authorization: Bearer <jwt_token>
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "message": "Berapa kalori dalam 100g ayam goreng?"
        }
    """
    try:
        # Verify the user_id matches the authenticated user
        if request.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create jobs for other users"
            )
        
        # Create job in database with PENDING status
        job_data = await MealProcessingJobService.create_job(
            user_id=request.user_id,
            progress_message="Pesanan diterima, koki mulai bekerja...",
            content=request.message
        )

        job_id = str(job_data["id"])

        # Trigger n8n webhook asynchronously
        if N8N_WEBHOOK_URL:
            background_tasks.add_task(
                trigger_n8n_webhook,
                job_id,
                request.user_id,
                request.message
            )

        return ChatMessageResponse(
            job_id=job_id,
            status="PENDING",
            message="Job queued for processing"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating meal processing job: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=MealProcessingJobResponse)
async def get_job_status(
    job_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get current status of a meal processing job
    
    - Requires authentication (JWT token in Authorization header)
    - Only allows access to own jobs
    - Retrieves job from database by ID
    - Returns full job data for frontend polling
    - Frontend can check status and result periodically
    
    Example:
        GET /api/meal-processing/status/550e8400-e29b-41d4-a716-446655440000
        Headers: Authorization: Bearer <jwt_token>
    """
    try:
        job_data = await MealProcessingJobService.get_job(job_id)

        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        # Verify the job belongs to the current user
        if job_data.get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access jobs from other users"
            )

        return MealProcessingJobResponse(**job_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job status: {str(e)}"
        )


@router.get("/jobs", response_model=dict)
async def get_user_jobs(
    limit: int = 50,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all meal processing jobs for the authenticated user
    
    - Requires authentication (JWT token in Authorization header)
    - Only returns jobs for the currently logged-in user
    - Optional status filter (PENDING, PROCESSING, COMPLETED, FAILED)
    - Ordered by newest first
    - Useful for user history/dashboard
    
    Example:
        GET /api/meal-processing/jobs?limit=20&status=COMPLETED
        Headers: Authorization: Bearer <jwt_token>
    """
    try:
        jobs = await MealProcessingJobService.get_user_jobs(
            user_id=current_user.user_id,
            limit=limit,
            status_filter=status_filter
        )

        return {
            "user_id": current_user.user_id,
            "total": len(jobs),
            "jobs": jobs
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user jobs: {str(e)}"
        )


@router.put("/progress", response_model=MealProcessingJobResponse)
@router.patch("/progress", response_model=MealProcessingJobResponse)
async def update_job_progress(request: JobProgressUpdate):
    """
    Update job progress from n8n workflow
    
    NO AUTHENTICATION REQUIRED - called by n8n webhook
    
    Called by n8n to update job status during processing.
    
    Request fields:
    - job_id (required): Job ID (UUID)
    - status (required): PROCESSING, COMPLETED, FAILED, or CANCELLED
    - progress_message (optional): Current progress text to show user
    - result (optional): Final processing result as JSON object
    
    Example - During processing:
        PATCH /api/meal-processing/progress
        {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "PROCESSING",
            "progress_message": "Menganalisis nutrisi..."
        }
        
    Example - When complete with result:
        {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "COMPLETED",
            "progress_message": "Analisis selesai",
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
            }
        }
        
    Example - On error:
        {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "FAILED",
            "progress_message": "Error: Invalid food item"
        }
    """
    try:
        job_data = await MealProcessingJobService.update_job_status(
            job_id=request.job_id,
            status=request.status,
            progress_message=request.progress_message,
            result=request.result
        )

        return MealProcessingJobResponse(**job_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job progress: {str(e)}"
        )
