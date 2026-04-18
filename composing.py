import os
import secrets
import string

CYPHER_NETWORK = "cypher_net"

def _random_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def _base_network() -> str:
    return f"""
networks:
  {CYPHER_NETWORK}:
    external: true
"""

def generate_n8n(config: dict) -> str:
    port = config["port"]
    host = config["host"]
    protocol = config.get("protocol", "http")
    webhook_url = f"{protocol}://{host}:{port}"
    
    return f"""version: "3.8"

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: cypher_n8n
    restart: unless-stopped
    ports:
      - "{port}:5678"
    environment:
      - N8N_HOST={host}
      - N8N_PORT=5678
      - N8N_PROTOCOL={protocol}
      - NODE_ENV=production
      - WEBHOOK_URL={webhook_url}/
      - GENERIC_TIMEZONE=UTC
      - N8N_ENCRYPTION_KEY={_random_password()}
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - {CYPHER_NETWORK}

volumes:
  n8n_data:
{_base_network()}"""

def generate_supabase(config: dict) -> str:
    port = config["port"]
    db_password = _random_password()
    jwt_secret = _random_password(40)
    anon_key = _random_password(48)
    service_key = _random_password(48)
    
    return f"""version: "3.8"

services:
  supabase_db:
    image: supabase/postgres:15.1.0.117
    container_name: cypher_supabase_db
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: {db_password}
      POSTGRES_DB: postgres
    volumes:
      - supabase_db_data:/var/lib/postgresql/data
    networks:
      - {CYPHER_NETWORK}

  supabase_kong:
    image: kong:2.8.1
    container_name: cypher_supabase_kong
    restart: unless-stopped
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: /var/lib/kong/kong.yml
      KONG_DNS_ORDER: LAST,A,CNAME
      KONG_PLUGINS: request-transformer,cors,key-auth,acl
    volumes:
      - supabase_kong_config:/var/lib/kong
    networks:
      - {CYPHER_NETWORK}

  supabase_auth:
    image: supabase/gotrue:v2.132.3
    container_name: cypher_supabase_auth
    restart: unless-stopped
    environment:
      GOTRUE_API_HOST: 0.0.0.0
      GOTRUE_API_PORT: 9999
      API_EXTERNAL_URL: http://{config["host"]}:{port}
      GOTRUE_DB_DRIVER: postgres
      GOTRUE_DB_DATABASE_URL: postgres://supabase_auth_admin:{db_password}@supabase_db:5432/postgres
      GOTRUE_SITE_URL: http://{config["host"]}:{port}
      GOTRUE_JWT_SECRET: {jwt_secret}
      GOTRUE_JWT_EXP: 3600
      GOTRUE_DISABLE_SIGNUP: "false"
    depends_on:
      - supabase_db
    networks:
      - {CYPHER_NETWORK}

  supabase_rest:
    image: postgrest/postgrest:v12.0.2
    container_name: cypher_supabase_rest
    restart: unless-stopped
    environment:
      PGRST_DB_URI: postgres://authenticator:{db_password}@supabase_db:5432/postgres
      PGRST_DB_SCHEMAS: public,storage,graphql_public
      PGRST_DB_ANON_ROLE: anon
      PGRST_JWT_SECRET: {jwt_secret}
      PGRST_DB_USE_LEGACY_GUCS: "false"
    depends_on:
      - supabase_db
    networks:
      - {CYPHER_NETWORK}

  supabase_studio:
    image: supabase/studio:20240205-6a02b87
    container_name: cypher_supabase_studio
    restart: unless-stopped
    ports:
      - "{port}:3000"
    environment:
      STUDIO_PG_META_URL: http://supabase_meta:8080
      POSTGRES_PASSWORD: {db_password}
      DEFAULT_ORGANIZATION_NAME: cypher
      DEFAULT_PROJECT_NAME: default
      SUPABASE_URL: http://supabase_kong:8000
      SUPABASE_PUBLIC_URL: http://{config["host"]}:{port}
      SUPABASE_ANON_KEY: {anon_key}
      SUPABASE_SERVICE_KEY: {service_key}
    depends_on:
      - supabase_kong
    networks:
      - {CYPHER_NETWORK}

  supabase_meta:
    image: supabase/postgres-meta:v0.80.0
    container_name: cypher_supabase_meta
    restart: unless-stopped
    environment:
      PG_META_PORT: 8080
      PG_META_DB_HOST: supabase_db
      PG_META_DB_PASSWORD: {db_password}
    depends_on:
      - supabase_db
    networks:
      - {CYPHER_NETWORK}

volumes:
  supabase_db_data:
  supabase_kong_config:
{_base_network()}"""

