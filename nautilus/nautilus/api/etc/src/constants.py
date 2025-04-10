

class WorkDir:
    WORKSPACE = "workspace"
    WIP = "wip_dir"
    STATE = "state_dir"
    RESOURCES = "resources_dir"
    CURRENT_PROD_DIR = "current_prod_dir"


class ParticipantType:
    SERVER = "server"
    CLIENT = "client"
    ADMIN = "admin"
    OVERSEER = "overseer"


class PropKey:
    API_VERSION = "api_version"
    NAME = "name"
    DESCRIPTION = "description"
    ROLE = "role"
    HOST_NAMES = "host_names"
    CONNECT_TO = "connect_to"
    LISTENING_HOST = "listening_host"
    DEFAULT_HOST = "default_host"
    PROTOCOL = "protocol"
    API_ROOT = "api_root"
    PORT = "port"
    OVERSEER_END_POINT = "overseer_end_point"
    ADMIN_PORT = "admin_port"
    FED_LEARN_PORT = "fed_learn_port"


class CtxKey(WorkDir, PropKey):
    PROJECT = "__project__"
    TEMPLATE = "__template__"
    PROVISION_MODE = "__provision_model__"
    LAST_PROD_STAGE = "last_prod_stage"
    TEMPLATE_FILES = "template_files"
    SERVER_NAME = "server_name"
    ROOT_CERT = "root_cert"
    ROOT_PRI_KEY = "root_pri_key"


class ProvisionMode:
    POC = "poc"
    NORMAL = "normal"


class AdminRole:
    PROJECT_ADMIN = "project_admin"
    ORG_ADMIN = "org_admin"
    LEAD = "lead"
    MEMBER = "member"


class OverseerRole:
    SERVER = "server"
    CLIENT = "client"
    ADMIN = "admin"


class TemplateSectionKey:
    START_SERVER_SH = "start_svr_sh"
    START_CLIENT_SH = "start_cln_sh"
    DOCKER_SERVER_SH = "docker_svr_sh"
    DOCKER_CLIENT_SH = "docker_cln_sh"
    DOCKER_ADMIN_SH = "docker_adm_sh"
    GUNICORN_CONF_PY = "gunicorn_conf_py"
    START_OVERSEER_SH = "start_ovsr_sh"
    FED_SERVER = "fed_server"
    FED_CLIENT = "fed_client"
    SUB_START_SH = "sub_start_sh"
    STOP_FL_SH = "stop_fl_sh"
    LOG_CONFIG = "log_config"
    LOCAL_SERVER_RESOURCES = "local_server_resources"
    LOCAL_CLIENT_RESOURCES = "local_client_resources"
    SAMPLE_PRIVACY = "sample_privacy"
    DEFAULT_AUTHZ = "default_authz"
    SERVER_README = "readme_fs"
    CLIENT_README = "readme_fc"
    ADMIN_README = "readme_am"
    FL_ADMIN_SH = "fl_admin_sh"
    FED_ADMIN = "fed_admin"
    COMPOSE_YAML = "compose_yaml"
    DOCKERFILE = "dockerfile"
    HELM_CHART_CHART = "helm_chart_chart"
    HELM_CHART_VALUES = "helm_chart_values"
    HELM_CHART_SERVICE_OVERSEER = "helm_chart_service_overseer"
    HELM_CHART_SERVICE_SERVER = "helm_chart_service_server"
    HELM_CHART_DEPLOYMENT_OVERSEER = "helm_chart_deployment_overseer"
    HELM_CHART_DEPLOYMENT_SERVER = "helm_chart_deployment_server"


class ProvFileName:
    START_SH = "start.sh"
    SUB_START_SH = "sub_start.sh"
    PRIVILEGE_YML = "privilege.yml"
    DOCKER_SH = "docker.sh"
    GUNICORN_CONF_PY = "gunicorn.conf.py"
    FED_SERVER_JSON = "fed_server.json"
    FED_CLIENT_JSON = "fed_client.json"
    STOP_FL_SH = "stop_fl.sh"
    LOG_CONFIG_DEFAULT = "log_config.json.default"
    RESOURCES_JSON_DEFAULT = "resources.json.default"
    PRIVACY_JSON_SAMPLE = "privacy.json.sample"
    AUTHORIZATION_JSON_DEFAULT = "authorization.json.default"
    README_TXT = "readme.txt"
    FED_ADMIN_JSON = "fed_admin.json"
    FL_ADMIN_SH = "fl_admin.sh"
    SIGNATURE_JSON = "signature.json"
    COMPOSE_YAML = "compose.yaml"
    ENV = ".env"
    COMPOSE_BUILD_DIR = "nvflare_compose"
    DOCKERFILE = "Dockerfile"
    REQUIREMENTS_TXT = "requirements.txt"
    SERVER_CONTEXT_TENSEAL = "server_context.tenseal"
    CLIENT_CONTEXT_TENSEAL = "client_context.tenseal"
    HELM_CHART_DIR = "nvflare_hc"
    DEPLOYMENT_OVERSEER_YAML = "deployment_overseer.yaml"
    SERVICE_OVERSEER_YAML = "service_overseer.yaml"
    CHART_YAML = "Chart.yaml"
    VALUES_YAML = "values.yaml"
    HELM_CHART_TEMPLATES_DIR = "templates"


class CertFileBasename:
    CLIENT = "client"
    SERVER = "server"
    OVERSEER = "overseer"
