from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="YouTube Transcript API",
    description="API para extrair transcrições de vídeos do YouTube",
    version="1.0.0"
)

class TranscriptRequest(BaseModel):
    video_id: str
    languages: Optional[List[str]] = ["pt", "en"]

@app.get("/")
def read_root():
    return {"message": "YouTube Transcript API Server"}

@app.post("/transcript")
def get_transcript(request: TranscriptRequest):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            request.video_id,
            languages=request.languages
        )
        return {
            "video_id": request.video_id,
            "transcript": transcript
        }
    except TranscriptsDisabled:
        raise HTTPException(
            status_code=404,
            detail="Transcrições estão desabilitadas para este vídeo"
        )
    except NoTranscriptFound:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhuma transcrição encontrada nos idiomas: {request.languages}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/available-transcripts/{video_id}")
def list_transcripts(video_id: str):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_transcripts = []
        
        for transcript in transcript_list:
            available_transcripts.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable,
                "translation_languages": transcript.translation_languages
            })
            
        return {
            "video_id": video_id,
            "available_transcripts": available_transcripts
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