def generate_kong(config: dict) -> str:
    port = config["port"]
    admin_port = config.get("admin_port", port + 1)
    db_password = _random_password()
    
    return f"""version: "3.8"

services:
  kong_db:
    image: postgres:16-alpine
    container_name: cypher_kong_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: kong
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: {db_password}
    volumes:
      - kong_db_data:/var/lib/postgresql/data
    networks:
      - {CYPHER_NETWORK}

  kong_migration:
    image: kong:3.6
    container_name: cypher_kong_migration
    command: kong migrations bootstrap
    restart: on-failure
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong_db
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: {db_password}
      KONG_PG_DATABASE: kong
    depends_on:
      - kong_db
    networks:
      - {CYPHER_NETWORK}

  kong:
    image: kong:3.6
    container_name: cypher_kong
    restart: unless-stopped
    ports:
      - "{port}:8000"
      - "{admin_port}:8001"
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong_db
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: {db_password}
      KONG_PG_DATABASE: kong
      KONG_PROXY_ACCESS_LOG: /dev/null
      KONG_ADMIN_ACCESS_LOG: /dev/null
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
    depends_on:
      - kong_migration
    networks:
      - {CYPHER_NETWORK}

volumes:
  kong_db_data:
{_base_network()}"""

def generate_mailcow(config: dict) -> str:
    host = config["host"]
    
    return f"""version: "3.8"

services:
  mailcow_nginx:
    image: nginx:alpine
    container_name: cypher_mailcow_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - mailcow_nginx_conf:/etc/nginx/conf.d
      - mailcow_certs:/etc/ssl/mailcow
    networks:
      - {CYPHER_NETWORK}

  mailcow_mysql:
    image: mariadb:10.11
    container_name: cypher_mailcow_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: {_random_password()}
      MYSQL_DATABASE: mailcow
      MYSQL_USER: mailcow
      MYSQL_PASSWORD: {_random_password()}
    volumes:
      - mailcow_mysql_data:/var/lib/mysql
    networks:
      - {CYPHER_NETWORK}

  mailcow_postfix:
    image: mailcow/postfix:1.67
    container_name: cypher_mailcow_postfix
    restart: unless-stopped
    ports:
      - "25:25"
      - "587:587"
      - "465:465"
    environment:
      MAILCOW_HOSTNAME: {host}
    volumes:
      - mailcow_postfix_data:/var/spool/postfix
    networks:
      - {CYPHER_NETWORK}

  mailcow_dovecot:
    image: mailcow/dovecot:1.3
    container_name: cypher_mailcow_dovecot
    restart: unless-stopped
    ports:
      - "993:993"
      - "995:995"
      - "143:143"
      - "110:110"
    volumes:
      - mailcow_vmail:/var/vmail
    networks:
      - {CYPHER_NETWORK}

volumes:
  mailcow_nginx_conf:
  mailcow_certs:
  mailcow_mysql_data:
  mailcow_postfix_data:
  mailcow_vmail:
{_base_network()}"""

def generate_mattermost(config: dict) -> str:
    port = config["port"]
    db_password = _random_password()
    
    return f"""version: "3.8"

services:
  mattermost_db:
    image: postgres:15-alpine
    container_name: cypher_mattermost_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: mattermost
      POSTGRES_USER: mattermost
      POSTGRES_PASSWORD: {db_password}
    volumes:
      - mattermost_db_data:/var/lib/postgresql/data
    networks:
      - {CYPHER_NETWORK}

  mattermost:
    image: mattermost/mattermost-team-edition:latest
    container_name: cypher_mattermost
    restart: unless-stopped
    ports:
      - "{port}:8065"
    environment:
      MM_SQLSETTINGS_DRIVERNAME: postgres
      MM_SQLSETTINGS_DATASOURCE: postgres://mattermost:{db_password}@mattermost_db:5432/mattermost?sslmode=disable&connect_timeout=10
      MM_BLEVESETTINGS_INDEXDIR: /mattermost/bleve-indexes
      MM_SERVICESETTINGS_SITEURL: http://{config["host"]}:{port}
    volumes:
      - mattermost_data:/mattermost/data
      - mattermost_logs:/mattermost/logs
      - mattermost_config:/mattermost/config
      - mattermost_plugins:/mattermost/plugins
      - mattermost_client_plugins:/mattermost/client/plugins
      - mattermost_bleve:/mattermost/bleve-indexes
    depends_on:
      - mattermost_db
    networks:
      - {CYPHER_NETWORK}

volumes:
  mattermost_db_data:
  mattermost_data:
  mattermost_logs:
  mattermost_config:
  mattermost_plugins:
  mattermost_client_plugins:
  mattermost_bleve:
{_base_network()}"""

