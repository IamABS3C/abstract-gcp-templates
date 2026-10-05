<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../../brand/abstract-logo-white.svg">
  <img alt="Abstract Security" src="../../brand/abstract-logo-black.svg" width="180">
</picture>

# Network Threat Telemetry Export to Abstract Security

<a href="https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/IamABS3C/abstract-gcp-templates&cloudshell_git_branch=main&cloudshell_workspace=deployments/11-network-threats&cloudshell_tutorial=TUTORIAL.md"><img alt="Open in Cloud Shell" src="https://gstatic.com/cloudssh/images/open-btn.svg" height="24"></a>

Provisions a high-performance aggregated export pipeline routing the four fundamental pillars of GCP network threat telemetry directly to **Abstract Security** via Google Cloud Pub/Sub.

> [!WARNING]
> **These logs reach the Pub/Sub topic; Abstract's managed GCP parser does not yet store them.** The managed GCP Pub/Sub parser keeps only Cloud Audit Log records, and firewall, DNS, Cloud Armor and Cloud IDS logs are not audit logs. There is no parser for them yet. Do not rely on them for detection until a parser ships.

<p align="center">
  <img src="../../images/diagrams/11-network-threats.png" width="100%" alt="GCP Network Threat Telemetry Architecture Diagram">
</p>

> [!TIP]
> **Interactive Architecture Diagram (Draw.io / diagrams.net)**:
> Edit, export, and customize this architecture directly on your machine or browser:
> ```bash
> ./scripts/open-diagram.sh 11-network-threats          # Opens in macOS Draw.io Desktop
> ./scripts/open-diagram.sh 11-network-threats --web    # Opens in diagrams.net
> ```

---

## Overview

Network threat detection is a primary security workload in Google Cloud Platform (GCP). While Cloud Audit Logs capture management-plane API interactions, network security events occur in the data plane: edge web attacks, intrusion attempts, command-and-control (C2) beacons, exfiltration via DNS, and lateral movement probes.

This deployment creates a unified, production-grade export pipeline routing the four fundamental pillars of GCP network threat telemetry directly to **Abstract Security** via Google Cloud Pub/Sub:

1. **Cloud Armor WAF decisions** (`resource.type="http_load_balancer"`)
2. **Cloud IDS threat alerts** (`logName:"ids.googleapis.com%2Fthreat"`)
3. **VPC DNS query logs** (`logName:"dns.googleapis.com%2Fdns_queries"`)
4. **Cloud Firewall rule decisions** (`logName:"compute.googleapis.com%2Ffirewall"`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GCP Network Surfaces                             │
│                                                                             │
│  [Cloud Armor WAF]     [Cloud IDS]      [VPC Cloud DNS]   [VPC Firewalls]   │
│  HTTP(S) Load Balancer  Threat engine    Query logging     Rule decisions   │
│  (OWASP, DDoS, LFI)    (CVEs, Malware)  (C2, tunneling)   (ALLOW / DENY)   │
└──────────────┬─────────────────┬───────────────┬──────────────────┬─────────┘
               │                 │               │                  │
               ▼                 ▼               ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│             Aggregated Cloud Logging Sink (Organization / Folder)           │
│                                                                             │
│  Filter: (resource.type="http_load_balancer")                               │
│      OR  (logName:"ids.googleapis.com%2Fthreat")                            │
│      OR  (logName:"dns.googleapis.com%2Fdns_queries")                       │
│      OR  (logName:"compute.googleapis.com%2Ffirewall")                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Writer Identity
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Dedicated Logging Project (log_project)                  │
│                                                                             │
│   Pub/Sub Topic: abstract-network-threats                                   │
│         │                                                                   │
│         ▼                                                                   │
│   Pub/Sub Pull Subscription: abstract-network-threats-sub                   │
│         ▲                                                                   │
│         │ Authenticated Pull                                                │
│   Abstract Security Platform                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
    subgraph Surfaces["GCP Network Security Telemetry Surfaces"]
        Armor["Cloud Armor WAF<br/>(resource.type=http_load_balancer)<br/>OWASP, DDoS, L7 Rules"]
        IDS["Cloud IDS Threat Engine<br/>(logName: ids.../threat)<br/>Malware, Exploits, CVEs"]
        DNS["VPC Cloud DNS Queries<br/>(logName: dns.../dns_queries)<br/>C2, Exfiltration, Tunneling"]
        Firewall["VPC Firewall Decisions<br/>(logName: compute.../firewall)<br/>Allow / Deny rule logs"]
    end

    subgraph AggregatedSink["Aggregated Log Router (Org / Folder Level)"]
        Router["Cloud Logging Aggregated Sink<br/>abstract-network-threats-sink"]
        Filter["Composite Filter:<br/>Armor OR Cloud IDS OR DNS Queries OR Firewall Rules"]
        Router --- Filter
    end

    subgraph LoggingProject["Dedicated Logging Project (log_project)"]
        Topic["Pub/Sub Topic<br/>abstract-network-threats"]
        Sub["Pub/Sub Pull Subscription<br/>abstract-network-threats-sub"]
        SA["Reader Service Account<br/>abstract-network-threats-reader"]
        Topic --> Sub
        SA -.->|Subscribes to| Sub
    end

    subgraph Abstract["Abstract Security Platform"]
        SIEM["Abstract Security SIEM<br/>(Network Threat Analytics)"]
    end

    Armor --> Router
    IDS --> Router
    DNS --> Router
    Firewall --> Router

    Router -->|Writer Identity (roles/pubsub.publisher)| Topic
    Sub --> SIEM

    style Abstract fill:#FF216B15,stroke:#FF216B,stroke-width:2px
    style SIEM fill:#FF216B,color:#ffffff,stroke:#FF216B,stroke-width:2px
    classDef surfaceBox fill:#f8f9fa,stroke:#FBBC04,stroke-width:1.5px;
    classDef routerBox fill:#f8f9fa,stroke:#4285F4,stroke-width:1.5px;
    class Surfaces surfaceBox;
    class AggregatedSink,LoggingProject routerBox;
```

---

## Telemetry Dataflow & Ingestion Path

Network security telemetry constitutes the highest volume and most dynamic event stream in Google Cloud. Partitioning this telemetry into a dedicated Pub/Sub pipeline ensures that high-velocity network attacks do not starve low-volume, high-criticality control plane audit logs:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TELEMETRY DATAFLOW & INGESTION PATH                                     │
│                                                                                                         │
│   GCP Network Telemetry Fabric         Pub/Sub Ingestion Pipeline            Abstract Security Platform │
│   ┌───────────────────────────┐        ┌───────────────────────────┐         ┌────────────────────────┐ │
│   │ • Cloud Armor L7 WAF Logs │  gRPC  │ Topic:                    │  gRPC   │ • Threat Detection     │ │
│   │ • Cloud IDS Threat Signat.├───────►│ abstract-network-threats  ├────────►│ • C2 Beacon Analytics │ │
│   │ • Cloud DNS Query Logs    │ TLS 1.3│ Sub:                      │ TLS 1.3 │ • WAF Attack Correl.   │ │
│   │ • VPC Firewall Allow/Deny │        │ ...-network-threats-sub   │         │ • NetFlow Graph Model  │ │
│   └───────────────────────────┘        └───────────────────────────┘         └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Technical Telemetry Parameters

| Dimension | Specification | Operational Note |
|---|---|---|
| **Ingestion Protocols** | Google Internal Network Logging ➔ Cloud Pub/Sub StreamingPull (gRPC / HTTPS over TLS 1.3) | Wire-level encryption with mutual TLS authentication |
| **Transport Port** | `443` (Outbound TLS) | No specialized firewall modifications required |
| **Telemetry Latency Profile** | • Cloud Armor WAF: < 2s<br/>• Cloud IDS Threats: 5–30s<br/>• VPC DNS Queries: 2–5s<br/>• VPC Firewalls: 1–3s | Immediate write-time routing to Pub/Sub |
| **Pub/Sub Transport Latency** | < 100 milliseconds | Microsecond buffering in regional Google fabric |
| **Throughput & Capacity** | 50,000+ events/second sustained burst | Dedicated topic prevents control-plane audit log starvation |
| **Durability & Guarantees** | At-least-once delivery, 7-day retention window | Resilient against consumer disconnections or network partitions |

---

## Diagnostic & Troubleshooting Decision Tree

When network telemetry fails to appear in Abstract Security, use this sequential decision tree to locate the failure:

```
Network Threat Telemetry Issue
  │
  ├──► [Cloud Armor Events Missing?]
  │      ├── YES ──► Check if Logging is enabled on the Load Balancer Backend Service!
  │      │           Command: gcloud compute backend-services list --format="table(name,enableLogging)"
  │      │           Remediation: gcloud compute backend-services update BACKEND --enable-logging
  │      └── NO  ──► Check Cloud IDS
  │
  ├──► [Cloud IDS Alerts Missing?]
  │      ├── YES ──► Check if Cloud IDS endpoint is in READY state and Packet Mirroring is attached!
  │      │           Commands: gcloud ids endpoints list
  │      │                     gcloud compute packet-mirrorings list
  │      └── NO  ──► Check Cloud DNS
  │
  ├──► [Cloud DNS Queries Missing?]
  │      ├── YES ──► DNS query logging is OFF by default. Verify Cloud DNS server policy!
  │      │           Command: gcloud dns policies list
  │      │           Remediation: gcloud dns policies create ... --enable-logging
  │      └── NO  ──► Check VPC Firewalls
  │
  ├──► [Firewall Decisions Missing?]
  │      ├── YES ──► Firewall logging is configured PER RULE. Check logConfig.enable!
  │      │           Command: gcloud compute firewall-rules list --format="table(name,logConfig.enable)"
  │      └── NO  ──► Check Topic IAM Permissions
  │
  └──► [Sink Writer Identity Has roles/pubsub.publisher?]
         └── NO  ──► Missing publisher role on abstract-network-threats topic!
                     Command: gcloud pubsub topics get-iam-policy abstract-network-threats
```

### Verification & Remediation Commands

#### 1. Verify Cloud Armor Logging on Backend Services
```bash
gcloud compute backend-services list \
  --format="table(name,enableLogging,logConfig.sampleRate)"
```
If logging is disabled, enable it with 100% sample rate:
```bash
gcloud compute backend-services update BACKEND_SERVICE_NAME \
  --global \
  --enable-logging \
  --logging-sample-rate=1.0
```

#### 2. Verify Cloud IDS Endpoints & Packet Mirroring
```bash
gcloud ids endpoints list
gcloud compute packet-mirrorings list
```

#### 3. Verify Cloud DNS Server Policies
```bash
gcloud dns policies list \
  --format="table(name,enableLogging,networks[].networkUrl)"
```
If missing, create policy with query logging enabled:
```bash
gcloud dns policies create vpc-dns-security-policy \
  --description="Enables VPC DNS query logging for security telemetry" \
  --enable-logging \
  --networks=VPC_NETWORK_NAME
```

#### 4. Verify Firewall Rule Logging
```bash
gcloud compute firewall-rules list \
  --format="table(name,network,direction,action,logConfig.enable)"
```
Enable logging on critical deny rules:
```bash
gcloud compute firewall-rules update FIREWALL_RULE_NAME \
  --enable-logging \
  --logging-metadata=include-all
```

#### 5. Verify Network Threat Sink Writer Permissions
```bash
export LOG_PROJECT="acme-security-logging"
export ORG_ID="123456789012"

export WRITER_SA=$(gcloud logging sinks describe abstract-network-threats-sink \
  --organization="$ORG_ID" \
  --format="value(writerIdentity)")

echo "Sink Writer Service Account: $WRITER_SA"

gcloud pubsub topics get-iam-policy abstract-network-threats \
  --project="$LOG_PROJECT" \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/pubsub.publisher"
```

If missing, grant publisher permissions:
```bash
gcloud pubsub topics add-iam-policy-binding abstract-network-threats \
  --project="$LOG_PROJECT" \
  --member="${WRITER_SA}" \
  --role="roles/pubsub.publisher"
```

#### 6. Test Network Messages via a Probe Subscription
```bash
# Never pull from abstract-network-threats-sub: with --auto-ack that deletes events before Abstract
# reads them, and without it hides them from Abstract for the ack deadline.
# Pull from a throwaway subscription on the same topic instead. Create it BEFORE the
# test event: a new subscription only receives messages published after it exists.
PROBE="abstract-probe-$(date +%s)"
gcloud pubsub subscriptions create "$PROBE" --topic=abstract-network-threats \
  --project="$LOG_PROJECT" --expiration-period=1d --message-retention-duration=10m
# Make a DNS query or trigger a logged firewall rule from a VM in the VPC, then wait.
sleep 60
gcloud pubsub subscriptions pull "$PROBE" --project="$LOG_PROJECT" --limit=2 --auto-ack
gcloud pubsub subscriptions delete "$PROBE" --project="$LOG_PROJECT" --quiet
```

---

## 1. Cloud Armor WAF Decision Logging

### Architecture & Mechanism
Google Cloud Armor provides enterprise DDoS mitigation and Web Application Firewall (WAF) capabilities for external and internal Application Load Balancers. It inspects incoming HTTP/HTTPS traffic against:
- Preconfigured WAF rulesets (OWASP Top 10 core rules: SQLi, XSS, LFI, RFI, RCE, scanner detection, protocol attacks)
- Custom Layer 7 security rules (IP allow/block lists, geo-fencing, header inspection, reCAPTCHA validation)
- Rate limiting and bot management policies
- Adaptive Protection machine learning threat detection

> [!IMPORTANT]
> **Crucial GCP Nuance:** Cloud Armor does **not** emit logs to an isolated Cloud Armor service log name. Instead, all Cloud Armor WAF decisions (rule matches, block actions, preview evaluations, rate limit triggers) are embedded directly within **HTTP(S) Load Balancer request logs** (`resource.type="http_load_balancer"`).
>
> If request logging is disabled on the backend services of your load balancers, **Cloud Armor decisions are not written to Cloud Logging and cannot be routed to Abstract**.

### Enabling Logging on Backend Services

To capture Cloud Armor evaluations, request logging must be enabled on every Backend Service protected by a Cloud Armor security policy.

#### Using `gcloud`:
```bash
# For Global Application Load Balancers:
gcloud compute backend-services update BACKEND_SERVICE_NAME \
  --global \
  --enable-logging \
  --logging-sample-rate=1.0

# For Regional Application Load Balancers:
gcloud compute backend-services update BACKEND_SERVICE_NAME \
  --region=REGION \
  --enable-logging \
  --logging-sample-rate=1.0
```

#### Using Terraform:
```hcl
resource "google_compute_backend_service" "app_service" {
  name                  = "web-backend-service"
  project               = "workload-project-id"
  security_policy       = google_compute_security_policy.armor_policy.id
  load_balancing_scheme = "EXTERNAL_MANAGED"

  log_config {
    enable      = true
    sample_rate = 1.0 # 100% of requests sampled
  }
}
```

### Telemetry & Log Fields in Abstract
Cloud Armor enriches `resource.type="http_load_balancer"` entries with `jsonPayload`:
* `jsonPayload.enforcedSecurityPolicy`:
  * `name`: Security policy identifier
  * `outcome`: Decision result (`ACCEPT`, `DENY`)
  * `priority`: Rule priority matched
  * `configuredAction`: Configured response (`DENY_403`, `DENY_404`, `DENY_502`, `RATE_BASED_BAN`)
  * `preconfiguredExprIds`: Matched WAF rule IDs (e.g. `sqli-v33-crs`, `xss-v33-crs`, `rce-v33-crs`, `cve-canary`)
* `jsonPayload.previewSecurityPolicy`: Logs what rules *would* have matched for rules deployed in Preview mode without impacting live production traffic.
* `httpRequest.remoteIp`: Attacker/client source IP address.
* `httpRequest.requestMethod` & `httpRequest.requestUrl`: Attacking HTTP method and target URI.

---

## 2. Cloud IDS Threat Logs

> [!NOTE]
> **Cloud IDS costs money on its own.** It is billed per endpoint-hour plus per GB of traffic inspected, and it needs Packet Mirroring. These templates do not create the IDS endpoint or the mirroring policy; they only route the threat logs an existing endpoint writes.

### Architecture & Mechanism
Google Cloud Intrusion Detection System (Cloud IDS) delivers cloud-native network threat detection powered by Palo Alto Networks technologies. Cloud IDS inspects traffic for:
- Malware communication and spyware command-and-control (C2)
- Exploits against known CVEs and software vulnerabilities
- Remote access trojans (RATs) and reverse shell connections
- Lateral movement and port scans between VPC subnets

Cloud IDS operates out-of-band by attaching an IDS endpoint to a customer VPC via Private Service Access (PSA). Traffic is cloned to the IDS inspection engine using GCP **Packet Mirroring**.

### Setting Up Cloud IDS Endpoint & Packet Mirroring

#### Step 1: Create a Cloud IDS Endpoint
```bash
gcloud ids endpoints create ids-us-central1 \
  --project=WORKLOAD_PROJECT_ID \
  --zone=us-central1-a \
  --network=VPC_NETWORK_NAME \
  --severity=INFORMATIONAL
```
*Note: Setting `--severity=INFORMATIONAL` ensures all threat severities (`INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) are analyzed and logged.*

