import uvicorn
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Vanguard Lens Dashboard Runner")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind the server to (Standard: 8001)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    app_path = "src.api.app:app"
    
    print("--- VANGUARD: LENS DASHBOARD ---")
    print(f"Starting Lens Dashboard on http://{args.host}:{args.port}")
    print("Use this dashboard to inspect lead payloads and refine MVDV heuristics.")
    
    uvicorn.run(app_path, host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
