import botocore.session
import requests
from pathlib import Path

from utils.cache_manager import (
    load_service_cache,
    save_service_cache,
)
GCP_SERVICES = [
    "acceleratedmobilepageurl",
    "accessapproval",
    "accesscontextmanager",
    "adexchangebuyer2",
    "adexperiencereport",
    "admin",
    "adsense",
    "alertcenter",
    "analytics",
    "androiddeviceprovisioning",
    "androidenterprise",
    "androidmanagement",
    "androidpublisher",
    "apigee",
    "appengine",
    "appsmarket",
    "artifactregistry",
    "assuredworkloads",
    "bigquery",
    "bigtableadmin",
    "billingbudgets",
    "binaryauthorization",
    "calendar",
    "chat",
    "chromemanagement",
    "cloudasset",
    "cloudbilling",
    "cloudbuild",
    "cloudchannel",
    "clouddebugger",
    "clouderrorreporting",
    "cloudfunctions",
    "cloudidentity",
    "cloudiot",
    "cloudkms",
    "cloudprofiler",
    "cloudresourcemanager",
    "cloudscheduler",
    "cloudsearch",
    "cloudsupport",
    "cloudtasks",
    "cloudtrace",
    "compute",
    "contactcenterinsights",
    "container",
    "containeranalysis",
    "contentwarehouse",
    "datacatalog",
    "dataflow",
    "datafusion",
    "datalabeling",
    "datamigration",
    "datapipelines",
    "dataplex",
    "dataproc",
    "datastore",
    "deploymentmanager",
    "dialogflow",
    "dns",
    "documentai",
    "domains",
    "drive",
    "essentialcontacts",
    "eventarc",
    "factchecktools",
    "file",
    "firebase",
    "firebasedynamiclinks",
    "firebasehosting",
    "firebaseml",
    "firestore",
    "gameservices",
    "gkehub",
    "gmail",
    "groupsmigration",
    "groupssettings",
    "healthcare",
    "iam",
    "iap",
    "integrations",
    "keep",
    "kgsearch",
    "language",
    "lifesciences",
    "logging",
    "managedidentities",
    "manufacturers",
    "memcache",
    "ml",
    "monitoring",
    "networkconnectivity",
    "networkmanagement",
    "networksecurity",
    "networkservices",
    "notebooks",
    "oauth2",
    "orgpolicy",
    "osconfig",
    "oslogin",
    "pagespeedonline",
    "people",
    "playcustomapp",
    "playdeveloperreporting",
    "playintegrity",
    "policyanalyzer",
    "privateca",
    "pubsub",
    "realtimebidding",
    "recommender",
    "redis",
    "remotebuildexecution",
    "reseller",
    "run",
    "runtimeconfig",
    "sasportal",
    "searchconsole",
    "secretmanager",
    "securitycenter",
    "serviceconsumermanagement",
    "servicecontrol",
    "servicedirectory",
    "servicemanagement",
    "serviceusage",
    "sheets",
    "siteverification",
    "slides",
    "sourcerepo",
    "spanner",
    "speech",
    "sqladmin",
    "storage",
    "storagetransfer",
    "streetviewpublish",
    "support",
    "surveys",
    "tagmanager",
    "tasks",
    "texttospeech",
    "toolresults",
    "tpu",
    "trafficdirector",
    "transcoder",
    "translate",
    "vault",
    "verifiedaccess",
    "verifiedemail",
    "videointelligence",
    "vision",
    "vmmigration",
    "vmwareengine",
    "vpcaccess",
    "webfonts",
    "webrisk",
    "websecurityscanner",
    "workflows",
    "youtube",
    "youtubereporting"
]
AWS_SERVICES = [
    "accessanalyzer",
    "account",
    "acm",
    "acm-pca",
    "alexaforbusiness",
    "amp",
    "amplify",
    "amplifybackend",
    "amplifyuibuilder",
    "apigateway",
    "apigatewaymanagementapi",
    "apigatewayv2",
    "appconfig",
    "appconfigdata",
    "appfabric",
    "appflow",
    "appintegrations",
    "application-autoscaling",
    "application-insights",
    "applicationcostprofiler",
    "appmesh",
    "apprunner",
    "appstream",
    "appsync",
    "arc-zonal-shift",
    "athena",
    "auditmanager",
    "autoscaling",
    "autoscaling-plans",
    "backup",
    "backup-gateway",
    "backupstorage",
    "batch",
    "billingconductor",
    "braket",
    "budgets",
    "ce",
    "chime",
    "chime-sdk-identity",
    "chime-sdk-media-pipelines",
    "chime-sdk-meetings",
    "chime-sdk-messaging",
    "cloud9",
    "cloudcontrol",
    "clouddirectory",
    "cloudformation",
    "cloudfront",
    "cloudhsm",
    "cloudhsmv2",
    "cloudsearch",
    "cloudtrail",
    "cloudwatch",
    "cloudwatch-events",
    "codeartifact",
    "codebuild",
    "codecommit",
    "codedeploy",
    "codeguru-profiler",
    "codeguru-reviewer",
    "codepipeline",
    "codestar",
    "codestar-connections",
    "codestar-notifications",
    "cognito-identity",
    "cognito-idp",
    "cognito-sync",
    "comprehend",
    "compute-optimizer",
    "config",
    "connect",
    "connect-contact-lens",
    "connectcampaigns",
    "controltower",
    "cur",
    "customer-profiles",
    "databrew",
    "dataexchange",
    "datapipeline",
    "datasync",
    "dax",
    "detective",
    "devicefarm",
    "devops-guru",
    "directconnect",
    "discovery",
    "dlm",
    "dms",
    "docdb",
    "drs",
    "ds",
    "dynamodb",
    "ebs",
    "ec2",
    "ec2-instance-connect",
    "ecr",
    "ecr-public",
    "ecs",
    "eks",
    "elastic-inference",
    "elasticache",
    "elasticbeanstalk",
    "elasticfilesystem",
    "elasticloadbalancing",
    "elasticsearch",
    "emr",
    "emr-containers",
    "emr-serverless",
    "es",
    "events",
    "evidently",
    "finspace",
    "firehose",
    "fis",
    "fms",
    "forecast",
    "forecastquery",
    "frauddetector",
    "fsx",
    "gamelift",
    "gamesparks",
    "glacier",
    "globalaccelerator",
    "glue",
    "grafana",
    "greengrass",
    "greengrassv2",
    "groundstation",
    "guardduty",
    "health",
    "healthlake",
    "honeycode",
    "iam",
    "identitystore",
    "imagebuilder",
    "importexport",
    "inspector",
    "inspector2",
    "internetmonitor",
    "iot",
    "iot-data",
    "iot-jobs-data",
    "iot1click-devices",
    "iot1click-projects",
    "iotanalytics",
    "iotdeviceadvisor",
    "iotevents",
    "iotevents-data",
    "iotfleethub",
    "iotsecuretunneling",
    "iotsitewise",
    "iotthingsgraph",
    "iottwinmaker",
    "iotwireless",
    "ivs",
    "ivschat",
    "kafka",
    "kafkaconnect",
    "kendra",
    "kinesis",
    "kinesis-video-archived-media",
    "kinesis-video-media",
    "kinesis-video-signaling",
    "kinesisanalytics",
    "kinesisanalyticsv2",
    "kms",
    "lakeformation",
    "lambda",
    "lex-models",
    "lex-runtime",
    "lexv2-models",
    "lexv2-runtime",
    "license-manager",
    "lightsail",
    "location",
    "logs",
    "lookoutequipment",
    "lookoutmetrics",
    "lookoutvision",
    "m2",
    "machinelearning",
    "macie",
    "macie2",
    "managedblockchain",
    "marketplace-catalog",
    "marketplace-entitlement",
    "marketplacecommerceanalytics",
    "mediaconnect",
    "mediaconvert",
    "medialive",
    "mediapackage",
    "mediapackage-vod",
    "mediastore",
    "mediastore-data",
    "mediatailor",
    "memorydb",
    "meteringmarketplace",
    "mgh",
    "mgn",
    "migrationhub-refactor-spaces",
    "mobile",
    "mq",
    "mturk",
    "neptune",
    "network-firewall",
    "networkmanager",
    "nimble",
    "oam",
    "opsworks",
    "opsworks-cm",
    "organizations",
    "outposts",
    "panorama",
    "personalize",
    "personalize-events",
    "personalize-runtime",
    "pi",
    "pinpoint",
    "pinpoint-email",
    "pinpoint-sms-voice",
    "polly",
    "pricing",
    "prometheus",
    "qldb",
    "qldb-session",
    "quicksight",
    "ram",
    "rbin",
    "rds",
    "rds-data",
    "redshift",
    "redshift-data",
    "rekognition",
    "resiliencehub",
    "resource-explorer-2",
    "resource-groups",
    "resourcegroupstaggingapi",
    "robomaker",
    "rolesanywhere",
    "route53",
    "route53-recovery-cluster",
    "route53-recovery-control-config",
    "route53-recovery-readiness",
    "route53domains",
    "route53resolver",
    "rum",
    "s3",
    "s3control",
    "s3outposts",
    "sagemaker",
    "sagemaker-a2i-runtime",
    "sagemaker-edge",
    "sagemaker-featurestore-runtime",
    "sagemaker-runtime",
    "savingsplans",
    "scheduler",
    "schemas",
    "secretsmanager",
    "securityhub",
    "serverlessrepo",
    "service-quotas",
    "servicecatalog",
    "servicecatalog-appregistry",
    "servicediscovery",
    "ses",
    "sesv2",
    "shield",
    "signer",
    "simspaceweaver",
    "sms",
    "snow-device-management",
    "snowball",
    "sns",
    "sqs",
    "ssm",
    "ssm-contacts",
    "ssm-incidents",
    "sso",
    "sso-admin",
    "sso-oidc",
    "stepfunctions",
    "storagegateway",
    "sts",
    "support",
    "support-app",
    "swf",
    "synthetics",
    "textract",
    "timestream-query",
    "timestream-write",
    "transcribe",
    "transfer",
    "translate",
    "verifiedpermissions",
    "voice-id",
    "vpc-lattice",
    "waf",
    "waf-regional",
    "wafv2",
    "wellarchitected",
    "wisdom",
    "workdocs",
    "worklink",
    "workmail",
    "workmailmessageflow",
    "workspaces",
    "xray"
]
AZURE_SERVICES = [
    "ad",
    "apimanagement",
    "appconfiguration",
    "automation",
    "backup",
    "batch",
    "blueprint",
    "blueprintassignment",
    "cdn",
    "cognitiveservices",
    "compute",
    "confidentialledger",
    "containerinstance",
    "containerservice",
    "cosmos-db",
    "databricks",
    "devtestlabs",
    "dns",
    "eventhub",
    "expressroute",
    "frontdoor",
    "hdinsight",
    "insights",
    "iothub",
    "keyvault",
    "keyvaultaccess",
    "logic",
    "machinelearning",
    "managedidentity",
    "maps",
    "media",
    "migrate",
    "monitor",
    "network",
    "notificationhubs",
    "powerbi",
    "redis",
    "resources",
    "scheduler",
    "search",
    "security",
    "servicebus",
    "signalr",
    "sql",
    "storage",
    "synapse",
    "web",
    "webpubsub"
]