#### Step 2: Retrieve the Endpoint's Forwarding Rule
```bash
gcloud ids endpoints describe ids-us-central1 \
  --zone=us-central1-a \
  --project=WORKLOAD_PROJECT_ID \
  --format="value(endpointForwardingRule)"
```

#### Step 3: Attach Packet Mirroring
Create a packet mirroring policy in the VPC that forwards traffic from sensitive subnets or tagged VMs to the IDS collector:
```bash
gcloud compute packet-mirrorings create ids-mirroring-policy \
  --project=WORKLOAD_PROJECT_ID \
  --region=us-central1 \
  --network=VPC_NETWORK_NAME \
  --collector-ilb=FORWARDING_RULE_FROM_STEP_2 \
  --mirrored-subnets=SUBNET_TO_MONITOR
```

### Telemetry & Log Fields in Abstract
Cloud IDS emits security findings directly to Cloud Logging under:
`logName:"ids.googleapis.com%2Fthreat"`

Key fields forwarded to Abstract include:
* `jsonPayload.alert_severity`: Threat severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFORMATIONAL`).
* `jsonPayload.category`: Threat category (`vulnerability`, `spyware`, `malware`, `c2`).
* `jsonPayload.threat_id` & `jsonPayload.threat_name`: Specific vulnerability identifier (e.g. `CVE-2021-44228 Log4j RCE`, `Palo Alto Threat ID 91542`).
* `jsonPayload.application`: Identified layer-7 application protocol (e.g. `ssh`, `dns`, `ssl`, `web-browsing`).
* `jsonPayload.src_ip_address` & `jsonPayload.dest_ip_address`: Attacker and victim IP endpoints.
* `jsonPayload.src_port` & `jsonPayload.dest_port`: Transport layer ports.
* `jsonPayload.direction`: `client-to-server` or `server-to-client`.

---

## 3. VPC DNS Query Logging Policy

### Architecture & Importance
Domain Name System (DNS) query logging is widely recognized as the single highest-fidelity data plane signal for identifying:
- Command and Control (C2) beaconing and domain generation algorithms (DGAs)
- DNS data exfiltration and tunneling (e.g. `dnscat2`, `iodine`, large TXT/NULL queries)
- Access to phishing domains or newly registered malicious infrastructure
- Fast-flux DNS and malicious domain resolution

In GCP, Compute Engine VMs, Google Kubernetes Engine (GKE) nodes, and serverless connectors forward recursive DNS queries to the internal metadata resolver (`169.254.169.254`).

> [!NOTE]
> **DNS Query Logging is OFF by default:** GCP does not log internal or outbound DNS queries until an explicit **Cloud DNS Server Policy** with query logging enabled is bound to the VPC network.

### Enabling DNS Query Logging via Cloud DNS Policy

#### Using `gcloud`:
```bash
gcloud dns policies create vpc-dns-security-policy \
  --project=WORKLOAD_PROJECT_ID \
  --description="Enables VPC DNS query logging for security telemetry" \
  --enable-logging \
  --networks=VPC_NETWORK_NAME
