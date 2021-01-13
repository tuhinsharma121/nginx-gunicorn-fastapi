# nginx-gunicorn-fastapi

This is a standard skeleton of a python ML project that I have built. 

- web server/load balancer : nginx
- application server : gunicorn
- application server worker : uvicorn
- rest api layer : fastapi
- db : postgres
- deployment : docker/docker-compose


Prerequisite:-

1. Install docker and docker-compose in your system.

2. Use this command to clone the repo (for Windows)
   ```bash
   git clone https://github.com/tuhinsharma121/nginx-gunicorn-fastapi.git --config core.autocrlf=input
   ```
3. Use this command to clone the repo (for Unix)
   ```bash
   git clone https://github.com/tuhinsharma121/nginx-gunicorn-fastapi.git
   ```
   
Steps to run the project:-

1. To run tests:

   ```bash
   docker-compose -f docker-compose-test.yml build
   docker-compose -f docker-compose-test.yml up
   ```
   Expected output

   ```bash
   Creating network "nginx-gunicorn-fastapi_default" with the default driver
   Creating nginx-gunicorn-fastapi_db-test_1 ... done
   Creating nginx-gunicorn-fastapi_intel-test_1 ... done
   Attaching to nginx-gunicorn-fastapi_db-test_1, nginx-gunicorn-fastapi_intel-test_1
   db-test_1     |
   db-test_1     | PostgreSQL Database directory appears to contain a database; Skipping initialization
   db-test_1     |
   db-test_1     | 2021-01-13 10:13:06.285 UTC [1] LOG:  starting PostgreSQL 13.1 on x86_64-pc-linux-musl, compiled by gcc (Alpine 9.3.0) 9.3.0, 64-bit
   db-test_1     | 2021-01-13 10:13:06.285 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
   db-test_1     | 2021-01-13 10:13:06.285 UTC [1] LOG:  listening on IPv6 address "::", port 5432
   db-test_1     | 2021-01-13 10:13:06.295 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
   db-test_1     | 2021-01-13 10:13:06.317 UTC [21] LOG:  database system was shut down at 2021-01-13 10:12:04 UTC
   db-test_1     | 2021-01-13 10:13:06.337 UTC [1] LOG:  database system is ready to accept connections
   intel-test_1  | ...........
   intel-test_1  | ----------------------------------------------------------------------
   intel-test_1  | Ran 11 tests in 0.516s
   intel-test_1  |
   intel-test_1  | OK
   nginx-gunicorn-fastapi_intel-test_1 exited with code 0
   ```
   
   Then bring it down:

   ```bash
   docker-compose -f docker-compose-test.yml down
   ```
   Expected output:
   ```bash
   Removing nginx-gunicorn-fastapi_intel-test_1 ... done
   Removing nginx-gunicorn-fastapi_db-test_1    ... done
   Removing network nginx-gunicorn-fastapi_default
   ```
   
   
2. To bring the cluster up and running

    ```bash
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml build
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml up -d --remove-orphans
    ```
    
    Expected output:
    ```bash
    Creating network "nginx-gunicorn-fastapi_intel_db_nw" with driver "bridge"
    Creating network "nginx-gunicorn-fastapi_nginx_intel_nw" with driver "bridge"
    Creating nginx-gunicorn-fastapi_db_1 ... done
    Creating nginx-gunicorn-fastapi_intel_1 ... done
    Creating nginx-gunicorn-fastapi_nginx_1 ... done
    ```
    intel app - http://localhost:8008
   
    swagger docs - http://localhost:8008/hxdocs


3. To scale intel app up to 3
    ```bash
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml up -d --scale intel=3 --no-recreate
    ```
    Expected output:
    ```bash
    Creating nginx-gunicorn-fastapi_intel_2 ... done
    Creating nginx-gunicorn-fastapi_intel_3 ... done
    ```
   
4. To check the logs
    ```bash
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml logs
    ```

5. To check the list of active containers
    ```bash
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml ps
    ```
    Expected output:
    ```bash
                 Name                           Command                  State                Ports
    --------------------------------------------------------------------------------------------------------
    nginx-gunicorn-fastapi_db_1      docker-entrypoint.sh postgres    Up (healthy)   0.0.0.0:5432->5432/tcp
    nginx-gunicorn-fastapi_intel_1   /bin/entrypoint.sh               Up             0.0.0.0:49261->5678/tcp
    nginx-gunicorn-fastapi_intel_2   /bin/entrypoint.sh               Up             0.0.0.0:49267->5678/tcp
    nginx-gunicorn-fastapi_intel_3   /bin/entrypoint.sh               Up             0.0.0.0:49266->5678/tcp
    nginx-gunicorn-fastapi_nginx_1   /app/docker-entrypoint.sh  ...   Up             0.0.0.0:8008->80/tcp
    ```
   
6. To scale intel app down to 1
    ```bash
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml up -d --scale intel=1 --no-recreate
    ```
    Expected output:
    ```bash
    Stopping and removing nginx-gunicorn-fastapi_intel_2 ... done
    Stopping and removing nginx-gunicorn-fastapi_intel_3 ... done
    ```

7. To get inside a running docker container - intel
    ```bash
    docker exec -it nginx-gunicorn-fastapi_intel_1 bash
    ```
    Expected output:
    ```bash
    root@2f1b3f7bb31d:/#
    ```
8. To bring the cluster down:
    ```bash
    docker-compose -f docker-compose-nginx-gunicorn-fastapi.yml down
    ```
    Expected output:
    ```bash
    Stopping nginx-gunicorn-fastapi_nginx_1 ... done
    Stopping nginx-gunicorn-fastapi_intel_1 ... done
    Stopping nginx-gunicorn-fastapi_db_1    ... done
    Removing nginx-gunicorn-fastapi_nginx_1 ... done
    Removing nginx-gunicorn-fastapi_intel_1 ... done
    Removing nginx-gunicorn-fastapi_db_1    ... done
    Removing network nginx-gunicorn-fastapi_intel_db_nw
    Removing network nginx-gunicorn-fastapi_nginx_intel_nw
    ```

