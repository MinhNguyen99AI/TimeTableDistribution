<<<<<<< HEAD
1) Cài nodejs: 16.17.0 LTS
2) cd folder front-end
3) gõ lệnh "ng serve" hoặc "npm start"
=======
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

cd frontend
docker build --tag timetable-angular-front-end:1.0.0 .

## Chạy app

```
cd..
docker-compose -f docker-compose.yml up --detach
```

## Dừng app

```
docker-compose down
```
>>>>>>> 518cf99ff4d382074a779c4b44b30c6cb8bd8aeb
