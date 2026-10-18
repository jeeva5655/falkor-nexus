"""
Seed dataset for FalkorNexus.
Models a realistic high-tech Cloud & Fintech enterprise knowledge graph,
enabling deep multi-hop reasoning, multi-agent coordination, and company intelligence.
"""

def seed_enterprise_graph(graph):
    """
    Populates the graph with interconnected enterprise entities:
    Teams, Persons, Services, Repositories, PRs, Commits, Incidents,
    Tickets, RFCs, Decisions, Slack messages, and Procedural Playbooks.
    """
    # 1. Teams
    teams = [
        {"id": "team_sre", "name": "Cloud Platform & SRE", "dept": "Infrastructure", "slack": "#infra-sre", "lead": "alex_rivera"},
        {"id": "team_auth", "name": "Identity & Access Management", "dept": "Security Engineering", "slack": "#team-iam", "lead": "sarah_chen"},
        {"id": "team_payments", "name": "Core Payments & Billing", "dept": "Fintech Products", "slack": "#payments-dev", "lead": "marcus_vance"},
        {"id": "team_secops", "name": "Security Operations (SOC)", "dept": "Information Security", "slack": "#sec-war-room", "lead": "priya_sharma"},
        {"id": "team_data", "name": "Data Platform & Streaming", "dept": "Analytics", "slack": "#data-eng", "lead": "elena_rostova"}
    ]
    for t in teams:
        graph.add_node(t["id"], "Team", t)

    # 2. Persons / Engineers
    people = [
        {
            "id": "sarah_chen",
            "name": "Sarah Chen",
            "role": "Principal Systems Architect",
            "email": "sarah.chen@nexuscorp.io",
            "timezone": "UTC-7 (San Francisco)",
            "on_call": True,
            "skills": ["Distributed Systems", "Graph Databases", "OAuth2/JWT", "Zero-Trust Architecture", "FalkorDB"],
            "bio": "Lead architect for auth and graph persistence. Author of RFC-104 and RFC-112."
        },
        {
            "id": "alex_rivera",
            "name": "Alex Rivera",
            "role": "Staff SRE & Incident Commander",
            "email": "alex.rivera@nexuscorp.io",
            "timezone": "UTC-5 (New York)",
            "on_call": True,
            "skills": ["Kubernetes", "Observability", "Chaos Engineering", "Incident Triage", "Traffic Routing"],
            "bio": "Platform reliability lead. On-call commander for tier-1 outage triage."
        },
        {
            "id": "marcus_vance",
            "name": "Marcus Vance",
            "role": "Senior Staff Payments Engineer",
            "email": "marcus.vance@nexuscorp.io",
            "timezone": "UTC-8 (Seattle)",
            "on_call": False,
            "skills": ["Ledger Systems", "Stripe API", "Idempotency", "PCI-DSS", "High-Throughput Go"],
            "bio": "Subject matter expert on PaymentGateway, settlement reconciliation, and double-entry ledgers."
        },
        {
            "id": "priya_sharma",
            "name": "Priya Sharma",
            "role": "Principal Security Engineer",
            "email": "priya.sharma@nexuscorp.io",
            "timezone": "UTC+1 (London)",
            "on_call": False,
            "skills": ["Vulnerability Management", "AppSec", "Threat Modeling", "CVE Triage", "Cryptography"],
            "bio": "Head of security architecture. Leads CVE triage and blast-radius vulnerability containment."
        },
        {
            "id": "elena_rostova",
            "name": "Elena Rostova",
            "role": "Staff Data Engineer",
            "email": "elena.rostova@nexuscorp.io",
            "timezone": "UTC+2 (Berlin)",
            "on_call": False,
            "skills": ["Kafka", "ClickHouse", "Event Sourcing", "Real-time Telemetry", "Graph Analytics"],
            "bio": "Maintains telemetry pipelines and streaming analytics."
        }
    ]
    for p in people:
        graph.add_node(p["id"], "Person", p)

    # Link Person to Team
    graph.add_edge("sarah_chen", "team_auth", "MEMBER_OF", {"role": "Lead"})
    graph.add_edge("alex_rivera", "team_sre", "MEMBER_OF", {"role": "Lead"})
    graph.add_edge("marcus_vance", "team_payments", "MEMBER_OF", {"role": "Lead"})
    graph.add_edge("priya_sharma", "team_secops", "MEMBER_OF", {"role": "Lead"})
    graph.add_edge("elena_rostova", "team_data", "MEMBER_OF", {"role": "Lead"})

    # 3. Services / Microservices
    services = [
        {"id": "service_payment_gw", "name": "PaymentGateway", "tier": "Tier-1", "language": "Go", "health": "DEGRADED", "critical": True, "sla": "99.99%"},
        {"id": "service_auth", "name": "AuthService", "tier": "Tier-1", "language": "Rust", "health": "CRITICAL_FAILING", "critical": True, "sla": "99.999%"},
        {"id": "service_user_dir", "name": "UserDirectory", "tier": "Tier-2", "language": "TypeScript", "health": "HEALTHY", "critical": False, "sla": "99.9%"},
        {"id": "service_ledger", "name": "LedgerDB", "tier": "Tier-1", "language": "C++", "health": "HEALTHY", "critical": True, "sla": "99.999%"},
        {"id": "service_notif", "name": "NotificationService", "tier": "Tier-2", "language": "Python", "health": "HEALTHY", "critical": False, "sla": "99.5%"},
        {"id": "service_order_proc", "name": "OrderProcessor", "tier": "Tier-1", "language": "Java", "health": "DEGRADED", "critical": True, "sla": "99.95%"},
        {"id": "service_kafka", "name": "KafkaStreamingBus", "tier": "Tier-1", "language": "JVM", "health": "HEALTHY", "critical": True, "sla": "99.99%"},
        {"id": "service_falkor_graph", "name": "FalkorDBCluster", "tier": "Tier-1", "language": "C/Redis", "health": "OPTIMAL", "critical": True, "sla": "99.999%"}
    ]
    for s in services:
        graph.add_node(s["id"], "Service", s)

    # Team Ownership of Services
    graph.add_edge("team_payments", "service_payment_gw", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_payments", "service_order_proc", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_payments", "service_ledger", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_auth", "service_auth", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_auth", "service_user_dir", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_sre", "service_falkor_graph", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_sre", "service_kafka", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_data", "service_notif", "OWNS", {"ownership_level": "Primary"})

    # Service Dependencies (Call Graph & Blast Radius)
    # PaymentGateway -> AuthService, LedgerDB, OrderProcessor
    graph.add_edge("service_payment_gw", "service_auth", "DEPENDS_ON", {"protocol": "gRPC", "timeout_ms": 150, "circuit_breaker": False})
    graph.add_edge("service_payment_gw", "service_ledger", "DEPENDS_ON", {"protocol": "TCP", "timeout_ms": 50, "circuit_breaker": True})
    graph.add_edge("service_order_proc", "service_payment_gw", "DEPENDS_ON", {"protocol": "HTTP/2", "timeout_ms": 500, "circuit_breaker": True})
    graph.add_edge("service_order_proc", "service_user_dir", "DEPENDS_ON", {"protocol": "gRPC", "timeout_ms": 100, "circuit_breaker": True})
    graph.add_edge("service_user_dir", "service_auth", "DEPENDS_ON", {"protocol": "gRPC", "timeout_ms": 100, "circuit_breaker": False})
    graph.add_edge("service_auth", "service_falkor_graph", "DEPENDS_ON", {"protocol": "Falkor-Cypher", "timeout_ms": 20, "circuit_breaker": True})
    graph.add_edge("service_notif", "service_kafka", "DEPENDS_ON", {"protocol": "KafkaConsumer", "timeout_ms": 1000, "circuit_breaker": False})
    graph.add_edge("service_payment_gw", "service_kafka", "DEPENDS_ON", {"protocol": "KafkaProducer", "timeout_ms": 50, "circuit_breaker": True})

    # On-call relationships
    graph.add_edge("sarah_chen", "service_auth", "ON_CALL_FOR", {"shift": "Primary 24/7", "escalation_tier": 1})
    graph.add_edge("alex_rivera", "service_payment_gw", "ON_CALL_FOR", {"shift": "Secondary SRE", "escalation_tier": 2})
    graph.add_edge("marcus_vance", "service_payment_gw", "ON_CALL_FOR", {"shift": "Primary Domain Expert", "escalation_tier": 1})

    # 4. Code Commits & Pull Requests (Track 01 & 03: Change Tracing)
    prs = [
        {
            "id": "pr_482",
            "number": 482,
            "title": "feat(auth): Upgrade JWT validation with zero-trust token cache",
            "status": "MERGED",
            "merged_at": "2026-10-15T04:15:00Z",
            "author_id": "sarah_chen",
            "risk_score": 0.88,
            "changes_summary": "Introduced strict cryptographic payload signature check and cache TTL eviction."
        },
        {
            "id": "pr_479",
            "number": 479,
            "title": "perf(ledger): Add batching for reconciliation queries",
            "status": "MERGED",
            "merged_at": "2026-10-14T18:30:00Z",
            "author_id": "marcus_vance",
            "risk_score": 0.15,
            "changes_summary": "Optimized batch write transaction sizes in LedgerDB."
        }
    ]
    for pr in prs:
        graph.add_node(pr["id"], "PullRequest", pr)

    commits = [
        {
            "id": "commit_c3b8f19",
            "hash": "c3b8f19",
            "message": "fix(jwt): enforce strict claim verification on external bearer tokens",
            "timestamp": "2026-10-15T04:12:00Z",
            "author_id": "sarah_chen"
        },
        {
            "id": "commit_a7e204d",
            "hash": "a7e204d",
            "message": "chore(deps): bump falkordb-client to v1.8.0",
            "timestamp": "2026-10-14T22:00:00Z",
            "author_id": "sarah_chen"
        }
    ]
    for c in commits:
        graph.add_node(c["id"], "Commit", c)

    # PR and Commit Links
    graph.add_edge("sarah_chen", "pr_482", "AUTHORED", {"created_at": "2026-10-14T19:00:00Z"})
    graph.add_edge("pr_482", "commit_c3b8f19", "CONTAINS", {})
    graph.add_edge("pr_482", "service_auth", "MODIFIES", {"files_changed": 8, "lines_added": 240, "lines_removed": 45})
    graph.add_edge("marcus_vance", "pr_479", "AUTHORED", {"created_at": "2026-10-14T12:00:00Z"})
    graph.add_edge("pr_479", "service_ledger", "MODIFIES", {"files_changed": 3, "lines_added": 55, "lines_removed": 12})

    # 5. Incidents (Track 01 & 02: Triage and Memory)
    incidents = [
        {
            "id": "inc_804",
            "title": "INC-804: PaymentGateway 500 Spike & Upstream Auth Timeouts",
            "severity": "SEV-1 (CRITICAL)",
            "status": "ACTIVE_INVESTIGATING",
            "detected_at": "2026-10-15T05:30:00Z",
            "error_rate": "18.4%",
            "symptoms": "HTTP 500 error cascade on /v2/checkout. Latency rose from 45ms to 2400ms.",
            "impact": "Customer checkout conversions dropping. $12,000/min estimated revenue risk."
        },
        {
            "id": "inc_732",
            "title": "INC-732: Auth Token Revocation Memory Leak & Latency Spikes",
            "severity": "SEV-2 (RESOLVED)",
            "status": "RESOLVED",
            "detected_at": "2026-09-28T14:10:00Z",
            "resolution": "Rolled back in-memory token map. Decided to transition token graph to FalkorDB.",
            "postmortem_url": "https://wiki.nexuscorp.io/postmortems/inc-732"
        }
    ]
    for inc in incidents:
        graph.add_node(inc["id"], "Incident", inc)

    # Incident Relationships
    graph.add_edge("inc_804", "service_payment_gw", "AFFECTS", {"detected_metric": "error_rate > 15%"})
    graph.add_edge("inc_804", "commit_c3b8f19", "TRIGGERED_BY", {"confidence": 0.94, "heuristic": "Time-correlation & Auth stacktrace"})
    graph.add_edge("inc_732", "service_auth", "AFFECTS", {})
    graph.add_edge("sarah_chen", "inc_732", "RESOLVED_BY", {"resolution_time_min": 42})

    # 6. RFCs & Architecture Decisions (Track 03: Decision Provenance)
    rfcs = [
        {
            "id": "rfc_104",
            "code": "RFC-104",
            "title": "Transition Session & Identity Store to FalkorDB Multi-Tenant Graph Context",
            "status": "APPROVED_ACTIVE",
            "summary": "Replaces fragmented Redis/Postgres session caches with unified FalkorDB graph topology for sub-millisecond multi-hop permission queries.",
            "approved_at": "2026-10-02"
        },
        {
            "id": "rfc_112",
            "code": "RFC-112",
            "title": "Universal Circuit Breaker & Adaptive Rate Limiting for Tier-1 Services",
            "status": "IN_REVIEW",
            "summary": "Mandates Hystrix/Resilience4j style circuit breakers on all inter-service gRPC dependencies.",
            "approved_at": None
        }
    ]
    for r in rfcs:
        graph.add_node(r["id"], "RFC", r)

    decisions = [
        {
            "id": "dec_42",
            "title": "ADR-42: Adopt FalkorDB for Multi-Tenant Agent Context & Graph Topology",
            "status": "DECIDED",
            "rationale": "FalkorDB offers isolated multi-graph per tenant, ultra-low latency graph algorithms in C, and native Cypher query speed.",
            "decided_date": "2026-10-04"
        }
    ]
    for d in decisions:
        graph.add_node(d["id"], "Decision", d)

    # Decision Lineage
    graph.add_edge("sarah_chen", "rfc_104", "AUTHORED", {})
    graph.add_edge("rfc_104", "dec_42", "PRODUCED", {})
    graph.add_edge("dec_42", "inc_732", "MOTIVATED_BY", {"evidence": "Postmortem identified memory leak in legacy session cache"})
    graph.add_edge("rfc_104", "service_auth", "GOVERNS", {})
    graph.add_edge("rfc_104", "service_falkor_graph", "GOVERNS", {})
    graph.add_edge("sarah_chen", "rfc_112", "AUTHORED", {})
    graph.add_edge("rfc_112", "service_payment_gw", "GOVERNS", {})

    # 7. Slack Messages & Communication Context (Track 03)
    slack_msgs = [
        {
            "id": "msg_804_1",
            "channel": "#war-room-payment",
            "sender": "alex_rivera",
            "text": "PagerDuty fired: PaymentGateway error rate hit 18.4%. Checkout failures climbing.",
            "timestamp": "2026-10-15T05:32:00Z"
        },
        {
            "id": "msg_804_2",
            "channel": "#war-room-payment",
            "sender": "marcus_vance",
            "text": "PaymentGateway logs show 504 Gateway Timeout connecting to AuthService gRPC endpoint.",
            "timestamp": "2026-10-15T05:35:00Z"
        },
        {
            "id": "msg_804_3",
            "channel": "#team-iam",
            "sender": "sarah_chen",
            "text": "PR #482 was merged 1 hour ago touching token cache TTL. Looking into it now.",
            "timestamp": "2026-10-15T05:38:00Z"
        }
    ]
    for msg in slack_msgs:
        graph.add_node(msg["id"], "SlackMessage", msg)
        graph.add_edge(msg["sender"], msg["id"], "SENT", {"timestamp": msg["timestamp"]})
        graph.add_edge(msg["id"], "inc_804", "DISCUSSES", {})

    # 8. Procedural Memory (Playbooks & SOPs) (Track 02)
    playbooks = [
        {
            "id": "plb_sev1_triage",
            "name": "SEV-1 Tier-1 Service Outage Mitigation SOP",
            "domain": "Platform Reliability",
            "trigger_condition": "error_rate > 10% OR cascade_failure",
            "steps_count": 4
        },
        {
            "id": "plb_sec_cve_containment",
            "name": "Zero-Day Vulnerability & CVE Blast-Radius Containment SOP",
            "domain": "Information Security",
            "trigger_condition": "CVSS >= 8.5 OR unauthenticated_rce",
            "steps_count": 3
        }
    ]
    for plb in playbooks:
        graph.add_node(plb["id"], "Playbook", plb)

    steps = [
        {
            "id": "step_sev1_1",
            "step_number": 1,
            "action_name": "Dependency Blast-Radius & PageRank Analysis",
            "command": "CALL falkor.blast_radius($service_id, depth=3)",
            "description": "Traverse upstream and downstream dependencies to calculate cascading blast radius."
        },
        {
            "id": "step_sev1_2",
            "step_number": 2,
            "action_name": "Identify Recent Deployments & Commits in Radius",
            "command": "MATCH (s:Service)<-[:MODIFIES]-(pr:PullRequest)<-[:AUTHORED]-(p:Person) RETURN pr, p ORDER BY pr.merged_at DESC",
            "description": "Find recent pull requests merged in the past 6 hours within the blast radius."
        },
        {
            "id": "step_sev1_3",
            "step_number": 3,
            "action_name": "Trigger Circuit-Breaker & Isolate Culprit Service",
            "command": "EXECUTE service.circuit_breaker.enable(target='service_auth', fallback_mock=True)",
            "description": "Prevent cascaded timeout exhaustion by failing fast with cached responses."
        },
        {
            "id": "step_sev1_4",
            "step_number": 4,
            "action_name": "Page On-Call Expert & Draft Rollback PR",
            "command": "EXECUTE pagerduty.page(person='sarah_chen') AND github.revert(pr='pr_482')",
            "description": "Notify designated on-call architect and prepare automated rollback branch."
        }
    ]
    for stp in steps:
        graph.add_node(stp["id"], "PlaybookStep", stp)

    # Link Playbook Steps in Procedural Sequence
    graph.add_edge("plb_sev1_triage", "step_sev1_1", "FIRST_STEP", {})
    graph.add_edge("step_sev1_1", "step_sev1_2", "NEXT_STEP", {})
    graph.add_edge("step_sev1_2", "step_sev1_3", "NEXT_STEP", {})
    graph.add_edge("step_sev1_3", "step_sev1_4", "NEXT_STEP", {})

    # 9. Episodic Memory (Track 02: Historical Sessions & Learning)
    episodes = [
        {
            "id": "ep_2026_09_28",
            "session_id": "sess_historic_01",
            "user_id": "alex_rivera",
            "intent": "Investigate recurring memory leak in AuthService during peak load",
            "outcome": "Identified unbounded cache growth in JWT claims. Guided team to file RFC-104.",
            "confidence": 0.98,
            "timestamp": "2026-09-28T16:00:00Z"
        }
    ]
    for ep in episodes:
        graph.add_node(ep["id"], "MemoryEpisode", ep)
        graph.add_edge(ep["id"], "service_auth", "RECALLS_SERVICE", {})
        graph.add_edge(ep["id"], "rfc_104", "LED_TO_RFC", {})
        graph.add_edge(ep["id"], "inc_732", "RESOLVED_INCIDENT", {})

    return {
        "status": "seeded",
        "total_nodes": len(graph.nodes),
        "total_edges": len(graph.edges)
    }


def seed_cyber_defense_graph(graph):
    """
    Populates tenant_aegis_cyber_brain with a SecOps, Zero-Trust & CVE Triage graph:
    Services: ApiGatewayWAF, VaultKMS, IdentityProxy, ThreatIntelStream, AuditLogger
    Persons: Elena Vance (SecOps Lead), Devon Brooks (Zero-Trust Architect), Marcus Kane (Incident Handler)
    Teams: team_cloudsec (Cloud Security), team_redteam (Offensive Sec)
    Incidents: cve_2026_9901 (Critical OpenSSL Buffer Overflow RCE)
    PRs, Commits, RFCs, Playbooks.
    """
    # 1. Teams
    teams = [
        {"id": "team_cloudsec", "name": "Cloud Security Operations", "dept": "InfoSec", "slack": "#secops-war-room", "lead": "elena_vance"},
        {"id": "team_redteam", "name": "Offensive Security & Red Team", "dept": "Cyber Defense", "slack": "#red-ops", "lead": "devon_brooks"}
    ]
    for t in teams:
        graph.add_node(t["id"], "Team", t)

    # 2. Persons
    people = [
        {"id": "elena_vance", "name": "Elena Vance", "role": "Principal SecOps Commander", "email": "elena.vance@aegiscyber.io", "on_call": True, "skills": ["CVE Triage", "Firewall Rules", "Zero-Trust", "SIEM"]},
        {"id": "devon_brooks", "name": "Devon Brooks", "role": "Staff Zero-Trust Architect", "email": "devon.brooks@aegiscyber.io", "on_call": True, "skills": ["mTLS", "Vault", "Key Management", "FalkorDB"]},
        {"id": "marcus_kane", "name": "Marcus Kane", "role": "Senior Threat Analyst", "email": "marcus.kane@aegiscyber.io", "on_call": False, "skills": ["Network Forensics", "WAF Policy", "Mitre ATT&CK"]}
    ]
    for p in people:
        graph.add_node(p["id"], "Person", p)

    graph.add_edge("elena_vance", "team_cloudsec", "MEMBER_OF", {"role": "Lead"})
    graph.add_edge("devon_brooks", "team_cloudsec", "MEMBER_OF", {"role": "Architect"})
    graph.add_edge("marcus_kane", "team_redteam", "MEMBER_OF", {"role": "Senior Analyst"})

    # 3. Services
    services = [
        {"id": "service_waf_gateway", "name": "ApiGatewayWAF", "tier": "Tier-1", "language": "Rust", "health": "DEGRADED", "critical": True, "sla": "99.999%"},
        {"id": "service_vault_kms", "name": "VaultKMS", "tier": "Tier-1", "language": "Go", "health": "HEALTHY", "critical": True, "sla": "99.999%"},
        {"id": "service_id_proxy", "name": "IdentityProxy", "tier": "Tier-1", "language": "C++", "health": "CRITICAL_FAILING", "critical": True, "sla": "99.99%"},
        {"id": "service_threat_stream", "name": "ThreatIntelStream", "tier": "Tier-2", "language": "Python", "health": "HEALTHY", "critical": False, "sla": "99.5%"},
        {"id": "service_audit_logger", "name": "AuditLogger", "tier": "Tier-1", "language": "Go", "health": "HEALTHY", "critical": True, "sla": "99.9%"}
    ]
    for s in services:
        graph.add_node(s["id"], "Service", s)

    # Ownership
    graph.add_edge("team_cloudsec", "service_waf_gateway", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_cloudsec", "service_id_proxy", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_cloudsec", "service_vault_kms", "OWNS", {"ownership_level": "Primary"})
    graph.add_edge("team_redteam", "service_threat_stream", "OWNS", {"ownership_level": "Advisory"})

    # Dependencies
    graph.add_edge("service_waf_gateway", "service_id_proxy", "DEPENDS_ON", {"protocol": "mTLS", "circuit_breaker": False})
    graph.add_edge("service_id_proxy", "service_vault_kms", "DEPENDS_ON", {"protocol": "gRPC", "circuit_breaker": True})
    graph.add_edge("service_waf_gateway", "service_threat_stream", "DEPENDS_ON", {"protocol": "AsyncEvent", "circuit_breaker": True})
    graph.add_edge("service_id_proxy", "service_audit_logger", "DEPENDS_ON", {"protocol": "TCP", "circuit_breaker": True})

    # On Call
    graph.add_edge("elena_vance", "service_waf_gateway", "ON_CALL_FOR", {"shift": "Primary 24/7"})
    graph.add_edge("devon_brooks", "service_id_proxy", "ON_CALL_FOR", {"shift": "Primary Architect"})

    # 4. Incident CVE
    cve = {
        "id": "cve_2026_9901",
        "title": "CVE-2026-9901: OpenSSL Buffer Overflow RCE in IdentityProxy mTLS Handshake",
        "severity": "CRITICAL_SEV1",
        "status": "ACTIVE_INVESTIGATION",
        "started_at": "2026-10-18T18:30:00Z",
        "cvss_score": 9.8,
        "symptoms": "Corrupted ASN.1 parser triggers stack overflow and crash in IdentityProxy handshake"
    }
    graph.add_node(cve["id"], "Incident", cve)
    graph.add_edge("cve_2026_9901", "service_id_proxy", "AFFECTS", {"impact": "Direct Vulnerability Exploit"})

    # 5. Pull Request & Commit
    pr = {
        "id": "pr_sec_912",
        "number": 912,
        "title": "fix(ssl): patch OpenSSL 3.4.1 ASN.1 parsing memory corruption",
        "status": "MERGED",
        "merged_at": "2026-10-18T17:45:00Z",
        "author_id": "devon_brooks",
        "risk_score": 0.88
    }
    graph.add_node(pr["id"], "PullRequest", pr)
    graph.add_edge(pr["id"], "service_id_proxy", "MODIFIES", {})
    graph.add_edge("devon_brooks", pr["id"], "AUTHORED", {})

    commit = {
        "id": "commit_sec_f99a",
        "hash": "f99a01b",
        "message": "fix(asn1): validate buffer length before memcpy",
        "author_id": "devon_brooks"
    }
    graph.add_node(commit["id"], "Commit", commit)
    graph.add_edge(pr["id"], commit["id"], "CONTAINS", {})
    graph.add_edge("cve_2026_9901", commit["id"], "TRIGGERED_BY", {})

    # 6. Policy & RFC
    rfc = {
        "id": "rfc_sec_201",
        "title": "RFC-201: Zero-Trust Strict mTLS Boundary & KMS Ephemeral Certificates",
        "status": "APPROVED",
        "author": "Devon Brooks"
    }
    graph.add_node(rfc["id"], "RFC", rfc)
    graph.add_edge("devon_brooks", rfc["id"], "AUTHORED", {})

    # 7. Playbook
    playbook = {
        "id": "plb_cve_containment",
        "name": "Zero-Trust Active CVE Quarantine & Rollback SOP",
        "domain": "Cloud Security",
        "trigger_condition": "cvss > 9.0 && cve_active == True",
        "severity": "CRITICAL"
    }
    graph.add_node(playbook["id"], "Playbook", playbook)
    step1 = {"id": "step_cve_1", "step_number": 1, "action_name": "Quarantine Vulnerable Pods", "command": "EXECUTE waf.block_traffic(service_id='service_id_proxy')"}
    step2 = {"id": "step_cve_2", "step_number": 2, "action_name": "Revoke mTLS Intermediate Certs", "command": "CALL vault.revoke_certs('intermediate_ca')"}
    graph.add_node(step1["id"], "PlaybookStep", step1)
    graph.add_node(step2["id"], "PlaybookStep", step2)
    graph.add_edge("plb_cve_containment", step1["id"], "FIRST_STEP", {})
    graph.add_edge(step1["id"], step2["id"], "NEXT_STEP", {})

    return {
        "status": "seeded",
        "tenant": "aegis_cyber",
        "total_nodes": len(graph.nodes),
        "total_edges": len(graph.edges)
    }

