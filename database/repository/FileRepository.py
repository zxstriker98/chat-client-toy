from typing import List

from sqlalchemy.orm import Session

from database.FileRecord import FileRecord


class FileRepository:

    def __init__(self, session: Session):
        self.session = session

    def insert(self, record: FileRecord) -> FileRecord:
        self.session.merge(record)
        self.session.commit()
        return record

    def get_by_hash(self, file_hash: str) -> FileRecord | None:
        return self.session.get(FileRecord, file_hash)

    def get_by_doc_id(self, doc_id: str) -> FileRecord | None:
        return self.session.query(FileRecord).filter(FileRecord.doc_id == doc_id).first()

    def get_all(self) -> list[type[FileRecord]]:
        return self.session.query(FileRecord).all()

    def find_by_name(self, search_name: str):
        return self.session.query(FileRecord).filter(FileRecord.file_name.ilike(f"%{search_name}%")).all()

    def delete(self, file_hash: str) -> bool:
        record: FileRecord | None = self.session.get(FileRecord, file_hash)
        if record:
            self.session.delete(record)
            self.session.commit()
            return True
        return False

    def count(self) -> int:
        return self.session.query(FileRecord).count()