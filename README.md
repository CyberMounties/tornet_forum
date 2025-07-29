# Clearnet Forum

This repository provides code for a simulated Tor cyber-crime forum, designed as an educational tool for learning about cyber threat intelligence, open-source intelligence (OSINT), and web scraping in a safe, legal, and controlled environment. The forum mimics real-world scenarios to help users practice data collection and analysis techniques.

To get started, download and install [Docker](https://docs.docker.com/compose/install/).

## Tech-stack

- Frontend
    - HTML5
    - CSS
- Backend
    - Python Flask
    - Jinja2 templating engine
    - SQLite3 


## Running Docker

If you are using Ubuntu 24.04 or later, you can set up and run the forum with the following commands:

```bash
sudo docker compose build
sudo docker compose up -d
```

These commands build the Docker environment and start the forum in the background.


## Running site without docker

You can also run the site without docker by downloading `tornet_forum` and running it:
```
git clone https://github.com/CyberMounties/tornet_forum.git
cd tornet_forum
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
flask run --debug               # Remove --debug if you want to run without debugger
```


## Accessing the Site

After the Docker container is up and running, retrieve the onion link for the Tor-hosted site by executing the following command:

```bash
sudo docker exec -it tornet_forum cat /var/lib/tor/hidden_service/hostname
```

Copy the outputted onion link and paste it into the Tor Browser to access the site.


## Note

> The automated data population scripts rely on a cron job configured within the Docker environment. Running the site outside of Docker will prevent these scripts from executing, as they depend on the container's configuration.