```

#### Using Terraform:
```hcl
resource "google_dns_policy" "vpc_dns_logging" {
  name                      = "vpc-dns-logging-policy"
  project                   = "workload-project-id"
  description               = "VPC DNS query logging for Abstract Security threat detection"
  enable_logging            = true

  networks {
    network_url = google_compute_network.vpc.id
  }
}
```

### Telemetry & Log Fields in Abstract
DNS queries are captured under:
`logName:"dns.googleapis.com%2Fdns_queries"`

Key fields routed to Abstract:
* `jsonPayload.queryName`: Queried fully qualified domain name (FQDN), e.g. `malicious-c2.attacker.com.`
* `jsonPayload.queryType`: DNS record type requested (`A`, `AAAA`, `TXT`, `MX`, `CNAME`, `ANY`).
* `jsonPayload.responseCode`: DNS server response code (`NOERROR`, `NXDOMAIN`, `SERVFAIL`). A spike in `NXDOMAIN` is a primary indicator of DGA botnets.
* `jsonPayload.vmInstanceId`: Unique ID of the Compute Engine instance originating the query.
* `jsonPayload.srcIp`: Private IP address of the source workload or pod.
* `jsonPayload.destination`: Address of the DNS resolver handling the request.

---

## 4. Cloud Firewall Rule Decision Logging

### Architecture & Mechanism
Google Cloud VPC Firewalls enforce ingress and egress traffic filtering across Compute Engine VMs and GKE nodes. When enabled, firewall rule logging records individual TCP/UDP/ICMP connection attempts matched against firewall rules.

> [!NOTE]
> **Firewall Logging is Configured PER RULE:** A Cloud Logging sink cannot force firewall rules to generate logs. Logging must be enabled either on individual VPC firewall rules or within Network Firewall Policies.

### Enabling Firewall Rule Logging

#### For Individual VPC Firewall Rules:
Enable logging with metadata on deny rules (perimeter defense) or sensitive allow rules:

```bash
# Enable logging on an existing deny rule:
gcloud compute firewall-rules update default-deny-all-ingress \
  --project=WORKLOAD_PROJECT_ID \
  --enable-logging \
  --logging-metadata=include-all
