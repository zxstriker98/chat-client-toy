from sqlalchemy.orm import Session

from database.ChunkRecord import ChunkRecord


class ChunkRepository:

    def __init__(self, session: Session):
        self.session = session

    def insert(self, record: ChunkRecord) -> ChunkRecord:
        self.session.add(record)
        self.session.commit()
        return record

    def insert_many(self, records: list[ChunkRecord]) -> list[ChunkRecord]:
        self.session.add_all(records)
        self.session.commit()
        return records

    def get_by_id(self, chunk_id: int) -> ChunkRecord | None:
        return self.session.get(ChunkRecord, chunk_id)

    def get_by_file(self, file_hash: str) -> list[type[ChunkRecord]]:
        return (
            self.session.query(ChunkRecord)
            .filter(ChunkRecord.file_hash == file_hash)
            .order_by(ChunkRecord.chunk_id)
            .all()
        )

    def get_by_node(self, file_hash: str, node_id: str) -> list[type[ChunkRecord]]:
        return (
            self.session.query(ChunkRecord)
            .filter(ChunkRecord.file_hash == file_hash, ChunkRecord.node_id == node_id)
            .order_by(ChunkRecord.chunk_index)
            .all()
        )

    def get_by_page(self, file_hash: str, page_index: int) -> list[type[ChunkRecord]]:
        return (
            self.session.query(ChunkRecord)
            .filter(ChunkRecord.file_hash == file_hash, ChunkRecord.page_index == page_index)
            .all()
        )

    def delete_by_file(self, file_hash: str) -> int:
        count = (
            self.session.query(ChunkRecord)
            .filter(ChunkRecord.file_hash == file_hash)
            .delete()
        )
        self.session.commit()
        return count

    def delete_all(self) -> int:
        count = self.session.query(ChunkRecord).delete()
        self.session.commit()
        return count

    def count(self, file_hash: str | None = None) -> int:
        q = self.session.query(ChunkRecord)
        if file_hash is not None:
            q = q.filter(ChunkRecord.file_hash == file_hash)
        return q.count()
