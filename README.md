# README

Welcome to the CAROLINE Project source code repository.

CAROLINE is a InSAR data processing system that automates data dowload, processing and product generation. It allows for continuous product generation where predefined products are created as new datasets are downloaded as wel as ad-hoc product creation.

# Development

For development purposes a container has been created with the latest stable Python version. All developed code must be able to run in this invironment.

## Start the container

```
docker-compose up -d --build caroline
```

## Start a shell in the container

```
docker exec -it caroline bash
```

## Run Python interactively in the container

```
docker exec -it caroline python3
```

## Contacts

### Project Lead

- Freek van Leijen <F.J.vanLeijen@tudelft.nl>

### Developers

- Freek van Leijen <F.J.vanLeijen@tudelft.nl>
- Manuel Garcia Alvarez <M.G.GarciaAlvarez@tudelft.nl>
- Marc Bruna <M.F.D.Bruna@tudelft.nl>
- Niels Jansen <N.H.Jansen@tudelft.nl>

### Repository admins

- Niels Jansen <N.H.Jansen@tudelft.nl>

