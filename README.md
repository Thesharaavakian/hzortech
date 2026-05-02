# HzorTech

**[hzortech.com](https://hzortech.com)** — Software development, business automation, DevOps infrastructure, and security monitoring for companies that need solid technical execution without a full internal IT team.

Based in Yerevan, Armenia. Remote-first, serving clients globally.

---

## Services

| Area                               | What we do                                                      |
| ---------------------------------- | --------------------------------------------------------------- |
| **Web & Software Development**     | Corporate sites, web apps, Django backends, REST APIs           |
| **CRM Setup & Customization**      | HubSpot, custom CRM, workflow automation, integrations          |
| **Business Process Automation**    | Workflow triggers, tool integrations, notification pipelines    |
| **DevOps & Cloud Infrastructure**  | CI/CD, Docker, Kubernetes, Terraform, AWS, server migrations    |
| **API Development & Integrations** | REST APIs, webhooks, system connectors, legacy modernisation    |
| **Security Monitoring & DevSecOps** | SIEM, alerting, access control, hardening, blue team ops       |

---

## How the automation works

The entire lifecycle — from infrastructure creation to app updates — is automated through a chain of three systems: **Terraform → GitHub Actions → Kubernetes**.

```
You push code
      │
      ▼
GitHub Actions (deploy.yml)
      │
      ├─ Builds Docker image
      ├─ Pushes to ghcr.io (GitHub Container Registry)
      └─ SSHes into EC2 →
              │
              ▼
         Kubernetes (k3s on EC2)
              │
              ├─ kubectl apply -f k8s/   (applies any config changes)
              ├─ Init container runs:    python manage.py migrate --noinput
              ├─ Django pod starts:      gunicorn on port 8000
              └─ Traefik ingress routes: HTTPS → Django (cert auto-issued by cert-manager)
```

```
You push a change to terraform/
      │
      ▼
GitHub Actions (terraform.yml)
      │
      ├─ terraform apply  →  creates/updates EC2, security group, Elastic IP on AWS
      ├─ Captures IP      →  auto-writes EC2_HOST back to GitHub Secrets
      └─ SSHes into EC2 →
              │
              ├─ Waits for k3s to finish starting
              └─ Runs setup-secrets.sh  (creates Django key + DB password + Gmail in k8s)
```

After the one-time setup below, **you never touch a server again**. Every push to `master` is a full deployment.

---

## One-time setup (do this once, then everything is automatic)

### Step 1 — Create the Terraform state bucket on AWS

The bucket stores Terraform's memory of what infrastructure it has created. Run this once from your machine (install AWS CLI first if you haven't):

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region (us-east-1), output format (json)

aws s3 mb s3://hzortech-tf-state --region us-east-1

aws s3api put-bucket-versioning \
  --bucket hzortech-tf-state \
  --versioning-configuration Status=Enabled
```

### Step 2 — Generate an SSH key pair

This key is how GitHub Actions SSHes into the EC2 server:

```bash
ssh-keygen -t ed25519 -C "hzortech-deploy" -f ~/.ssh/hzortech_deploy
# Creates two files:
#   ~/.ssh/hzortech_deploy      ← private key  (EC2_SSH_KEY secret)
#   ~/.ssh/hzortech_deploy.pub  ← public key   (SSH_PUBLIC_KEY secret)

cat ~/.ssh/hzortech_deploy.pub   # copy this for SSH_PUBLIC_KEY
cat ~/.ssh/hzortech_deploy       # copy this for EC2_SSH_KEY
```

### Step 3 — Create a GitHub Personal Access Token (PAT)

This lets the Terraform workflow automatically update the `EC2_HOST` secret so you never have to set the server IP manually.

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name: `hzortech-actions`
4. Set expiration: **No expiration** (or 1 year)
5. Select scope: check **`repo`** (the full repo box — this includes secrets write)
6. Click **Generate token** and copy it immediately (shown once)

### Step 4 — Add all GitHub Actions secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add each of these:

| Secret name           | Value                                    | Where to get it                                   |
| --------------------- | ---------------------------------------- | ------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`   | your IAM access key ID                   | AWS Console → IAM → your user → Security credentials |
| `AWS_SECRET_ACCESS_KEY` | your IAM secret access key             | Shown once when you create the access key         |
| `SSH_PUBLIC_KEY`      | contents of `~/.ssh/hzortech_deploy.pub` | From Step 2                                       |
| `EC2_SSH_KEY`         | contents of `~/.ssh/hzortech_deploy`     | From Step 2 (the private key, full file contents) |
| `EC2_USER`            | `ubuntu`                                 | Fixed value, type as-is                           |
| `GH_PAT`              | your personal access token               | From Step 3                                       |
| `EC2_HOST`            | *(leave blank for now)*                  | Set automatically after first Terraform run       |

