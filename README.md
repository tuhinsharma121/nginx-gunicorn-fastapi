# nginx-gunicorn-fastapi

Use this command to clone the repo else docker will fail (for Windows)
   ```bash
   git clone https://github.com/tuhinsharma121/nginx-gunicorn-fastapi.git --config core.autocrlf=input
   ```

1. To bring the cluster up and running

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

2. Check the intel app - http://localhost:8008/hxdocs

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