```

#### For Hierarchical / Network Firewall Policies:
If utilizing centralized Hierarchical Firewall Policies or Regional Network Firewall Policies:
```bash
gcloud compute network-firewall-policies rules update PRIORITY \
  --firewall-policy=POLICY_NAME \
  --enable-logging
```

### Telemetry & Log Fields in Abstract
Firewall decisions appear under:
`logName:"compute.googleapis.com%2Ffirewall"`

Key fields forwarded to Abstract:
* `jsonPayload.rule_details.action`: Rule verdict (`ALLOW` or `DENY`).
* `jsonPayload.rule_details.reference`: Resource path of the matched rule.
* `jsonPayload.connection`:
  * `src_ip`: Source IPv4 or IPv6 address.
  * `dest_ip`: Destination IP address.
  * `src_port`: Source port number.
  * `dest_port`: Target port number (e.g. `22` for SSH brute force, `3389` for RDP, `445` for SMB).
  * `protocol`: Protocol number (`6` for TCP, `17` for UDP, `1` for ICMP).
* `jsonPayload.disposition`: `ALLOWED` or `DENIED`.
* `jsonPayload.instance.vm_name`: Target VM instance receiving or initiating the connection.

---

## Deployment Instructions

### Prerequisites
1. **IAM Permissions**:
   * Organization scope: `roles/logging.configWriter` on the organization (`--org-id`) or folder (`--folder-id`).
   * Pub/Sub: `roles/pubsub.admin` on the dedicated logging project (`var.log_project`).
   * Service Account: `roles/iam.serviceAccountAdmin` on `var.log_project`.
2. **Dedicated Logging Project**:
   * Host the Pub/Sub topic and subscription in a dedicated logging or security project, separate from workload projects.
   * If you need to create one, run [`deployments/01-logging-project`](../01-logging-project).

### Configuration (`terraform.tfvars`)

```hcl
sink_scope  = "organization"
org_id      = "123456789012"
log_project = "acme-security-logging"

