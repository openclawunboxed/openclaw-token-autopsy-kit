# service install templates

ready-to-edit templates for running `tail_audit.py` and `alert_on_spike.py` as background services on the four common openclaw deployment shapes.

| file | platform | what it does |
| --- | --- | --- |
| `tail_audit.systemd.service` | linux (vps, docker host, wsl2) | runs tail_audit.py as a systemd service |
| `tail_audit.launchd.plist` | macos (mac mini) | runs tail_audit.py as a launchd agent |
| `alert_on_spike.crontab` | any unix | cron entry that runs alert_on_spike.py every 15 minutes |
| `docker-compose.yml` | docker | compose file that runs both services in containers |

## install steps (linux + systemd)

```bash
# copy the unit file
sudo cp tail_audit.systemd.service /etc/systemd/system/tail-audit.service

# edit the paths inside it for your install
sudo nano /etc/systemd/system/tail-audit.service

# reload, start, enable
sudo systemctl daemon-reload
sudo systemctl start tail-audit
sudo systemctl enable tail-audit
sudo systemctl status tail-audit
```

## install steps (macos + launchd)

```bash
# copy to your user's launch agents folder
cp tail_audit.launchd.plist ~/Library/LaunchAgents/com.openclaw.tail-audit.plist

# edit the paths inside it for your install
nano ~/Library/LaunchAgents/com.openclaw.tail-audit.plist

# load and start
launchctl load ~/Library/LaunchAgents/com.openclaw.tail-audit.plist
launchctl list | grep tail-audit
```

## install steps (cron for alerts)

```bash
# edit your crontab
crontab -e

# paste the contents of alert_on_spike.crontab, edit the paths
# save and exit. cron picks it up automatically.
crontab -l  # verify
```

## install steps (docker compose)

```bash
# edit the volume mounts and webhook url in docker-compose.yml
docker compose up -d
docker compose logs -f
```

## what to monitor after install

- check that `running_ledger.csv` is growing in real time
- check the systemd journal or launchd log for tail_audit errors
- send a test alert by setting `--threshold 0.0` temporarily and confirming the webhook fires
