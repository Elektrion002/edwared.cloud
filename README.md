# Edwared Cloud

Multisystem platform deployed on VPS.

## Deployment Workflow

1. **Local Development**: Work on `d:\VPS_Plat_Edwared_v01`.
2. **Push to GitHub**: `git push origin main`.
3. **VPS Sync**: `ssh root@187.124.81.209 "cd /var/www/VPS_Plat_Edwared_v01 && git pull origin main"`.

## Benchmarking & Lessons Learned

Refer to [deployment_benchmark.md](file:///C:/Users/reled/.gemini/antigravity/brain/ac5f2364-b1bc-46b5-a42c-25b8c430eba3/deployment_benchmark.md) for details on SSH tunneling and stability standards.
