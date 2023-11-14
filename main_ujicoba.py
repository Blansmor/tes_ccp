import streamlit as st
import paho.mqtt.client as mqtt
import plotly.graph_objs as go
from datetime import datetime
from PIL import Image

image = Image.open('bareng.png')

st.image(image, width=700)
st.write("  ")
#st.title("PLTU Banten 3 Lontar")
st.markdown("<center><h2>Monitoring Condensate Polishing Berbasis IoT</h2></center>", unsafe_allow_html=True)
st.markdown("<center><h2>PLTU Banten 3 Lontar</h2></center>", unsafe_allow_html=True)

# Variabel-variabel koneksi MQTT
#broker = "test.mosquitto.org"
broker = "mqtt-dashboard.com"
port = 1883
topic_red = "arsuya/sensor/red"  # Sesuaikan dengan topik MQTT yang digunakan oleh perangkat IoT pertama
topic_green = "arsuya/sensor/green"  # Sesuaikan dengan topik MQTT yang digunakan oleh perangkat IoT kedua
topic_blue = "arsuya/sensor/blue" 
mqtt_connected = False  # Variabel status koneksi MQTT

# Buat wadah kosong untuk output nilai dan grafik
output_container1 = st.empty()
chart_container1 = st.empty()

output_container2 = st.empty()
chart_container2 = st.empty()

output_container3 = st.empty()
chart_container3 = st.empty()

# Variabel-variabel grafik garis
data1 = []  # Simpan data dari topik pertama dalam list
data2 = []  # Simpan data dari topik kedua dalam list
data3 = []  # Simpan data dari topik kedua dalam list
max_data_points = 300  # Batasi jumlah data yang ditampilkan pada grafik (1 hari x 60 menit)

# Fungsi yang akan dipanggil saat koneksi MQTT berhasil
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    mqtt_connected = True
    client.subscribe(topic_red)  # Langganan ke topik MQTT pertama setelah koneksi berhasil
    client.subscribe(topic_green)  # Langganan ke topik MQTT kedua setelah koneksi berhasil
    client.subscribe(topic_blue)

# Fungsi yang akan dipanggil saat pesan MQTT diterima
def on_message(client, userdata, msg):
    try:
        sensor_data = msg.payload.decode("utf-8")  # Parsing pesan MQTT
        if msg.topic == topic_red:
            update_output(output_container1, sensor_data, "red", "red")  # Perbarui output nilai untuk topik pertama
            update_line_chart(chart_container1, data1, sensor_data)  # Perbarui grafik garis untuk topik pertama
        elif msg.topic == topic_green:
            update_output(output_container2, sensor_data, "green", "green")  # Perbarui output nilai untuk topik kedua
            update_line_chart(chart_container2, data2, sensor_data)  # Perbarui grafik garis untuk topik kedua
        elif msg.topic == topic_blue:
            update_output(output_container3, sensor_data, "blue", "blue")  # Perbarui output nilai untuk topik kedua
            update_line_chart(chart_container3, data3, sensor_data)  # Perbarui grafik garis untuk topik kedua
    except Exception as e:
        st.error(f"Error parsing MQTT message: {e}")

# Fungsi untuk memperbarui output nilai
def update_output(output_container, sensor_data, unit, topic_label):
    output_container.metric(topic_label, f"{sensor_data} {unit}")

# Fungsi untuk memperbarui data pada grafik garis
def update_line_chart(chart_container, data, sensor_data):
    current_time = datetime.now().strftime("%H:%M:%S")
    data.append((current_time, sensor_data))
    
    # Proses data waktu untuk sumbu x
    x_time = [entry[0] for entry in data]
    # Ambil data sensor untuk sumbu y
    y_sensor = [entry[1] for entry in data]
    # Tampilkan grafik garis menggunakan Plotly dalam wadah yang sudah dibuat
    fig = go.Figure(data=go.Scatter(x=x_time, y=y_sensor, mode='lines'))
    chart_container.plotly_chart(fig, use_container_width=True, key='line_chart')

    if len(data) > max_data_points:
        data.pop(0)

# Koneksi awal ke broker MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 60)
client.loop_forever()
