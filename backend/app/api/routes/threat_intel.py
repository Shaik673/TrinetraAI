from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/threat-intel", tags=["Threat Intelligence"])

# Simulated MITRE ATT&CK techniques
MITRE_TECHNIQUES = [
    {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution", "severity": "high"},
    {"id": "T1078", "name": "Valid Accounts", "tactic": "Defense Evasion, Persistence, Privilege Escalation, Initial Access", "severity": "high"},
    {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access", "severity": "medium"},
    {"id": "T1486", "name": "Data Encrypted for Impact", "tactic": "Impact", "severity": "critical"},
    {"id": "T1048", "name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "severity": "high"},
    {"id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control", "severity": "medium"},
    {"id": "T1055", "name": "Process Injection", "tactic": "Defense Evasion, Privilege Escalation", "severity": "high"},
    {"id": "T1082", "name": "System Information Discovery", "tactic": "Discovery", "severity": "low"},
    {"id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement", "severity": "high"},
    {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access", "severity": "critical"},
    {"id": "T1105", "name": "Ingress Tool Transfer", "tactic": "Command and Control", "severity": "medium"},
    {"id": "T1490", "name": "Inhibit System Recovery", "tactic": "Impact", "severity": "critical"},
]

SAMPLE_CVES = [
    {"cve_id": "CVE-2021-44228", "description": "Log4Shell - Apache Log4j2 Remote Code Execution", "cvss_score": 10.0, "affected": "Apache Log4j 2.x", "exploit_available": True},
    {"cve_id": "CVE-2023-44487", "description": "HTTP/2 Rapid Reset Attack (DoS)", "cvss_score": 7.5, "affected": "HTTP/2 servers", "exploit_available": True},
    {"cve_id": "CVE-2023-23397", "description": "Microsoft Outlook Elevation of Privilege", "cvss_score": 9.8, "affected": "Microsoft Outlook", "exploit_available": True},
    {"cve_id": "CVE-2022-30216", "description": "Windows Server Service Tampering Vulnerability", "cvss_score": 8.8, "affected": "Windows Server", "exploit_available": False},
    {"cve_id": "CVE-2024-3094", "description": "XZ Utils Backdoor (Supply Chain Attack)", "cvss_score": 10.0, "affected": "XZ Utils 5.6.0-5.6.1", "exploit_available": True},
    {"cve_id": "CVE-2023-20198", "description": "Cisco IOS XE Web UI Privilege Escalation", "cvss_score": 10.0, "affected": "Cisco IOS XE", "exploit_available": True},
]


@router.get("/mitre/techniques")
async def get_mitre_techniques(
    search: Optional[str] = Query(None),
    tactic: Optional[str] = Query(None),
):
    results = MITRE_TECHNIQUES
    if search:
        results = [t for t in results if search.lower() in t["name"].lower() or search.upper() in t["id"]]
    if tactic:
        results = [t for t in results if tactic.lower() in t["tactic"].lower()]
    return {"count": len(results), "techniques": results}


@router.get("/cves")
async def search_cves(
    search: Optional[str] = Query(None),
    min_cvss: float = Query(0.0, ge=0.0, le=10.0),
):
    results = [c for c in SAMPLE_CVES if c["cvss_score"] >= min_cvss]
    if search:
        results = [c for c in results if search.lower() in c["description"].lower() or search.upper() in c["cve_id"]]
    return {"count": len(results), "cves": results}


@router.get("/cves/{cve_id}")
async def get_cve(cve_id: str):
    cve = next((c for c in SAMPLE_CVES if c["cve_id"].upper() == cve_id.upper()), None)
    if not cve:
        return {"error": "CVE not found", "cve_id": cve_id}
    return cve


@router.get("/threat-feeds")
async def get_threat_feeds():
    """Return simulated threat feed entries."""
    return {
        "feeds": [
            {
                "feed_name": "Emerging Threats",
                "indicator_type": "ip",
                "value": "185.220.101.45",
                "threat_type": "Tor Exit Node",
                "confidence": 0.95,
                "last_seen": "2026-09-12T10:00:00Z",
            },
            {
                "feed_name": "AlienVault OTX",
                "indicator_type": "domain",
                "value": "malicious-c2-domain.xyz",
                "threat_type": "Command and Control",
                "confidence": 0.88,
                "last_seen": "2026-09-11T18:30:00Z",
            },
            {
                "feed_name": "VirusTotal",
                "indicator_type": "hash",
                "value": "5d41402abc4b2a76b9719d911017c592",
                "threat_type": "Ransomware Payload",
                "confidence": 0.99,
                "last_seen": "2026-09-10T12:00:00Z",
            },
        ],
        "total": 3,
    }
