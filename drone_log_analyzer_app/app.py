from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import csv
import io
import math

app = Flask(__name__)
DB_NAME = 'telemetry.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS telemetry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        latitude REAL,
                        longitude REAL,
                        altitude REAL,
                        speed REAL,
                        flytime REAL,
                        battery REAL,
                        mode TEXT,
                        max_wind_speed REAL)''')  
        conn.commit()

init_db()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return "Brak pliku", 400

        try:
            stream = io.TextIOWrapper(file.stream, encoding='utf-8-sig', newline='', errors='ignore')
            reader = csv.DictReader(stream, delimiter=';')

            if reader.fieldnames:
                reader.fieldnames = [h.strip() for h in reader.fieldnames]

            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM telemetry")

                for i, row in enumerate(reader):
                    if not row:
                        continue
                    try:
                        latitude = float(row['OSD.latitude'].replace(',', '.'))
                        longitude = float(row['OSD.longitude'].replace(',', '.'))
                        altitude = float(row['OSD.height [ft]'].replace(',', '.'))
                        speed = float(row['OSD.hSpeed [MPH]'].replace(',', '.'))
                        timestamp = row['CUSTOM.date [local]'].strip() + " " + row['CUSTOM.updateTime [local]'].strip()
                        flytime = float(row['OSD.flyTime [s]'].replace(',', '.'))
                        battery = float(row.get('BATTERY.chargeLevel [%]', '0').replace(',', '.')) if row.get('BATTERY.chargeLevel [%]') else None
                        mode = row.get('RC.mode', '').strip().upper()
                        max_wind_speed = float(row.get('WEATHER.windSpeed [MPH]', '0').replace(',', '.')) if row.get('WEATHER.windSpeed [MPH]') else None
                    except:
                        continue

                    c.execute('''INSERT INTO telemetry (timestamp, latitude, longitude, altitude, speed, flytime, battery, mode, max_wind_speed)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (timestamp, latitude, longitude, altitude, speed, flytime, battery, mode, max_wind_speed))

                conn.commit()

        except:
            return "Nie udało się odczytać pliku", 500

        return redirect(url_for('results'))

    return render_template('index.html')


@app.route('/results')
def results():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT flytime, altitude, speed, battery, latitude, longitude, timestamp, mode, max_wind_speed FROM telemetry ORDER BY flytime")
        rows = c.fetchall()

    data_altitude = []
    data_speed = []
    data_battery = []
    data_mode = []
    data_wind_speed = []
    coordinates = []

    max_altitude = 0
    max_speed = 0
    max_wind_speed = 0
    total_speed = 0
    total_flytime = 0
    speed_count = 0
    total_distance = 0.0

    prev_lat, prev_lon = None, None
    first_timestamp = rows[0][6] if rows else "Brak danych"

    battery_start = None
    battery_end = None

    for row in rows:
        flytime = round(row[0], 2)
        altitude_m = round(row[1] * 0.3048, 2)
        speed_kmh = round(row[2] * 1.60934, 2)
        battery = row[3]
        lat = row[4]
        lon = row[5]
        mode = row[7]
        wind_speed = row[8]

        data_altitude.append({'x': flytime, 'y': altitude_m})
        data_speed.append({'x': flytime, 'y': speed_kmh})
        if battery is not None:
            data_battery.append({'x': flytime, 'y': battery})
        if mode:
            mapped_mode = {'C': 0, 'N': 1, '1': 1, 'S': 2, '0': 2}.get(mode, None)
            if mapped_mode is not None:
                data_mode.append({'x': flytime, 'y': mapped_mode})
        if wind_speed is not None:
            data_wind_speed.append({'x': flytime, 'y': wind_speed})
            max_wind_speed = max(max_wind_speed, wind_speed)
        if lat is not None and lon is not None:
            coordinates.append([lat, lon])

        max_altitude = max(max_altitude, altitude_m)
        max_speed = max(max_speed, speed_kmh)
        total_speed += speed_kmh
        speed_count += 1
        total_flytime = flytime

        if prev_lat is not None and prev_lon is not None:
            total_distance += haversine(prev_lat, prev_lon, lat, lon)
        prev_lat, prev_lon = lat, lon

        if battery_start is None and battery is not None:
            battery_start = battery
        if battery is not None:
            battery_end = battery

    avg_speed = round(total_speed / speed_count, 2) if speed_count > 0 else 0
    total_time_minutes = round(total_flytime / 60, 2)
    total_distance = round(total_distance, 3)

    return render_template('results.html',
                           altitude_data=data_altitude,
                           speed_data=data_speed,
                           battery_data=data_battery,
                           mode_data=data_mode,
                           wind_speed_data=data_wind_speed,
                           coordinates=coordinates,
                           summary={
                               'total_time': round(total_flytime, 2),
                               'total_time_min': total_time_minutes,
                               'max_altitude': max_altitude,
                               'max_speed': max_speed,
                               'avg_speed': avg_speed,
                               'total_distance': total_distance,
                               'date': first_timestamp.split()[0],
                               'battery_start': battery_start if battery_start is not None else 'Brak danych',
                               'battery_end': battery_end if battery_end is not None else 'Brak danych',
                               'max_wind_speed': max_wind_speed
                           })


if __name__ == '__main__':
    app.run(debug=True)