### Step 5 — Attach the right IAM policy to your AWS user

The `github-actions-deploy` IAM user needs permissions to create EC2 resources and read/write the S3 state bucket.

Go to **AWS Console → IAM → Users → github-actions-deploy → Add permissions → Attach policies directly → Create policy**

Use this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "s3:GetObject", "s3:PutObject", "s3:DeleteObject",
        "s3:ListBucket", "s3:GetBucketVersioning"
      ],
      "Resource": "*"
    }
  ]
}
```

Name it `hzortech-deploy-policy` and attach it to the user.

### Step 6 — Trigger the first run

You have two options:

**Option A — Push any small change to a terraform file:**

```bash
# Touch the file to force a change
echo "# triggered" >> terraform/main.tf
git add terraform/main.tf
git commit -m "trigger: initial infra provision"
git push origin master
```

**Option B — Trigger manually from GitHub:**

Go to your repo → **Actions → Terraform → Run workflow → Run workflow**

### What happens automatically after Step 6

```
terraform.yml runs:
  1. terraform apply → EC2 created, k3s installed, Elastic IP assigned
  2. EC2_HOST secret → auto-written to GitHub (no manual step)
  3. SSH into EC2 → waits for k3s → runs setup-secrets.sh
     → Django secret key generated
     → PostgreSQL password generated
     → Gmail credentials stored in Kubernetes secrets

deploy.yml runs (same push triggers both):
  1. Docker image built and pushed to ghcr.io
  2. kubectl apply → namespace, postgres, django, ingress all start
  3. Init container runs migrations
  4. cert-manager requests SSL cert from Let's Encrypt
  5. Site is live at https://hzortech.com
```

**Total time from push to live site: ~8–12 minutes on a fresh server.**
On subsequent pushes (code updates): ~2 minutes.

---

## Required GitHub Secrets — full reference

| Secret                | Required by     | Description                                                         |
| --------------------- | --------------- | ------------------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`   | terraform.yml   | IAM user access key for `github-actions-deploy`                     |
| `AWS_SECRET_ACCESS_KEY` | terraform.yml | IAM user secret key                                                 |
| `SSH_PUBLIC_KEY`      | terraform.yml   | Installed on EC2 by Terraform (ed25519 public key)                  |
| `EC2_SSH_KEY`         | terraform.yml, deploy.yml | Private key GitHub Actions uses to SSH into the server  |
| `EC2_USER`            | deploy.yml      | Linux user on EC2 — always `ubuntu` for Ubuntu AMIs                 |
| `EC2_HOST`            | deploy.yml      | Server's public IP — **auto-set by terraform.yml**, never manual    |
| `GH_PAT`              | terraform.yml   | Personal access token used to write EC2_HOST back to GitHub Secrets |
| `GITHUB_TOKEN`        | deploy.yml      | Auto-provided by GitHub Actions — nothing to add                    |

---

## How to update the app

### Update website text or design

Edit any HTML file in `business_page/templates/` or CSS in `base.html`, then:

```bash
git add .
git commit -m "update: homepage hero text"
git push origin master
# → deploy.yml fires → new image built → pod restarts → live in ~2 min
```

### Add a new Django model or change the database

```bash
# 1. Edit models.py locally
# 2. Generate the migration file
python manage.py makemigrations

# 3. Commit everything including the migration file
git add .
git commit -m "feat: add NewsletterSubscription model"
git push origin master
# → deploy.yml fires
# → init container runs: python manage.py migrate --noinput  ← automatic
# → new pod starts with updated schema
```

You never run migrations manually on the server — the Kubernetes init container handles it on every deploy.

### Update a non-secret config value

Edit `k8s/01-configmap.yaml` (e.g., change `CONTACT_EMAIL` or `EMAIL_HOST`):

```bash
git add k8s/01-configmap.yaml
git commit -m "config: update contact email"
git push origin master
# → deploy.yml applies the updated ConfigMap and restarts the deployment
```

### Update a secret (email password, Django key, DB password)

These live inside Kubernetes and are never in git. SSH to the server and patch them:

```bash
ssh -i ~/.ssh/hzortech_deploy ubuntu@<EC2_HOST>

kubectl create secret generic hzortech-secrets \
  --namespace hzortech \
  --from-literal=DJANGO_SECRET_KEY="new-key-here" \
  --from-literal=POSTGRES_PASSWORD="existing-or-new-password" \
  --from-literal=EMAIL_HOST_USER="shara@hzortech.com" \
  --from-literal=EMAIL_HOST_PASSWORD="new-app-password" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/django -n hzortech
```

