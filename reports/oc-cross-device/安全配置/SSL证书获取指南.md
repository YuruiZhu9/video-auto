# SSL 证书获取指南

## 方案一：Let's Encrypt（免费，推荐）

### 方式 A：certbot 自动（Nginx）
```bash
# 安装 certbot
apt update && apt install -y certbot python3-certbot-nginx

# 自动获取证书 + 配置 Nginx
certbot --nginx -d oc.example.com
```

### 方式 B：standalone（不依赖 Nginx）
```bash
certbot certonly --standalone -d oc.example.com --agree-tos -m your@email.com --non-interactive
```

### 方式 C：Caddy 自动（HTTPS 自动配置）
```bash
# Caddy 默认自动申请 Let's Encrypt 证书（仅需开放 80 端口）
# 直接配置 Caddyfile 然后运行即可
caddy run --config Caddyfile
```

## 方案二：acme.sh（轻量，推荐内网/IP）

```bash
# 安装
curl https://get.acme.sh | sh

# 申请证书（阿里云 DNS API 示例）
export Ali_Key="your_ali_key"
export Ali_Secret="your_ali_secret"

~/.acme.sh/acme.sh --issue --dns dns_ali -d oc.example.com

# 安装证书到指定目录
~/.acme.sh/acme.sh --install-cert -d oc.example.com \
  --key-file /etc/ssl/private/oc.key \
  --fullchain-file /etc/ssl/certs/oc.crt \
  --reloadcmd "systemctl reload nginx"
```

## 方案三：自签名证书（仅开发测试）

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/oc-selfsigned.key \
  -out /etc/ssl/certs/oc-selfsigned.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=OpenClaw/OU=Control/CN=your-server-ip"

# Nginx 中配置：
# ssl_certificate     /etc/ssl/certs/oc-selfsigned.crt;
# ssl_certificate_key /etc/ssl/private/oc-selfsigned.key;
```

## 证书文件位置（对应 Nginx 配置）

```
ssl_certificate     /etc/letsencrypt/live/oc.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/oc.example.com/privkey.pem;
```

## 证书自动续期

Let's Encrypt 证书有效期 90 天，certbot/caddy 默认自动续期：
```bash
# certbot 续期测试
certbot renew --dry-run

# acme.sh 自动续期（安装时已配置 cron 任务）
~/.acme.sh/acme.sh --cron
```
