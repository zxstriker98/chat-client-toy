import hashlib
import os

from database.FileRecord import FileRecord
from database.repository.FileRepository import FileRepository
from services.PageIndexService import PageIndexService


class PageIndexCacheService:
    def __init__(self, repo: FileRepository):
        self.repo = repo

    def compute_hash(self, file_path: str) -> str | None:
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                return hashlib.md5(file_bytes).hexdigest()
        except (FileNotFoundError, PermissionError):
            return None

    def lookup(self, file_path: str) -> str | None:
        file_hash = self.compute_hash(file_path)
        if file_hash is None:
            return None
        record: FileRecord | None = self.repo.get_by_hash(file_hash)
        return record.doc_id if record else None

    def store(self, file_path: str, doc_id: str) -> FileRecord:
        file_hash = self.compute_hash(file_path)
        if file_hash is None:
            raise FileNotFoundError(f"Cannot store: file not found at '{file_path}'")
        record: FileRecord = FileRecord()
        record.doc_id = doc_id
        record.file_hash = file_hash
        record.file_name = os.path.basename(file_path)
        record.file_size = os.path.getsize(file_path)
        record.file_format = record.file_name.rsplit(".", 1)[-1]
        return self.repo.insert(record)

    def get_or_submit(self, pageIndexService: PageIndexService, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: '{file_path}'")
        existing_doc_id: str | None = self.lookup(file_path)
        if existing_doc_id:
            return existing_doc_id
        doc_id = pageIndexService.submit_and_wait(file_path)
        self.store(file_path, doc_id)
        return doc_id