def generate_jenkins(config: dict) -> str:
    port = config["port"]
    agent_port = config.get("agent_port", 50000)
    
    return f"""version: "3.8"

services:
  jenkins:
    image: jenkins/jenkins:lts-jdk17
    container_name: cypher_jenkins
    restart: unless-stopped
    ports:
      - "{port}:8080"
      - "{agent_port}:50000"
    environment:
      JENKINS_OPTS: --httpPort=8080
      JAVA_OPTS: "-Djenkins.install.runSetupWizard=false"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    user: root
    networks:
      - {CYPHER_NETWORK}

volumes:
  jenkins_home:
{_base_network()}"""

def generate_gitea(config: dict) -> str:
    port = config["port"]
    ssh_port = config.get("ssh_port", 2222)
    db_password = _random_password()
    
    return f"""version: "3.8"

services:
  gitea_db:
    image: postgres:15-alpine
    container_name: cypher_gitea_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: gitea
      POSTGRES_USER: gitea
      POSTGRES_PASSWORD: {db_password}
    volumes:
      - gitea_db_data:/var/lib/postgresql/data
    networks:
      - {CYPHER_NETWORK}

  gitea:
    image: gitea/gitea:latest
    container_name: cypher_gitea
    restart: unless-stopped
    ports:
      - "{port}:3000"
      - "{ssh_port}:22"
    environment:
      USER_UID: 1000
      USER_GID: 1000
      GITEA__database__DB_TYPE: postgres
      GITEA__database__HOST: gitea_db:5432
      GITEA__database__NAME: gitea
      GITEA__database__USER: gitea
      GITEA__database__PASSWD: {db_password}
      GITEA__server__HTTP_PORT: 3000
      GITEA__server__ROOT_URL: http://{config["host"]}:{port}
      GITEA__server__DOMAIN: {config["host"]}
    volumes:
      - gitea_data:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    depends_on:
      - gitea_db
    networks:
      - {CYPHER_NETWORK}

volumes:
  gitea_db_data:
  gitea_data:
{_base_network()}"""

def generate_gitlab(config: dict) -> str:
    port = config["port"]
    ssh_port = config.get("ssh_port", 2224)
    host = config["host"]
    
    return f"""version: "3.8"

services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: cypher_gitlab
    restart: unless-stopped
    hostname: {host}
    ports:
      - "{port}:80"
      - "{ssh_port}:22"
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://{host}:{port}'
        gitlab_rails['gitlab_shell_ssh_port'] = {ssh_port}
        nginx['listen_port'] = 80
        nginx['listen_https'] = false
        prometheus_monitoring['enable'] = false
        gitlab_rails['smtp_enable'] = false
    volumes:
      - gitlab_config:/etc/gitlab
      - gitlab_logs:/var/log/gitlab
      - gitlab_data:/var/opt/gitlab
    shm_size: 256m
    networks:
      - {CYPHER_NETWORK}

volumes:
  gitlab_config:
  gitlab_logs:
  gitlab_data:
{_base_network()}"""

