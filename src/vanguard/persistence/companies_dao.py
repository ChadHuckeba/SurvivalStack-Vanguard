import logging
from typing import Optional
from vanguard.models.company import Company
from .base_dao import BaseDAO

logger = logging.getLogger("vanguard.persistence.companies")

class CompaniesDAO(BaseDAO):
    """
    Data Access Object for managing company registry metadata.
    """

    def get_company(self, company_name: str) -> Optional[Company]:
        """Retrieves company metadata from the registry."""
        query = "SELECT * FROM companies WHERE company_name = ?"
        with self.engine.get_connection() as conn:
            row = conn.execute(query, (company_name,)).fetchone()
            if row:
                res = dict(row)
                return Company(**res)
        return None

    def upsert_company(self, company: Company) -> bool:
        """Adds or updates a company in the registry."""
        data = company.model_dump()
        name = data["company_name"]
        domain = data["root_domain"]
        career = data["career_url"]
        ats = data["ats_provider"]
        
        with self.engine.get_connection() as conn:
            conn.execute("""
                INSERT INTO companies (company_name, root_domain, career_url, ats_provider, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(company_name) DO UPDATE SET
                    root_domain = COALESCE(?, root_domain),
                    career_url = COALESCE(?, career_url),
                    ats_provider = COALESCE(?, ats_provider),
                    last_updated = CURRENT_TIMESTAMP
            """, (name, domain, career, ats, domain, career, ats))
            conn.commit()
            return True
