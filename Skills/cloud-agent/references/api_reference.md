# Cloud Agent — API Reference

## Anthropic Claude API
- Model: `claude-opus-4-5`
- SDK: `anthropic` Python package
- Docs: https://docs.anthropic.com

## Environment Variables
- `ANTHROPIC_API_KEY` — Claude API key
- `VAULT_PATH` — Path to vault (default: /home/ubuntu/AI_Employee_Vault)
- `AGENT_ROLE` — Must be `cloud`
- `DRY_RUN` — Set `true` for testing

## PM2 Commands
- `pm2 list` — Check running processes
- `pm2 logs cloud-orchestrator` — View logs
- `pm2 restart cloud-orchestrator` — Restart agent
