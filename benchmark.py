import time
import subprocess
import sys

def run_benchmark():
    cmd = ["poetry", "run", "vt", "dl", "-w", "S14E5", "FranceTV", "https://www.france.tv/france-3/lego-ninjago/"]
    
    print("==================================================")
    print("           VINETRIMMER BENCHMARK TOOL             ")
    print("==================================================")
    print(f"Target: {' '.join(cmd)}")
    print("--------------------------------------------------")
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            print(line, end="", flush=True)
            
        process.wait()
    except KeyboardInterrupt:
        print("\n[!] Benchmark interrupted by user.")
        process.kill()
        sys.exit(1)
        
    end_time = time.time()
    duration = end_time - start_time
    
    print("--------------------------------------------------")
    if process.returncode == 0:
        print(f"[+] SUCCESS: Download completed in {duration:.2f} seconds.")
    else:
        print(f"[-] FAILED: Process exited with return code {process.returncode} after {duration:.2f} seconds.")
    print("==================================================")

if __name__ == "__main__":
    run_benchmark()
