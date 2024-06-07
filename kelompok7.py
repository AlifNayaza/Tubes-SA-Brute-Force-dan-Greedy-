import tkinter as tk
from tkinter import messagebox
import itertools
import time
import random
import folium

def generate_coordinates(num_cities, seed):
    """
    Menghasilkan koordinat acak untuk setiap kota.
    Input: num_cities - jumlah kota, seed - nilai seed untuk random
    Output: cities - daftar nama kota, coordinates - daftar koordinat kota
    """
    random.seed(seed)
    cities = [f"Kota {i}" for i in range(num_cities)]
    coordinates = []
    for _ in range(num_cities):
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        coordinates.append((latitude, longitude))
    return cities, coordinates

def calculate_distances(coordinates):
    """
    Menghitung jarak antara setiap pasangan kota berdasarkan koordinat.
    Input: coordinates - daftar koordinat kota
    Output: distances - matriks jarak antar kota
    """
    num_cities = len(coordinates)
    distances = [[0] * num_cities for _ in range(num_cities)]
    for i in range(num_cities):
        for j in range(i + 1, num_cities):
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[j]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            distances[i][j] = distances[j][i] = distance
    return distances

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak antara dua titik berdasarkan formula haversine.
    Input: lat1, lon1 - koordinat titik 1
           lat2, lon2 - koordinat titik 2
    Output: jarak dalam kilometer
    """
    from math import radians, cos, sin, asin, sqrt
    R = 6371  # Radius bumi dalam kilometer

    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = R * c
    return distance

def brute_force_shortest_path(cities, distances):
    """
    Algoritma Brute Force:
    1. Generate semua permutasi kota.
    2. Hitung jarak total untuk setiap rute.
    3. Simpan rute terpendek.
    4. Kembalikan rute terpendek.
    """
    n = len(distances)
    shortest_path = None
    shortest_distance = float('inf')  # Inisialisasi jarak terpendek dengan nilai tak terhingga
    
    start_time = time.time()  # Mulai menghitung waktu eksekusi
    
    # Melakukan permutasi semua kemungkinan rute
    for path in itertools.permutations(range(n)):
        distance = 0
        # Menghitung jarak total untuk setiap rute
        for i in range(n-1):
            distance += distances[path[i]][path[i+1]]
        distance += distances[path[-1]][path[0]]  # Kembali ke kota awal
        
        # Memeriksa apakah jarak rute saat ini lebih pendek dari jarak terpendek yang sudah ditemukan sebelumnya
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_path = path
    
    end_time = time.time()  # Berhenti menghitung waktu eksekusi
    execution_time = end_time - start_time  # Menghitung waktu eksekusi
    
    return shortest_path, shortest_distance, execution_time

def greedy_shortest_path(cities, distances):
    """
    Algoritma Greedy:
    1. Pilih titik awal.
    2. Pilih titik berikutnya yang paling dekat.
    3. Hitung jarak total.
    4. Kembali ke titik awal.
    5. Kembalikan rute terpendek.
    """
    n = len(distances)
    current_city = 0  # Dimulai dari kota pertama
    unvisited_cities = set(range(1, n))  # Inisialisasi himpunan kota yang belum dikunjungi
    shortest_path = [current_city]  # Inisialisasi rute terpendek dengan kota awal
    total_distance = 0  # Inisialisasi jarak total
    
    start_time = time.time()  # Mulai menghitung waktu eksekusi

    # Mengunjungi setiap kota secara greedy
    while unvisited_cities:
        next_city = min(unvisited_cities, key=lambda city: distances[current_city][city])  # Memilih kota berikutnya yang paling dekat
        total_distance += distances[current_city][next_city]  # Menambahkan jarak ke kota berikutnya ke jarak total
        shortest_path.append(next_city)  # Menambahkan kota berikutnya ke rute terpendek
        unvisited_cities.remove(next_city)  # Menghapus kota yang telah dikunjungi dari himpunan kota yang belum dikunjungi
        current_city = next_city  # Memperbarui kota saat ini dengan kota berikutnya

    # Kembali ke kota awal
    total_distance += distances[shortest_path[-1]][shortest_path[0]]
    
    end_time = time.time()  # Berhenti menghitung waktu eksekusi
    execution_time = end_time - start_time  # Menghitung waktu eksekusi

    return shortest_path, total_distance, execution_time

def visualize_shortest_path(cities, shortest_path, coordinates, algorithm):
    """
    Visualisasi rute terpendek dalam bentuk peta.
    """
    map = folium.Map()

    # Menambahkan marker untuk setiap kota
    for i, city in enumerate(cities):
        folium.Marker(
            coordinates[i],
            tooltip=city,
            icon=folium.Icon(color='red' if i in shortest_path else 'blue')
        ).add_to(map)

    # Menambahkan garis untuk rute terpendek
    route_coordinates = [coordinates[i] for i in shortest_path]
    folium.PolyLine(
        locations=route_coordinates,
        color='green',
        weight=5,
        opacity=0.8
    ).add_to(map)

    # Menambahkan teks di sepanjang garis untuk rute terpendek
    for i in range(len(route_coordinates) - 1):
        start = route_coordinates[i]
        end = route_coordinates[i + 1]
        distance = haversine_distance(start[0], start[1], end[0], end[1])

        # Format teks dengan struktur melebar ke samping
        text = f"<span style='font-weight: bold; white-space: nowrap;'>{cities[shortest_path[i]]} &rarr; {cities[shortest_path[i + 1]]} ({distance:.2f} km)</span>"

        # Gaya CSS untuk membuat teks melebar ke samping
        div_style = "background-color: white; padding: 5px; border: 1px solid #ccc; border-radius: 5px; font-size: 14pt; display: inline-block;"
        folium.Marker(
            location=[(start[0] + end[0]) / 2, (start[1] + end[1]) / 2],  # Menempatkan teks di tengah garis
            icon=folium.DivIcon(html=f"<div style='{div_style}'>{text}</div>")
        ).add_to(map)

    map.fit_bounds(route_coordinates)
    map.save(f'rute_terpendek_{algorithm}.html')

def main():
    root = tk.Tk()
    root.title("Perhitungan Rute Terpendek")

    def calculate_shortest_path():
        try:
            num_cities = int(entry_num_cities.get())
            seed_value = int(entry_seed.get())

            cities, coordinates = generate_coordinates(num_cities, seed_value)
            distances = calculate_distances(coordinates)

            shortest_path_brute_force, shortest_distance_brute_force, execution_time_brute_force = brute_force_shortest_path(cities, distances)
            shortest_path_greedy, shortest_distance_greedy, execution_time_greedy = greedy_shortest_path(cities, distances)

            messagebox.showinfo("Hasil", f"Brute Force:\nRute: {shortest_path_brute_force}\nJarak: {shortest_distance_brute_force:.2f} km\nWaktu: {execution_time_brute_force:.6f} detik\n\nGreedy:\nRute: {shortest_path_greedy}\nJarak: {shortest_distance_greedy:.2f} km\nWaktu: {execution_time_greedy:.6f} detik")

            visualize_shortest_path(cities, shortest_path_brute_force, coordinates, "Brute Force")
            visualize_shortest_path(cities, shortest_path_greedy, coordinates, "Greedy")

        except ValueError:
            messagebox.showerror("Error", "Masukkan harus berupa bilangan bulat")

    label_num_cities = tk.Label(root, text="Jumlah Kota:")
    label_num_cities.grid(row=0, column=0, padx=10, pady=5, sticky="e")

    entry_num_cities = tk.Entry(root)
    entry_num_cities.grid(row=0, column=1, padx=10, pady=5)

    label_seed = tk.Label(root, text="Seed:")
    label_seed.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    entry_seed = tk.Entry(root)
    entry_seed.grid(row=1, column=1, padx=10, pady=5)

    button_calculate = tk.Button(root, text="Hitung", command=calculate_shortest_path)
    button_calculate.grid(row=2, columnspan=2, padx=10, pady=5)

    # Menambahkan daftar semua kota beserta koordinatnya
    def show_city_coordinates():
        try:
            num_cities = int(entry_num_cities.get())
            seed_value = int(entry_seed.get())

            cities, coordinates = generate_coordinates(num_cities, seed_value)

            city_info = "\n".join([f"{city}: {coord}" for city, coord in zip(cities, coordinates)])
            messagebox.showinfo("Daftar Kota dan Koordinat", city_info)
        except ValueError:
            messagebox.showerror("Error", "Masukkan harus berupa bilangan bulat")

    button_show_coordinates = tk.Button(root, text="Lihat Koordinat", command=show_city_coordinates)
    button_show_coordinates.grid(row=3, columnspan=2, padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()

