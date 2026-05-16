import asyncio
import random
import logging
import aiohttp
import asyncssh

# Configure logging to output to the console for easy monitoring via Docker logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Target configurations matching the docker-compose DMZ network
WEB_TARGET = "http://10.10.10.20"
SSH_TARGET = "10.10.10.10"
SSH_PORT = 2222 

# Common payloads to simulate realistic background noise
HTTP_PATHS = ["/", "/login", "/about", "/images/logo.png", "/contact", "/admin"]
SSH_USERS = ["root", "admin", "ubuntu", "test", "user"]
SSH_PASSWORDS = ["123456", "password", "admin123", "root", "qwerty"]

async def generate_http_traffic():
    """Simulates organic web browsing by sending periodic GET requests."""
    async with aiohttp.ClientSession() as session:
        while True:
            path = random.choice(HTTP_PATHS)
            url = f"{WEB_TARGET}{path}"
            try:
                # Add a timeout to prevent hanging connections
                async with session.get(url, timeout=5) as response:
                    logging.info(f"HTTP GET {url} - Status: {response.status}")
            except Exception as e:
                logging.warning(f"HTTP Request failed: {e}")
            
            # Sleep for a randomized stochastic interval (e.g., between 1 and 7 seconds)
            await asyncio.sleep(random.uniform(1.0, 7.0))

async def generate_ssh_traffic():
    """Simulates background SSH noise, including automated brute-force chatter."""
    while True:
        user = random.choice(SSH_USERS)
        password = random.choice(SSH_PASSWORDS)
        
        try:
            # We expect these to fail, but the attempt generates the required TCP handshakes
            logging.info(f"SSH Attempt - User: {user} to {SSH_TARGET}")
            async with asyncssh.connect(
                SSH_TARGET, 
                port=SSH_PORT, 
                username=user, 
                password=password, 
                known_hosts=None, # Ignore host key verification for the sandbox
                client_keys=None
            ) as conn:
                logging.info(f"SSH Success (Unexpected): {user}")
        except asyncssh.PermissionDenied:
            logging.info(f"SSH Denied (Expected): {user}")
        except Exception as e:
            logging.warning(f"SSH Connection Error: {e}")

        # Sleep for a randomized interval (e.g., between 3 and 10 seconds)
        await asyncio.sleep(random.uniform(3.0, 10.0))

async def main():
    """Orchestrates the concurrent execution of traffic generation."""
    logging.info("Starting NetSnares Baseline Traffic Generator...")
    
    # Run both traffic generators concurrently
    await asyncio.gather(
        generate_http_traffic(),
        generate_ssh_traffic()
    )

if __name__ == "__main__":
    try:
        # Execute the main event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Traffic Generator manually stopped.")