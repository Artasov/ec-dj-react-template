#!/bin/sh
# entrypoint_minio.sh

echo "#####################################"
echo "######### Minio Starting... #########"
echo "#####################################"

# Запускаем сервер MinIO в фоновом режиме
minio server /data --console-address ":9001" &

# Функция для проверки готовности MinIO
check_minio_ready() {
    mc alias set myminio http://minio:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
    mc ls myminio
}

# Ожидаем готовности MinIO
until check_minio_ready; do
  echo "Waiting for Minio to be ready..."
  sleep 2
done

echo "Minio is ready."
# Создаем бакет, если он не существует
echo "Creating media bucket if not exist..."
mc mb myminio/media --ignore-existing

# Настраиваем публичную политику доступа к бакету
echo "Setting public policy for media bucket..."
mc policy set download myminio/media
#echo "Setting anonymous public policy for media bucket..."
#mc anonymous set download myminio/media
echo "Minio setup complete."

# Блокируем скрипт, чтобы контейнер не завершал работу
wait
