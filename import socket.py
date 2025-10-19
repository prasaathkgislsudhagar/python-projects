#!/usr/bin/env python3
"""
port_scanner_mt.py - Multithreaded TCP port scanner with file output and optional banner grab

Features:
- Multithreaded scanning using ThreadPoolExecutor
- Customizable port range, timeout, and worker count
- Optional simple banner grabbing (reads up to 1024 bytes after connect)
- Saves results to CSV and JSON
- Prints duration and summary

Usage examples:
    python port_scanner_mt.py example.com --start 1 --end 1024 --timeout 0.8 --workers 200 --banner --out results
    python port_scanner_mt.py 192.168.1.10 --start 20 --end 1024

Output:
- results_YYYYMMDD_HHMMSS.csv
- results_YYYYMMDD_HHMMSS.json
"""
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import csv
import json
import sys
import os

def parse_args():
    p = argparse.ArgumentParser(description="Multithreaded TCP Port Scanner (with optional banner grabbing)")
    p.add_argument("target", help="Target hostname or IP")
    p.add_argument("--start", type=int, default=1, help="Start port (default 1)")
    p.add_argument("--end", type=int, default=1024, help="End port (default 1024)")
    p.add_argument("--timeout", type=float, default=0.5, help="Socket timeout in seconds (default 0.5)")
    p.add_argument("--workers", type=int, default=100, help="Number of threads (default 100)")
    p.add_argument("--banner", action="store_true", help="Attempt to read a small service banner after connect")
    p.add_argument("--out", default="results", help="Base filename for output files (default 'results')")
    return p.parse_args()

def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None

def scan_port(target_ip, port, timeout=0.5, do_banner=False):
    """
    Returns a dict:
    {
      "port": int,
      "status": "open" or "closed" or "filtered",
      "service": str or "",
      "banner": str (may be empty),
      "error": str or ""
    }
    """
    result = {"port": port, "status": "closed", "service": "", "banner": "", "error": ""}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        err = s.connect_ex((target_ip, port))
        if err == 0:
            result["status"] = "open"
            # Try to map to common service name
            try:
                result["service"] = socket.getservbyport(port)
            except Exception:
                result["service"] = ""
            if do_banner:
                try:
                    # Try to receive a short banner (non-blocking due to timeout)
                    s.settimeout(0.8)
                    banner = s.recv(1024)
                    if banner:
                        # decode best-effort
                        try:
                            result["banner"] = banner.decode(errors="replace").strip()
                        except Exception:
                            result["banner"] = repr(banner)[:200]
                except Exception:
                    # no banner / read timed out
                    pass
        else:
            # err != 0: could be refused (closed) or timeout (filtered). We try to infer.
            # Common: errno 111 = connection refused; timeout raises exception earlier.
            if err in (111, 10061):  # connection refused codes on Unix/Windows
                result["status"] = "closed"
            else:
                # treat as filtered/unreachable
                result["status"] = "filtered"
        s.close()
    except socket.timeout:
        result["status"] = "filtered"
    except Exception as e:
        result["status"] = "filtered"
        result["error"] = str(e)
    return result

def save_results_csv(results, filename):
    keys = ["port", "status", "service", "banner", "error"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in keys})

def save_results_json(results, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    args = parse_args()

    target_ip = resolve_target(args.target)
    if target_ip is None:
        print(f"[!] Could not resolve hostname: {args.target}")
        sys.exit(1)

    # Validate ports
    start_port = max(1, args.start)
    end_port = min(65535, args.end)
    if start_port > end_port:
        print("[!] Invalid port range")
        sys.exit(1)

    ports = list(range(start_port, end_port + 1))
    print("=== Multithreaded Port Scanner ===")
    print(f"Target: {args.target} -> {target_ip}")
    print(f"Ports: {start_port}..{end_port} ({len(ports)} ports)")
    print(f"Timeout: {args.timeout}s | Workers: {args.workers} | Banner grab: {args.banner}")
    start_time = datetime.now()
    print("Scan started at:", start_time.isoformat())

    results = []
    open_count = 0

    # Threaded scanning
    with ThreadPoolExecutor(max_workers=args.workers) as exe:
        futures = {exe.submit(scan_port, target_ip, p, args.timeout, args.banner): p for p in ports}
        try:
            for fut in as_completed(futures):
                res = fut.result()
                results.append(res)
                if res["status"] == "open":
                    open_count += 1
                    # Print progress for open ports only (keeps output readable)
                    svc = f" ({res['service']})" if res['service'] else ""
                    banner = f" | banner: {res['banner'][:120]}" if res.get("banner") else ""
                    print(f"Port {res['port']}: OPEN{svc}{banner}")
        except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user. Waiting for running threads to finish...")
            exe.shutdown(wait=False)
            # continue to saving partial results

    end_time = datetime.now()
    duration = end_time - start_time
    print("\nScan complete.")
    print(f"Open ports found: {open_count}")
    print("Duration:", str(duration))

    # Sort results by port
    results_sorted = sorted(results, key=lambda x: x["port"])

    # Prepare filenames with timestamp
    ts = start_time.strftime("%Y%m%d_%H%M%S")
    base = args.out
    csv_file = f"{base}_{ts}.csv"
    json_file = f"{base}_{ts}.json"

    # Ensure output directory exists if user passed a path
    out_dir = os.path.dirname(base)
    if out_dir and not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception:
            pass

    save_results_csv(results_sorted, csv_file)
    save_results_json(results_sorted, json_file)

    print(f"Results saved to: {csv_file} and {json_file}")

if __name__ == "__main__":
    main()