GCP_DISCOVERY_URL = "https://discovery.googleapis.com/discovery/v1/apis"
AZURE_SPEC_ROOT = "https://api.github.com/repos/Azure/azure-rest-api-specs/contents/specification"

PROVIDER_DEFAULTS = {
    "gcp": GCP_SERVICES,
    "aws": AWS_SERVICES,
    "azure": AZURE_SERVICES
}


def fetch_provider_services(provider):
    try:
        if provider == "aws":
            session = botocore.session.get_session()
            return sorted(session.get_available_services())
        if provider == "gcp":
            resp = requests.get(GCP_DISCOVERY_URL, timeout=20)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            return sorted({item.get("name") for item in items if item.get("name")})
        if provider == "azure":
            headers = {"Accept": "application/vnd.github.v3+json"}
            resp = requests.get(AZURE_SPEC_ROOT, headers=headers, timeout=20)
            resp.raise_for_status()
            entries = resp.json()
            return sorted({entry.get("name") for entry in entries if entry.get("type") == "dir"})
    except Exception as exc:
        print(f"⚠️ Could not refresh {provider.upper()} services automatically: {exc}")
    return []


def get_service_list(provider, service_cache):
    defaults = PROVIDER_DEFAULTS.get(provider, [])
    previous = service_cache.get(provider, [])
    refreshed = fetch_provider_services(provider)
    cache_dirty = False

    if refreshed:
        refreshed_clean = sorted({svc for svc in refreshed if svc})
        prev_set = {svc.lower() for svc in previous}
        refreshed_set = {svc.lower() for svc in refreshed_clean}
        if previous and prev_set == refreshed_set:
            print(f"ℹ️ List of {provider.upper()} services are up to date.")
        else:
            added = sorted(refreshed_set - prev_set)
            removed = sorted(prev_set - refreshed_set)
            if added:
                print(f"ℹ️ Added {len(added)} new {provider.upper()} services from live catalog.")
            elif not previous:
                print(f"ℹ️ Retrieved {len(refreshed_clean)} {provider.upper()} services from live catalog.")
            if removed:
                print(f"ℹ️ {len(removed)} {provider.upper()} services were removed from the live catalog.")
        service_cache[provider] = refreshed_clean
        cache_dirty = True
        active_list = refreshed_clean
    else:
        if previous:
            print(f"⚠️ Using cached {provider.upper()} services list; live refresh unavailable.")
            active_list = previous
        elif defaults:
            print(f"⚠️ Using bundled {provider.upper()} services list; live refresh unavailable.")
            active_list = defaults
        else:
            print(f"⚠️ No known services for provider '{provider}'.")
            active_list = []

    return sorted(active_list), cache_dirty