# Categories to include (defaults to all three network categories):
log_categories = ["firewall", "dns_queries", "load_balancer"]

# Cloud IDS threat log filter:
platform_log_filters = ["ids.googleapis.com%2Fthreat"]

# dns_queries and load_balancer are high tier. The plan stops until you acknowledge
# the volume (or pass -var acknowledge_high_volume=true). Measure a baseline first.
acknowledge_high_volume = true
```

### State Storage (`backend.tf`)

```bash
cp backend.tf.example backend.tf
```

Ensure the state bucket exists and has object versioning enabled:
```bash
gcloud storage buckets create gs://acme-abstract-tfstate \
  --project=acme-security-logging --location=US --uniform-bucket-level-access
gcloud storage buckets update gs://acme-abstract-tfstate --versioning
```

### Apply

```bash
tofu init
tofu plan
tofu apply
```

### Outputs
Run `tofu output` to view the parameters for Abstract Security onboarding:

```bash
tofu output abstract_onboarding
```

The output returns:
- `project_id`: The project holding the subscription (`var.log_project`).
- `subscription_id`: The short subscription ID (`abstract-network-threats-sub`).
- `credentials`: Instructions to create the service account JSON key for Abstract.

---

## Connecting to Abstract Security

1. Generate a key for the provisioned Abstract subscriber service account:
   ```bash
   SA_EMAIL=$(tofu output -raw service_account_email)
   gcloud iam service-accounts keys create key.json \
     --iam-account="$SA_EMAIL"
   ```
2. Navigate to your **Abstract Security Platform Console**.
3. Create a new **Google Cloud Pub/Sub** Data Source:
   * **Project ID**: Supply the output from `tofu output -raw abstract_onboarding` (`project_id`).
   * **Subscription ID**: Supply the short subscription name (`abstract-network-threats-sub`).
   * **Service Account Key**: Upload the generated `key.json`.
4. Delete the local `key.json` file once uploaded:
   ```bash
   rm -f key.json
   ```

---

[← All scenarios](../../README.md) · [Architecture](../../docs/ARCHITECTURE.md) · [Permissions](../../docs/PERMISSIONS.md) · [Filter Catalog](../../docs/FILTERS.md)
