import json
import logging
import sqlite3
from typing import List, Optional, Dict, Any
from vanguard.models.lead import Lead, SourceInfo, LeadContent, CareerInfo, Metadata
from .base_dao import BaseDAO

logger = logging.getLogger("vanguard.persistence.leads")


class LeadsDAO(BaseDAO):
    """
    Data Access Object for managing job leads (entries).
    """

    def _map_row_to_lead(self, row: sqlite3.Row) -> Lead:
        """Translates a database row into a Pydantic Lead model."""
        res = dict(row)
        content_data = json.loads(res["entry_data"])

        return Lead(
            vanguard_id=res["vanguard_id"],
            source_info=SourceInfo(
                scout=res["provider_id"],
                source_url=content_data.get("source_url") or content_data.get("source") or "unknown",
            ),
            content=LeadContent(**content_data),
            work_model=res.get("work_model", "unknown"),
            career_info=CareerInfo(
                url=res.get("career_url"),
                method=res.get("career_discovery_method"),
                status=res.get("career_extraction_status"),
                error=res.get("career_error_log"),
            ),
            metadata=Metadata(
                first_seen=res["first_seen"], 
                last_seen=res["last_seen"], 
                hit_count=res["hit_count"]
            ),
            status=res["status"],
        )

    def get_lead(self, vanguard_id: str) -> Optional[Lead]:
        """Retrieves a single lead by its unique fingerprint."""
        query = "SELECT * FROM entries WHERE vanguard_id = ?"
        with self.engine.get_connection() as conn:
            row = conn.execute(query, (vanguard_id,)).fetchone()
            return self._map_row_to_lead(row) if row else None

    def list_leads(self, status: str = "active") -> List[Lead]:
        """Returns all leads matching the provided status."""
        query = "SELECT * FROM entries WHERE status = ?"
        with self.engine.get_connection() as conn:
            rows = conn.execute(query, (status,)).fetchall()
            return [self._map_row_to_lead(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """Returns optimized database statistics using SQL aggregates."""
        stats: Dict[str, Any] = {
            "total_leads": 0,
            "providers": {},
            "extraction_status": {}
        }
        
        with self.engine.get_connection() as conn:
            # 1. Total Count
            stats["total_leads"] = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            
            # 2. Provider Distribution
            for row in conn.execute("SELECT provider_id, COUNT(*) FROM entries GROUP BY provider_id"):
                stats["providers"][row[0]] = row[1]
                
            # 3. Status Distribution
            for row in conn.execute("SELECT career_extraction_status, COUNT(*) FROM entries GROUP BY career_extraction_status"):
                stats["extraction_status"][row[0] or "unknown"] = row[1]
                
        return stats

    def upsert_lead(self, lead: Lead) -> bool:
        """Inserts or updates a lead, preserving first_seen date."""
        data = lead.model_dump()
        v_id = data["vanguard_id"]
        provider_id = data["source_info"]["scout"]
        entry_data = json.dumps(data["content"])
        work_model = data["work_model"]

        career = data["career_info"]
        career_url = career["url"]
        career_method = career["method"]
        career_status = career["status"]
        career_error = career["error"]

        with self.engine.get_connection() as conn:
            # Check for existing
            row = conn.execute("SELECT hit_count FROM entries WHERE vanguard_id = ?", (v_id,)).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE entries SET
                        last_seen = CURRENT_TIMESTAMP,
                        hit_count = hit_count + 1,
                        status = 'active',
                        entry_data = COALESCE(?, entry_data),
                        work_model = ?,
                        career_url = COALESCE(?, career_url),
                        career_discovery_method = COALESCE(?, career_discovery_method),
                        career_extraction_status = CASE WHEN ? != 'pending' THEN ? ELSE career_extraction_status END,
                        career_error_log = COALESCE(?, career_error_log)
                    WHERE vanguard_id = ?
                """,
                    (
                        entry_data,
                        work_model,
                        career_url,
                        career_method,
                        career_status,
                        career_status,
                        career_error,
                        v_id,
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO entries (
                        vanguard_id, provider_id, identity_manifest, entry_data, 
                        work_model, hit_count, 
                        career_url, career_discovery_method, career_extraction_status, career_error_log,
                        status
                    )
                    VALUES (?, ?, '["source_url", "entity_label"]', ?, ?, 1, ?, ?, ?, ?, 'active')
                """,
                    (v_id, provider_id, entry_data, work_model, career_url, career_method, career_status, career_error),
                )
            conn.commit()
            return True