def generate_jitsi(config: dict) -> str:
    port = config["port"]
    host = config["host"]
    jicofo_secret = _random_password(16)
    jvb_secret = _random_password(16)
    jigasi_secret = _random_password(16)
    
    return f"""version: "3.8"

services:
  jitsi_prosody:
    image: jitsi/prosody:stable-9111
    container_name: cypher_jitsi_prosody
    restart: unless-stopped
    expose:
      - "5222"
      - "5347"
      - "5280"
    environment:
      PUBLIC_URL: http://{host}:{port}
      JICOFO_AUTH_PASSWORD: {jicofo_secret}
      JVB_AUTH_PASSWORD: {jvb_secret}
      JIGASI_XMPP_PASSWORD: {jigasi_secret}
      ENABLE_AUTH: 0
      ENABLE_GUESTS: 1
      TZ: UTC
    volumes:
      - jitsi_prosody_config:/config
      - jitsi_prosody_plugins:/prosody-plugins-custom
    networks:
      - {CYPHER_NETWORK}

  jitsi_jicofo:
    image: jitsi/jicofo:stable-9111
    container_name: cypher_jitsi_jicofo
    restart: unless-stopped
    environment:
      AUTH_TYPE: internal
      XMPP_SERVER: jitsi_prosody
      XMPP_DOMAIN: meet.jitsi
      XMPP_AUTH_DOMAIN: auth.meet.jitsi
      XMPP_INTERNAL_MUC_DOMAIN: internal-muc.meet.jitsi
      JICOFO_AUTH_PASSWORD: {jicofo_secret}
      JVB_BREWERY_MUC: jvbbrewery
      TZ: UTC
    depends_on:
      - jitsi_prosody
    networks:
      - {CYPHER_NETWORK}

  jitsi_jvb:
    image: jitsi/jvb:stable-9111
    container_name: cypher_jitsi_jvb
    restart: unless-stopped
    ports:
      - "10000:10000/udp"
    environment:
      XMPP_SERVER: jitsi_prosody
      XMPP_DOMAIN: meet.jitsi
      XMPP_AUTH_DOMAIN: auth.meet.jitsi
      XMPP_INTERNAL_MUC_DOMAIN: internal-muc.meet.jitsi
      JVB_AUTH_PASSWORD: {jvb_secret}
      JVB_BREWERY_MUC: jvbbrewery
      JVB_PORT: 10000
      JVB_TCP_HARVESTER_DISABLED: "true"
      PUBLIC_URL: http://{host}:{port}
      TZ: UTC
    depends_on:
      - jitsi_prosody
    networks:
      - {CYPHER_NETWORK}

  jitsi_web:
    image: jitsi/web:stable-9111
    container_name: cypher_jitsi_web
    restart: unless-stopped
    ports:
      - "{port}:80"
    environment:
      PUBLIC_URL: http://{host}:{port}
      XMPP_SERVER: jitsi_prosody
      XMPP_DOMAIN: meet.jitsi
      XMPP_AUTH_DOMAIN: auth.meet.jitsi
      XMPP_BOSH_URL_BASE: http://jitsi_prosody:5280
      XMPP_MUC_DOMAIN: muc.meet.jitsi
      JICOFO_AUTH_PASSWORD: {jicofo_secret}
      TZ: UTC
      ENABLE_LETSENCRYPT: 0
    depends_on:
      - jitsi_prosody
    volumes:
      - jitsi_web_config:/config
      - jitsi_web_transcripts:/usr/share/jitsi-meet/transcripts
    networks:
      - {CYPHER_NETWORK}

volumes:
  jitsi_prosody_config:
  jitsi_prosody_plugins:
  jitsi_web_config:
  jitsi_web_transcripts:
{_base_network()}"""

def generate_openproject(config: dict) -> str:
    port = config["port"]
    db_password = _random_password()
    secret_key = _random_password(32)
    
    return f"""version: "3.8"

services:
  openproject_db:
    image: postgres:13-alpine
    container_name: cypher_openproject_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: openproject
      POSTGRES_USER: openproject
      POSTGRES_PASSWORD: {db_password}
    volumes:
      - openproject_db_data:/var/lib/postgresql/data
    networks:
      - {CYPHER_NETWORK}

  openproject_cache:
    image: memcached:latest
    container_name: cypher_openproject_cache
    restart: unless-stopped
    networks:
      - {CYPHER_NETWORK}

  openproject:
    image: openproject/openproject:14
    container_name: cypher_openproject
    restart: unless-stopped
    ports:
      - "{port}:80"
    environment:
      DATABASE_URL: postgres://openproject:{db_password}@openproject_db/openproject
      RAILS_CACHE_STORE: memcache
      MEMCACHE_SERVERS: openproject_cache:11211
      SECRET_KEY_BASE: {secret_key}
      RAILS_MIN_THREADS: 4
      RAILS_MAX_THREADS: 16
      OPENPROJECT_HOST__NAME: {config["host"]}:{port}
      OPENPROJECT_HTTPS: "false"
    volumes:
      - openproject_assets:/var/openproject/assets
      - openproject_config:/app/config/configuration.yml
    depends_on:
      - openproject_db
      - openproject_cache
    networks:
      - {CYPHER_NETWORK}

volumes:
  openproject_db_data:
  openproject_assets:
  openproject_config:
{_base_network()}"""

GENERATORS = {
    "n8n": generate_n8n,
    "supabase": generate_supabase,
    "kong": generate_kong,
    "mailcow": generate_mailcow,
    "mattermost": generate_mattermost,
    "jenkins": generate_jenkins,
    "gitea": generate_gitea,
    "gitlab": generate_gitlab,
    "jitsi": generate_jitsi,
    "openproject": generate_openproject,
}

def generate_compose(service: str, config: dict) -> str:
    generator = GENERATORS.get(service)
    if not generator:
        raise ValueError(f"No compose generator found for service: {service}")
    return generator(config)

def write_compose_file(service: str, config: dict, directory: str) -> str:
    content = generate_compose(service, config)
    path = os.path.join(directory, "docker-compose.yml")
    with open(path, "w") as f:
        f.write(content)
    return path