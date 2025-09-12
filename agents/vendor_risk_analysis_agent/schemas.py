"""Pydantic schemas for structured agent outputs."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchQuestion(BaseModel):
    """Schema for a research question with answer and reasoning."""
    
    question: str = Field(
        description="The original question text"
    )
    answer: str = Field(
        description="The synthesized answer based on research"
    )
    reasoning: str = Field(
        description="Detailed reasoning with inline citations"
    )


class ResearchCategory(BaseModel):
    """Schema for a category of research questions."""
    
    name: str = Field(
        description="The name of the category (e.g., 'Security', 'Compliance')"
    )
    questions: List[ResearchQuestion] = Field(
        description="List of questions and answers in this category"
    )


class Reference(BaseModel):
    """Schema for a reference citation."""
    
    id: int = Field(
        description="The reference number used in citations"
    )
    title: str = Field(
        description="The title of the reference source"
    )
    url: str = Field(
        description="The full URL of the reference source"
    )
    is_valid: Optional[bool] = Field(
        None, 
        description="Whether the URL has been validated as accessible"
    )


class ResearchOutput(BaseModel):
    """Schema for the complete research output."""
    
    vendor_name: str = Field(
        description="The name of the vendor being researched"
    )
    vendor_url: str = Field(
        description="The URL of the vendor's website"
    )
    categories: List[ResearchCategory] = Field(
        description="List of research categories with their questions and answers"
    )
    summary: str = Field(
        description="A brief summary of key findings across all questions"
    )
    references: List[Reference] = Field(
        description="List of all references cited in the research"
    )
