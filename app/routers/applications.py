from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from schemas import (JobApplicationCreate,
                     JobApplicationResponse, JobApplicationUpdate)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import models
from database import get_db

from auth import CurrentUser

router = APIRouter()

# Route to create a job application


@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_job_application(job: JobApplicationCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_job_application = models.JobApplication(
        user_id=current_user.id,
        company=job.company,
        role=job.role,
        url=job.url,
        location=job.location,
        notes=job.notes
    )
    db.add(new_job_application)
    await db.commit()
    await db.refresh(new_job_application, ["owner"])
    return new_job_application


# Route to get all job applications


@router.get("", name="job_applications", response_model=list[JobApplicationResponse])
async def get_job_applications(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.JobApplication).where(models.JobApplication.user_id == current_user.id).options(selectinload(models.JobApplication.owner)))
    job_applications = result.scalars().all()
    return list(job_applications)

# Route to get a specific job application based on its id


@router.get("/{job_id}", response_model=JobApplicationResponse)
async def get_job_application(current_user: CurrentUser, job_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.JobApplication).where(models.JobApplication.user_id == current_user.id).options(selectinload(models.JobApplication.owner)).where(models.JobApplication.id == job_id))
    job_application = result.scalars().first()
    if job_application:
        return job_application
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="job application not found")

# Route to update a job application(full)


@router.put("/{job_id}", response_model=JobApplicationResponse)
async def update_job_application_full(job_id: int, current_user: CurrentUser, job_data: JobApplicationCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check if job application exists in db
    result = await db.execute(select(models.JobApplication).options(
        selectinload(models.JobApplication.owner)).where(models.JobApplication.id == job_id))
    job_application = result.scalars().first()
    if not job_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="job application not found")

    if job_application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this job application")

    # Replace the job application
    job_application.company = job_data.company
    job_application.role = job_data.role
    job_application.url = job_data.url
    job_application.location = job_data.location
    job_application.notes = job_data.notes

    await db.commit()
    await db.refresh(job_application, ["owner"])
    return job_application

# Route to update a job application(partial)


@router.patch("/{job_id}", response_model=JobApplicationResponse)
async def update_job_application_partial(job_id: int, current_user: CurrentUser, job_data: JobApplicationUpdate, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check if job application exists in db
    result = await db.execute(select(models.JobApplication).options(selectinload(models.JobApplication.owner)).where(models.JobApplication.id == job_id))
    job_application = result.scalars().first()

    if not job_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="job application not found")

    if job_application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this job application")

    # Update the job application
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_application, field, value)

    await db.commit()
    await db.refresh(job_application,["owner"])
    return job_application

# Route to delete a specific job application based on its id


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_application(job_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.JobApplication).options(
        selectinload(models.JobApplication.owner)).where(models.JobApplication.id == job_id))
    job_application = result.scalars().first()

    # Check if note exists
    if not job_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="job application not found")

    if job_application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this job application")

    await db.delete(job_application)
    await db.commit()
