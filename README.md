# Clearnet Forum


Running docker:
```
sudo docker compose down && sudo docker compose build --no-cache && sudo docker compose up
```

Get link:
```
sudo docker exec -it tornet_forum cat /var/lib/tor/hidden_service/hostname
```

