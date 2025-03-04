from fastapi import FastAPI, HTTPException
from database import QdrantDB
from models import Document, SearchQuery, UpdateDocument

app = FastAPI(title="Document Search API")
db = QdrantDB()


@app.post("/documents/", response_model=Document)
async def create_document(document: Document):
    """Create a new document"""
    if document.id is None:
        # In a real application, you'd want a better ID generation strategy
        document.id = hash(document.title + document.content) % 10000000

    success = db.add_document(
        id=document.id,
        title=document.title,
        content=document.content,
        category=document.category,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create document")
    return document


@app.post("/search/")
async def search_documents(query: SearchQuery):
    """Search for similar documents"""
    results = db.search_documents(query.text, query.limit)
    return results


@app.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document"""
    success = db.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}


@app.patch("/documents/{document_id}")
async def update_document(document_id: int, update_data: UpdateDocument):
    """Update a document"""
    success = db.update_document(
        id=document_id,
        title=update_data.title,
        content=update_data.content,
        category=update_data.category,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document updated successfully"}