### Scale the app (more pods)

Edit `replicas:` in `k8s/03-django.yaml`:

```yaml
spec:
  replicas: 2   # was 1
```

```bash
git add k8s/03-django.yaml
git commit -m "scale: 2 django replicas"
git push origin master
```

### Upgrade the server (bigger EC2 instance)

Edit `instance_type` in `terraform/main.tf`:

```hcl
instance_type = "t3.small"   # was t2.micro
```

```bash
git add terraform/main.tf
git commit -m "infra: upgrade to t3.small"
git push origin master
# → terraform.yml fires → AWS resizes the instance
```

### Check what's running on the server

```bash
ssh -i ~/.ssh/hzortech_deploy ubuntu@<EC2_HOST>

kubectl get pods -n hzortech          # see all running pods
kubectl logs -n hzortech deploy/django  # Django app logs
kubectl logs -n hzortech deploy/postgres  # database logs
kubectl get ingress -n hzortech       # see ingress and TLS status
```

### Access the Django admin

```bash
ssh -i ~/.ssh/hzortech_deploy ubuntu@<EC2_HOST>

# Create a superuser (one-time, run on first deploy)
kubectl exec -n hzortech deploy/django -- \
  python manage.py createsuperuser
```

Then visit `https://hzortech.com/admin`

---

## Tech stack

### Application

- Python 3.13 + Django 6
- PostgreSQL 15 (production) / SQLite (local dev fallback)
- Gunicorn WSGI server
- WhiteNoise for static file serving

### Infrastructure

- AWS EC2 t2.micro (free tier — 750 hrs/month)
- k3s (lightweight Kubernetes) with Traefik ingress controller
- cert-manager + Let's Encrypt for automatic TLS (auto-renews)
- Terraform for infrastructure provisioning (state in S3)
- GitHub Actions for CI/CD (build, push, deploy)
- GitHub Container Registry (ghcr.io) for Docker images

---

## Repository structure

```text
hzortech-main/
├── business_page/          # Django app
│   ├── templates/          # HTML templates (base, home, services, about, contact)
│   ├── models.py           # ContactSubmission model
│   ├── views.py            # Page views + contact form handler (saves to DB + sends email)
│   ├── forms.py            # ContactForm
│   ├── admin.py            # Django admin registration
│   └── migrations/         # Database migrations (committed, applied automatically)
├── hzortech/
│   ├── settings.py         # Settings — all secrets from environment variables
│   └── urls.py
├── k8s/                    # Kubernetes manifests (applied on every deploy)
│   ├── 00-namespace.yaml   # hzortech namespace
│   ├── 01-configmap.yaml   # Non-secret config (email host, DB name, etc.)
│   ├── 02-postgres.yaml    # PostgreSQL Deployment + PVC + Service
│   ├── 03-django.yaml      # Django Deployment (with migrate init container) + Service
│   ├── 04-ingress.yaml     # Traefik Ingress + cert-manager ClusterIssuer + HTTPS redirect
│   └── setup-secrets.sh    # Bootstraps k8s secrets (idempotent, run by terraform.yml)
├── terraform/
│   ├── main.tf             # EC2, security group, Elastic IP, k3s user_data bootstrap
│   ├── variables.tf        # aws_region, ssh_public_key
│   └── outputs.tf          # public_ip, instance_id, ssh_command
├── .github/workflows/
│   ├── deploy.yml          # Trigger: push to master → build → push → kubectl → rollout
│   └── terraform.yml       # Trigger: push to terraform/ → plan → apply → bootstrap
├── Dockerfile              # Gunicorn only (Traefik handles ingress/TLS)
├── .env.example            # Template for /opt/hzortech/.env on the server
└── requirements.txt        # Django, gunicorn, whitenoise, psycopg2-binary
```

---

## Local development

```bash
git clone https://github.com/Thesharaavakian/hzortech.git
cd hzortech-main
pip install -r requirements.txt
export DJANGO_SECRET_KEY="any-string-for-local-dev"
python manage.py migrate        # uses SQLite (no POSTGRES_HOST set)
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

No database setup needed locally — when `POSTGRES_HOST` is not set, Django automatically uses SQLite.

---

## Contact

- **Email:** <shara@hzortech.com>
- **General:** <hello@hzortech.com>
- **Phone:** +374 77 075 919
- **Website:** [hzortech.com](https://hzortech.com)

---

HzorTech — Yerevan, Armenia