def format_service_table(services, columns=4):
    if not services:
        return ""
    col_width = min(max(len(s) for s in services) + 2, 30)
    rows = []
    for idx in range(0, len(services), columns):
        row = services[idx: idx + columns]
        rows.append("".join(name.ljust(col_width) for name in row))
    return "\n".join(rows)
from extractors.gcp_extractor import extract_gcp_service_apis
from extractors.aws_extractor import extract_aws_service_apis
from extractors.azure_extractor import extract_azure_service_apis
from writer.excel_writer import write_to_excel

EXTRACTOR_MAP = {
    "gcp": extract_gcp_service_apis,
    "aws": extract_aws_service_apis,
    "azure": extract_azure_service_apis,
}


def prompt_for_related_aws_variants(selected_service, available_services, auto_accept_all=False):
    normalized = selected_service.lower()
    root = normalized.split("-", 1)[0]

    def is_related(candidate):
        candidate_lower = candidate.lower()
        if candidate_lower == normalized:
            return False
        if candidate_lower.startswith(normalized):
            return True
        candidate_root = candidate_lower.split("-", 1)[0]
        return candidate_root == root and candidate_lower != normalized

    related = [svc for svc in available_services if is_related(svc)]
    if not related:
        return [(selected_service, selected_service)]

    if auto_accept_all:
        return [(selected_service, selected_service)] + [(svc, svc) for svc in related]

    print(f"ℹ️ The '{selected_service}' family includes additional AWS services: {', '.join(related)}")
    while True:
        choice = input(
            "Include these related services as well? (Press Enter/yes for all, 'no' to keep only the base, or enter comma-separated names): "
        ).strip()
        if choice.lower() in {"", "yes", "y"}:
            return [(selected_service, selected_service)] + [(svc, svc) for svc in related]
        if choice.lower() in {"no", "n"}:
            return [(selected_service, selected_service)]

        requested = [item.strip() for item in choice.split(",") if item.strip()]
        invalid = [svc for svc in requested if svc not in related]
        if invalid:
            print(f"❌ Unknown related services: {', '.join(invalid)}. Please choose from: {', '.join(related)}.")
            continue
        unique_requested = []
        for svc in requested:
            if svc not in unique_requested:
                unique_requested.append(svc)
        return [(selected_service, selected_service)] + [(svc, svc) for svc in unique_requested]


