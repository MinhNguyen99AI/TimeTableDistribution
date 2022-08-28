# Backend

## Start up api server

- Tạo environment mới `conda create --name timetable python=3.8`
- Activate environment `conda activate timetable`
- Cd vào folder `api`
- Install dependencies `pip install -r requirements.txt`
- Thêm env variable cho mongoDB url `set MONGODB_URL=mongodb://localhost:27017/`
- Start server: `python app.py`
