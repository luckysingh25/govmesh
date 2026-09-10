import httpx
import logging
import json

from app.connectors.base import BaseConnector, ConnectorResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class TaxConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.tax_url)

    async def fetch_data(self, citizen_id: str, correlation_id: str | None = None) -> ConnectorResult:
        try:
            headers = {"X-Correlation-ID": correlation_id} if correlation_id else {}
            job = await self.client.post(f"{self.base_url}/api/tax/requests/{citizen_id}", headers=headers)
            job.raise_for_status()
            job_data = job.json()
            if job_data.get("status") == "pending":
                return ConnectorResult("tax", "pending", {"tax_status": "PENDING", "job_id": job_data["job_id"]}, protocol="Async REST", raw_response=self.bounded_payload(json.dumps(job_data, indent=2)), source_mapping={"status":"tax.tax_status"}, external_job_id=job_data["job_id"])
            job_id = job_data["job_id"]
            response = await self.client.get(f"{self.base_url}/api/tax/requests/{job_id}", headers=headers)
            response.raise_for_status()
            result_payload = response.json()
            if result_payload.get("status") == "pending":
                return ConnectorResult("tax", result_payload.get("status", "pending"), {"tax_status": "PENDING", "job_id": job_id}, protocol="Async REST", raw_response=self.bounded_payload(json.dumps(result_payload, indent=2)), external_job_id=job_id)
            data = result_payload["result"]
            normalized = {
                "tax_id": data["taxId"],
                "taxpayer_name": data["taxpayerName"],
                "tax_status": data["taxStatus"],
                "outstanding_amount": data["outstandingAmount"],
                "assessment_year": data["assessmentYear"],
            }
            return ConnectorResult("tax", "success", normalized, protocol="Async REST", raw_response=self.bounded_payload(json.dumps(result_payload, indent=2)), source_mapping={"taxId":"tax.tax_id","taxpayerName":"tax.taxpayer_name","taxStatus":"tax.tax_status","outstandingAmount":"tax.outstanding_amount","assessmentYear":"tax.assessment_year"}, external_job_id=job_id)
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.warning("tax_http_error status=%s", status)
            if status == 404:
                return ConnectorResult("tax", "not_found", {}, "Tax record was not found")
            return ConnectorResult("tax", "failed", {}, "Tax service returned an error")
        except httpx.TimeoutException:
            logger.warning("tax_timeout")
            return ConnectorResult("tax", "timeout", {}, "Tax service timed out")
        except httpx.RequestError:
            logger.warning("tax_unavailable")
            return ConnectorResult("tax", "unavailable", {}, "Tax service could not be reached")
        except (KeyError, TypeError, ValueError):
            logger.warning("tax_invalid_response")
            return ConnectorResult("tax", "invalid_response", {}, "Tax service returned an invalid response")

    async def resume_job(self, job_id: str, correlation_id: str | None = None) -> ConnectorResult:
        try:
            headers = {"X-Correlation-ID": correlation_id} if correlation_id else {}
            response = await self.client.get(f"{self.base_url}/api/tax/requests/{job_id}", headers=headers)
            response.raise_for_status()
            payload = response.json()
            if payload.get("status") != "completed":
                return ConnectorResult("tax", payload.get("status", "pending"), {"tax_status":"PENDING", "job_id":job_id}, protocol="Async REST", raw_response=self.bounded_payload(json.dumps(payload, indent=2)), external_job_id=job_id)
            data = payload["result"]
            normalized = {"tax_id":data["taxId"],"taxpayer_name":data["taxpayerName"],"tax_status":data["taxStatus"],"outstanding_amount":data["outstandingAmount"],"assessment_year":data["assessmentYear"]}
            return ConnectorResult("tax", "success", normalized, protocol="Async REST", raw_response=self.bounded_payload(json.dumps(payload, indent=2)), source_mapping={"taxId":"tax.tax_id","taxpayerName":"tax.taxpayer_name","taxStatus":"tax.tax_status","outstandingAmount":"tax.outstanding_amount","assessmentYear":"tax.assessment_year"}, external_job_id=job_id)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return ConnectorResult("tax", "failed", {}, "Tax job could not be resumed", protocol="Async REST", external_job_id=job_id)