def fetch_gcp_service_versions(service):
    try:
        resp = requests.get(GCP_DISCOVERY_URL, timeout=20)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as exc:
        print(f"⚠️ Could not retrieve GCP versions for '{service}': {exc}")
        return []

    versions = sorted({item.get("version") for item in items if item.get("name", "").lower() == service.lower() and item.get("version")})
    return versions


def prompt_for_gcp_versions(service):
    versions = fetch_gcp_service_versions(service)
    if not versions:
        return [(service, service)]

    if len(versions) == 1:
        version = versions[0]
        return [(f"{service}@{version}", f"{service} ({version})")]

    ordered_versions = sorted(
        versions,
        key=lambda ver: (("beta" in ver.lower()) or ("alpha" in ver.lower()), ver),
    )
    print(f"ℹ️ '{service}' has multiple versions available:")
    for idx, ver in enumerate(ordered_versions, start=1):
        print(f"  [{idx}] {ver}")

    default_version = next((ver for ver in ordered_versions if "beta" not in ver.lower() and "alpha" not in ver.lower()), ordered_versions[0])

    while True:
        prompt = input(
            f"Select version number (e.g., 1), enter comma-separated numbers for multiple versions, type 'all', or press Enter for '{default_version}': "
        ).strip().lower()
        if not prompt:
            return [(f"{service}@{default_version}", f"{service} ({default_version})")]
        if prompt in {"all", "a"}:
            return [(f"{service}@{ver}", f"{service} ({ver})") for ver in ordered_versions]
        selections = [item.strip() for item in prompt.split(",") if item.strip()]
        chosen = []
        invalid = []
        for selection in selections:
            if not selection.isdigit():
                invalid.append(selection)
                continue
            idx = int(selection)
            if not (1 <= idx <= len(ordered_versions)):
                invalid.append(selection)
                continue
            ver = ordered_versions[idx - 1]
            if ver not in chosen:
                chosen.append(ver)
        if invalid:
            print(f"❌ Invalid selection(s): {', '.join(invalid)}. Please try again.")
            continue
        if not chosen:
            print("Please select at least one version.")
            continue
        return [(f"{service}@{ver}", f"{service} ({ver})") for ver in chosen]


