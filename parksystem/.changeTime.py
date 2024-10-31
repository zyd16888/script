import mysql.connector
import time

# 数据库连接信息
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 22336,
    'user': 'root',
    'password': '',
    'database': 'parksystem_base_info'
}

# 定期执行的SQL语句
SQL_UPDATE_TURN_OFF_SETTINGS = """
UPDATE parksystem_base_info.y_turn_off_settings_lighting
SET turn_off_time = '23:00'
WHERE turn_off_time < '23:00' AND deleted_at IS NULL;
"""

SQL_UPDATE_SCHEDULED_SETTINGS = """
UPDATE parksystem_base_info.s_scheduled_settings_lighting
SET time_end = '23:00'
WHERE time_end > '13:00' AND time_end < '22:00' AND deleted_at IS NULL;
"""

# 函数：连接到数据库并执行查询
def execute_queries():
    try:
        # 建立数据库连接
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # 执行SQL语句
        cursor.execute(SQL_UPDATE_TURN_OFF_SETTINGS)
        cursor.execute(SQL_UPDATE_SCHEDULED_SETTINGS)
        
        # 提交更改
        connection.commit()
        print("Queries executed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # 关闭连接
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 主循环：每5分钟执行一次
while True:
    execute_queries()
    print("Waiting for 5 minutes before next execution...")
    time.sleep(300)  # 每5分钟（300秒）执行一次

