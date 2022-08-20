# Time table scheduling

## Thông tin port

- API: 5000
- MongoDB: 27017

## Tạo API docker image (nếu chưa tồn tại)

```
cd api
docker build --tag timetable-flask-api:1.0.0 .
```

## Tạo Frontend docker image

#TODO

## Chạy app

```
docker-compose -f docker-compose.yml up --detach
```

## Dừng app

```
docker-compose down
```