import asyncio
import time
import httpx

# Number of concurrent requests to simulate
NUM_REQUESTS = 3

# URLs of the FastAPI endpoints
BLOCKING_URL = "http://localhost:8000/blocking"
NON_BLOCKING_URL = "http://localhost:8000/non-blocking"

async def simulate_requests(url: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [client.get(url) for _ in range(NUM_REQUESTS)]
        start = time.perf_counter()
        responses = await asyncio.gather(*tasks)
        end = time.perf_counter()
        return end - start

async def main():
    print("🔴 Testing blocking endpoint...")
    blocking_time = await simulate_requests(BLOCKING_URL)
    print(f"Blocking total time: {blocking_time:.2f} seconds")

    print("\n🟢 Testing non-blocking endpoint...")
    non_blocking_time = await simulate_requests(NON_BLOCKING_URL)
    print(f"Non-blocking total time: {non_blocking_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