def main():
    print("📡 Extracting CSP APIs and writing to Excel...")

    project_root = Path(__file__).resolve().parent
    default_output_dir = project_root / "OUTPUT_FILES"
    try:
        default_output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"❌ Unable to create default output directory '{default_output_dir}': {exc}")
        return

    service_cache = load_service_cache()

    provider = input("Enter CSP (e.g. aws, gcp, azure): ").strip().lower()
    if provider not in PROVIDER_DEFAULTS:
        print(f"❌ Unsupported provider '{provider}'.")
        return

    available_services, service_cache_dirty = get_service_list(provider, service_cache)
    if service_cache_dirty:
        save_service_cache(service_cache)

    service_lookup = {svc.lower(): svc for svc in available_services}

    list_prompt = "(press L to get list of services)"
    service_prompt = f"Enter {provider} service {list_prompt}: "
    list_command = {"l"}

    while True:
        service_input = input(service_prompt).strip()
        if not service_input:
            print("Please enter a service name.")
            continue
        if service_input.lower() in list_command:
            if available_services:
                table = format_service_table(available_services)
                if table:
                    print(f"Available {provider.upper()} services:\n{table}")
                else:
                    print(f"Available {provider.upper()} services: {', '.join(available_services)}")
            else:
                print(f"No cached list available for {provider.upper()} yet.")
            service_prompt = f"Enter {provider} service: "
            continue
        break

    service_key = service_input.lower()
    if service_key in service_lookup:
        service = service_lookup[service_key]
    else:
        service = service_input
        if available_services:
            print(f"⚠️ '{service_input}' not found in refreshed {provider.upper()} services. Continuing anyway.")

    safe_service_name = "".join(ch if ch.isalnum() else "-" for ch in service).strip("-") or f"{provider}-service"
    safe_service_name = "-".join(filter(None, safe_service_name.split("-")))
    default_output_file = f"{provider}-{safe_service_name.lower()}-api-extract.xlsx"

    while True:
        accept_default = input(
            f"Use default output file '{default_output_file}'? (Press Enter/yes to accept, no to change): "
        ).strip().lower()
        if accept_default in {"", "yes", "y"}:
            output_file = default_output_file
            break
        if accept_default in {"no", "n"}:
            output_file = input("Enter output Excel file name (without extension optional): ").strip()
            while not output_file:
                output_file = input("File name cannot be empty. Enter output Excel file name: ").strip()
            break
        print("Please respond with 'Press Enter/yes' or 'no'.")

    if not output_file.endswith(".xlsx"):
        output_file += ".xlsx"

    while True:
        save_to_default = input("Save Excel file to OUTPUT_FILES? (Press Enter/yes for default folder, no for custom path): ").strip().lower()
        if save_to_default in {"", "yes", "y"}:
            output_path = default_output_dir / output_file
            break
        if save_to_default in {"no", "n"}:
            custom_destination = input("Enter the directory or full file path for the Excel file: ").strip()
            while not custom_destination:
                custom_destination = input("Path cannot be empty. Enter the directory or full file path: ").strip()
            custom_path = Path(custom_destination).expanduser()
            if custom_path.suffix.lower() == ".xlsx":
                custom_path.parent.mkdir(parents=True, exist_ok=True)
                output_path = custom_path
            else:
                custom_path.mkdir(parents=True, exist_ok=True)
                output_path = custom_path / output_file
            break
        print("Please respond with 'Press Enter/yes' or 'no'.")

    output_path = output_path.resolve()

    extractor = EXTRACTOR_MAP.get(provider)
    if extractor is None:
        print(f"❌ No extractor configured for provider '{provider}'.")
        return

    if provider == "aws":
        service_variants = prompt_for_related_aws_variants(service, available_services)
    elif provider == "gcp":
        service_variants = prompt_for_gcp_versions(service)
    else:
        service_variants = [(service, service)]

    variant_runs = []
    for actual_service, display_service in service_variants:
        label = display_service or actual_service
        try:
            tree_data = extractor(actual_service)
        except RuntimeError as exc:
            print(f"❌ {exc}")
            continue
        except Exception as exc:
            print(f"❌ Unexpected error while extracting {provider.upper()} APIs for '{actual_service}': {exc}")
            continue

        if not tree_data:
            print(f"⚠️ No API methods were returned for '{actual_service}'.")
            continue

        variant_runs.append({
            "key": actual_service,
            "label": label,
            "data": tree_data,
        })

    if not variant_runs:
        print("⚠️ Extraction completed but produced no data. Excel files were not created.")
        return

    try:
        write_to_excel(variant_runs, str(output_path), provider)
    except PermissionError:
        print(f"❌ Unable to write to '{output_path}'. Close the file if it's open and try again.")
        return
    except OSError as exc:
        print(f"❌ Failed to write Excel file '{output_path}': {exc}")
        return

    print(f"✅ Done! API structure saved to: {output_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except EOFError:
        print("\n❌ Input stream closed unexpectedly. Please rerun the command.")
