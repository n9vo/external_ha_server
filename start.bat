@echo off

start /b cloudflared tunnel --config tunnels\admin.yml run
start /b cloudflared tunnel --config tunnels\lights.yml run
start /b cloudflared tunnel --config tunnels\inference.yml run
start /b python server.py