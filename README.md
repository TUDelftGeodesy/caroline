# README

Welcome to the CAROLINE Project source code repository.

CAROLINE is a InSAR data processing system that automates data dowload, processing and product generation. It allows for continuous product generation, where predefined products are created as new datasets are downloaded, as wel as ad-hoc product creation.

# Development

For development purposes containers have been created with the latest stable Python and PostgreSQL versions, along with a docker-compose.yml file. All developed code must be able to run in these environments.

Currently, there are 3 services defined within docker-compose.yml:
<dl>
  <dt>caroline</dt>
  <dd>In this container, caroline is installed as a package from source. You can use this container to use/test/interact with caroline.</dd>
  <dt>caroline-dev</dt>
  <dd>In this container, caroline is installed in <a href="https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html">'Development Mode'</a> in ~caroline/src/caroline.</dd>
  <dt>caroline-db</dt>
  <dd>The caroline database: a PostgreSQL database container with PostGIS extensions installed.</dd>
</dl>

## Container usage

### .env file

Before starting any containers, you must setup a .env file. An example .env file is provided in .env.example.

Copy the example .env file:
```text
$ cp .env.example .env
```

The defaults should be OK for development purposes. Do not use these settings in production. Review the file and make any desired changes.

### caroline

This container has caroline installed as a package so it can be interacted with as intended in a normal installation. It can be used for interactive testing of the installed package.

Starting the container:
```text
$ docker-compose up -d --build caroline
```

The database container is automatically started as a dependency.

Interacting with the container:
```text
$ docker exec -it --user caroline caroline bash
caroline@caroline:~$
```

You can now use caroline:
```text
caroline@caroline:~$ caroline --version
CAROLINE v0.1.0

Database       : PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
PostGIS        : 3.1 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
PostGIS Full   : POSTGIS="3.1.2 cbe925d" [EXTENSION] PGSQL="130" GEOS="3.7.1-CAPI-1.11.1 27a5e771" PROJ="Rel. 5.2.0, September 15th, 2018" LIBXML="2.9.4" LIBJSON="0.12.1" LIBPROTOBUF="1.3.1" WAGYU="0.5.0 (Internal)"
PostGIS GEOS   : 3.7.1-CAPI-1.11.1 27a5e771
PostGIS Lib    : 3.1.2
PostGIS LibXML : 2.9.4
PostGIS PROJ   : Rel. 5.2.0, September 15th, 2018

```

### caroline-dev

This container has caroline installed in <a href="https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html">'Development Mode'</a> in ~caroline/src/caroline. If you're not familiar with setuptools' development mode you can read up on it here: <a href="https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html">https://setuptools.readthedocs.io/en/latest/userguide/development_mode.html</a>. A short description: Having to build and install every time you make a change to the code is laborious. With development mode you can use the code in place while developing it without rebuilding and reinstalling the package.

Another feature of this container is that it has the PostgreSQL client psql installed. This makes for easy command line interaction with the database while developing.

Starting the container:
```text
$ docker-compose up -d --build caroline-dev
```

The database container is autmatically started as a dependency

Interacting with the container:
```text
$ docker exec -it --user caroline caroline-dev bash
caroline@caroline-dev:~$
```

Using caroline in development mode:
```text
caroline@caroline-dev:~$ cd src/caroline
caroline@caroline-dev:~/src/caroline$ caroline/caroline --version
CAROLINE v0.1.0

Database       : PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
PostGIS        : 3.1 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
PostGIS Full   : POSTGIS="3.1.2 cbe925d" [EXTENSION] PGSQL="130" GEOS="3.7.1-CAPI-1.11.1 27a5e771" PROJ="Rel. 5.2.0, September 15th, 2018" LIBXML="2.9.4" LIBJSON="0.12.1" LIBPROTOBUF="1.3.1" WAGYU="0.5.0 (Internal)"
PostGIS GEOS   : 3.7.1-CAPI-1.11.1 27a5e771
PostGIS Lib    : 3.1.2
PostGIS LibXML : 2.9.4
PostGIS PROJ   : Rel. 5.2.0, September 15th, 2018

```

Using psql:
```text
caroline@caroline-dev:~$ psql
psql (13.3 (Debian 13.3-1.pgdg100+1))
Type "help" for help.

caroline=> select version();
                                                     version
------------------------------------------------------------------------------------------------------------------
 PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
(1 row)

caroline=>
```

### caroline-db

The database container is normally started as a dependency by the other containers. If needed you can individually start the database:
```text
$ docker-compose up -d caroline-db
```

Interact with the database as super user:
```text
$ docker exec -it --user postgres caroline-db bash
postgres@caroline-db:/$ psql
psql (13.3 (Debian 13.3-1.pgdg100+1))
Type "help" for help.

postgres=# select version();
                                                     version
------------------------------------------------------------------------------------------------------------------
 PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit
(1 row)

postgres=#

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

