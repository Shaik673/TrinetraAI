"""
Evidence Collection Agent — gathers logs, asset info, vulnerabilities, packet metadata.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.workflow.state import (
    InvestigationState, LogEntry, PacketMetadata, VulnerabilityInfo, AssetInfo
)
from app.core.logging import get_logger

logger = get_logger("evidence_collector_agent")

SYSTEM_PROMPT = """You are the Evidence Collection Agent for TrinetraAI.
Your role is to determine which evidence needs to be collected and simulate retrieving it
from various security data sources (SIEM, EDR, network sensors, vulnerability scanners).
Respond with valid JSON only."""


def _simulate_server_logs(source_ip: str, dest_ip: str, alert_time: str) -> List[Dict]:
    """Generate realistic simulated server logs around the alert time."""
    base_time = datetime.fromisoformat(alert_time.replace('Z', '+00:00')) if 'T' in alert_time else datetime.utcnow()
    logs = []
    templates = [
        {"level": "ERROR", "message": f"Failed authentication attempt from {source_ip}", "source": "sshd"},
        {"level": "WARNING", "message": f"Suspicious process execution detected: cmd.exe /c whoami", "source": "syslog"},
        {"level": "ERROR", "message": f"Connection refused from {source_ip} on port 22", "source": "auth"},
        {"level": "INFO", "message": f"New connection established from {source_ip}", "source": "httpd"},
        {"level": "WARNING", "message": f"Privilege escalation attempt detected for user root", "source": "sudo"},
        {"level": "ERROR", "message": f"File access denied: /etc/shadow by process python3", "source": "auditd"},
        {"level": "CRITICAL", "message": f"Rootkit detection: hidden process found", "source": "security"},
        {"level": "INFO", "message": f"User login successful: admin from {source_ip}", "source": "auth"},
        {"level": "WARNING", "message": f"Outbound connection to suspicious IP {dest_ip}:4444", "source": "firewall"},
        {"level": "ERROR", "message": f"SQL injection attempt detected in request from {source_ip}", "source": "waf"},
    ]
    for i, tmpl in enumerate(random.sample(templates, min(6, len(templates)))):
        logs.append({
            "timestamp": (base_time - timedelta(minutes=i * 3)).isoformat(),
            "source": tmpl["source"],
            "level": tmpl["level"],
            "message": tmpl["message"],
            "raw": {"host": dest_ip, "pid": random.randint(1000, 9999)},
        })
    return logs


def _simulate_auth_logs(source_ip: str) -> List[Dict]:
    auth_entries = []
    base = datetime.utcnow()
    for i in range(8):
        auth_entries.append({
            "timestamp": (base - timedelta(minutes=i * 2)).isoformat(),
            "source": "auth_log",
            "level": "WARNING" if i < 5 else "INFO",
            "message": f"Authentication {'failed' if i < 5 else 'succeeded'} for user {'root' if i % 2 == 0 else 'admin'} from {source_ip}",
            "raw": {
                "user": "root" if i % 2 == 0 else "admin",
                "ip": source_ip,
                "method": "password",
                "result": "failed" if i < 5 else "success",
            },
        })
    return auth_entries


def _simulate_packet_metadata(source_ip: str, dest_ip: str) -> List[Dict]:
    base = datetime.utcnow()
    flows = []
    port_combos = [
        (random.randint(40000, 65535), 22, "TCP"),
        (random.randint(40000, 65535), 443, "TCP"),
        (random.randint(40000, 65535), 4444, "TCP"),
        (random.randint(40000, 65535), 80, "TCP"),
        (random.randint(40000, 65535), 3389, "TCP"),
    ]
    for i, (src_port, dst_port, proto) in enumerate(port_combos):
        flows.append({
            "timestamp": (base - timedelta(minutes=i * 5)).isoformat(),
            "src_ip": source_ip,
            "dst_ip": dest_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": proto,
            "bytes_transferred": random.randint(512, 50000),
            "flags": ["SYN", "ACK"] if dst_port != 4444 else ["SYN", "ACK", "PSH"],
            "payload_summary": f"{'Encrypted TLS' if dst_port == 443 else 'Plaintext'} traffic to port {dst_port}",
        })
    return flows


def _simulate_asset_info(ip: str) -> Dict:
    return {
        "asset_id": f"ASSET-{ip.replace('.', '-')}",
        "hostname": f"server-{ip.split('.')[-1]}.internal",
        "ip_address": ip,
        "asset_type": random.choice(["web_server", "database_server", "workstation", "domain_controller"]),
        "os": random.choice(["Ubuntu 22.04 LTS", "Windows Server 2022", "CentOS 8", "RHEL 9"]),
        "criticality": random.choice(["critical", "high", "medium"]),
        "is_quarantined": False,
        "vulnerabilities": [],
        "open_ports": [22, 80, 443, 3306, 5432],
        "services": ["ssh", "nginx", "postgresql"],
    }


def _simulate_vulnerabilities(ip: str) -> List[Dict]:
    vuln_pool = [
        {"cve_id": "CVE-2023-44487", "description": "HTTP/2 Rapid Reset Attack", "cvss_score": 7.5,
         "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
         "affected_systems": [ip], "exploit_available": True, "patch_available": True},
        {"cve_id": "CVE-2021-44228", "description": "Log4Shell Remote Code Execution", "cvss_score": 10.0,
         "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
         "affected_systems": [ip], "exploit_available": True, "patch_available": True},
        {"cve_id": "CVE-2023-23397", "description": "Microsoft Outlook Elevation of Privilege", "cvss_score": 9.8,
         "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
         "affected_systems": [ip], "exploit_available": True, "patch_available": False},
        {"cve_id": "CVE-2022-30216", "description": "Windows Server Service Tampering", "cvss_score": 8.8,
         "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
         "affected_systems": [ip], "exploit_available": False, "patch_available": True},
    ]
    return random.sample(vuln_pool, min(3, len(vuln_pool)))


class EvidenceCollectorAgent(BaseAgent):
    name = "evidence_collector"
    description = "Gathers logs, asset info, vulnerabilities, and packet metadata for investigation"

    async def execute(self, state: InvestigationState) -> InvestigationState:
        logger.info("evidence_collector_started", investigation_id=state["investigation_id"])
        alert = state.get("alert", {})
        plan = state.get("investigation_plan", {})
        sources_needed = plan.get("evidence_sources_needed", [
            "server_logs", "auth_logs", "packet_metadata", "asset_info", "vulnerabilities"
        ])

        source_ip = alert.get("source_ip", "10.0.0.100")
        dest_ip = alert.get("destination_ip", "192.168.1.50")
        alert_time = alert.get("alert_time", datetime.utcnow().isoformat())

        server_logs, auth_logs, packet_meta, assets, vulns = [], [], [], [], []
        collected_sources = []

        if "server_logs" in sources_needed:
            raw = _simulate_server_logs(source_ip, dest_ip, alert_time)
            server_logs = [LogEntry(**log) for log in raw]
            collected_sources.append(f"{len(server_logs)} server log entries")

        if "auth_logs" in sources_needed:
            raw = _simulate_auth_logs(source_ip)
            auth_logs = [LogEntry(**log) for log in raw]
            collected_sources.append(f"{len(auth_logs)} auth log entries")

        if "packet_metadata" in sources_needed:
            raw = _simulate_packet_metadata(source_ip, dest_ip)
            packet_meta = [PacketMetadata(**pkt) for pkt in raw]
            collected_sources.append(f"{len(packet_meta)} packet flows")

        if "asset_info" in sources_needed:
            for ip in [dest_ip, source_ip]:
                asset_raw = _simulate_asset_info(ip)
                assets.append(AssetInfo(**{k: asset_raw.get(k) for k in AssetInfo.__annotations__ if k in asset_raw}))
            collected_sources.append(f"{len(assets)} assets identified")

        if "vulnerabilities" in sources_needed:
            for asset in assets:
                vuln_list = _simulate_vulnerabilities(asset.get("ip_address", dest_ip))
                vulns.extend([VulnerabilityInfo(**v) for v in vuln_list])
            collected_sources.append(f"{len(vulns)} vulnerabilities found")

        decision = self._record_decision(
            state,
            decision=f"Collected evidence from {len(collected_sources)} sources",
            reasoning=f"Evidence needed per plan: {sources_needed}. Collected: {', '.join(collected_sources)}",
            confidence=0.85,
        )

        event = self._record_event(
            state,
            event_type="evidence_collected",
            message=f"Evidence collection complete: {'; '.join(collected_sources)}",
            data={"sources": collected_sources},
        )

        return {
            **state,
            "server_logs": server_logs,
            "auth_logs": auth_logs,
            "packet_metadata": packet_meta,
            "assets": assets,
            "vulnerabilities": vulns,
            "current_agent": "evidence_collector",
            "next_agent": "threat_correlator",
            "agent_decisions": [decision],
            "workflow_history": [event],
            "updated_at": datetime.utcnow().isoformat(),
        }
