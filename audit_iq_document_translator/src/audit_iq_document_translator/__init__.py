"""
AuditIQ Document Translator Tool

A CrewAI tool for translating documents while preserving formatting using Azure AI Document Translation.
"""

from .tool import AuditIqDocumentTranslator

__version__ = "1.0.1"
__all__ = ["AuditIqDocumentTranslator"]