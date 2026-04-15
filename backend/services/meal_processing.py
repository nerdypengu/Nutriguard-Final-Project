"""
Services for meal processing job operations
Handles all database operations for meal processing jobs
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from core.supabase import supabase_service_client
from models.meal_processing import JobStatus, MealProcessingJobResponse


class MealProcessingJobService:
    """Service for meal processing job operations"""

    @staticmethod
    async def create_job(
        user_id: str,
        progress_message: str = "Memulai proses...",
        content: str = None
    ) -> Dict[str, Any]:
        """
        Create a new meal processing job
        
        Args:
            user_id: User ID (UUID)
            progress_message: Initial progress message
            content: User's question/message content
            
        Returns:
            Created job data with id
            
        Raises:
            Exception: If database operation fails
        """
        try:
            job_data = {
                "user_id": user_id,
                "status": JobStatus.PENDING.value,
                "progress_message": progress_message,
                "result": None
            }
            
            if content is not None:
                job_data["content"] = content

            response = supabase_service_client.schema("nutriguard").table("meal_processing_jobs") \
                .insert(job_data) \
                .execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("Failed to create job in database")

        except Exception as e:
            raise Exception(f"Error creating meal processing job: {str(e)}")

    @staticmethod
    async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a meal processing job by ID
        
        Args:
            job_id: Job ID (UUID)
            
        Returns:
            Job data or None if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            response = supabase_service_client.schema("nutriguard").table("meal_processing_jobs") \
                .select("*") \
                .eq("id", job_id) \
                .single() \
                .execute()

            return response.data if response.data else None

        except Exception as e:
            if "0 rows" in str(e).lower() or "not found" in str(e).lower():
                return None
            raise Exception(f"Error retrieving meal processing job: {str(e)}")

    @staticmethod
    async def update_job_status(
        job_id: str,
        status: str,
        progress_message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update job status and optional fields
        
        Args:
            job_id: Job ID (UUID)
            status: New status (PENDING, PROCESSING, COMPLETED, FAILED)
            progress_message: Optional progress message
            result: Optional processing result
            
        Returns:
            Updated job data
            
        Raises:
            Exception: If database operation fails
        """
        try:
            update_data = {
                "status": status,
                "updated_at": "NOW()"
            }

            if progress_message is not None:
                update_data["progress_message"] = progress_message

            if result is not None:
                update_data["result"] = result

            response = supabase_service_client.schema("nutriguard").table("meal_processing_jobs") \
                .update(update_data) \
                .eq("id", job_id) \
                .execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("Failed to update job in database")

        except Exception as e:
            raise Exception(f"Error updating meal processing job: {str(e)}")

    @staticmethod
    async def get_user_jobs(
        user_id: str,
        limit: int = 50,
        status_filter: Optional[str] = None
    ) -> list:
        """
        Get all jobs for a user with optional status filter
        
        Args:
            user_id: User ID
            limit: Maximum number of jobs to retrieve
            status_filter: Optional status filter
            
        Returns:
            List of jobs
            
        Raises:
            Exception: If database operation fails
        """
        try:
            query = supabase_service_client.schema("nutriguard").table("meal_processing_jobs") \
                .select("*") \
                .eq("user_id", user_id)

            if status_filter:
                query = query.eq("status", status_filter)

            response = query.order("created_at", desc=True) \
                .limit(limit) \
                .execute()

            return response.data if response.data else []

        except Exception as e:
            raise Exception(f"Error retrieving user jobs: {str(e)}")
