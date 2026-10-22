"""CLI script to import the Kaggle Amazon Reviews dataset into ReviewPulse."""

import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.core.database import Base, get_engine, get_sessionmaker
from app.models.collection_job import CollectionJob
from app.services.harvester.importer import run_csv_import


async def import_kaggle_dataset(max_reviews: int | None = None) -> None:
    settings = get_settings()
    if not settings.database_url:
        print("Error: DATABASE_URL is not set.")
        return

    csv_path = settings.amazon_csv_path
    if not csv_path:
        print("Error: AMAZON_CSV_PATH is not configured.")
        return

    print(f"Connecting to database: {settings.database_url}")
    engine = get_engine(settings.database_url, settings=settings)

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = get_sessionmaker(settings.database_url, settings=settings)
    async with session_factory() as session:
        job = CollectionJob(source="csv_amazon", status="pending")
        session.add(job)
        await session.flush()

        limit = max_reviews or settings.amazon_import_limit or 2500
        print(f"Starting import from: {csv_path}")
        print(f"Review import limit: {limit} reviews")

        job = await run_csv_import(
            session=session,
            csv_path=csv_path,
            job=job,
            max_reviews=limit,
        )

        print("\n--- Import Summary ---")
        print(f"Status:            {job.status}")
        print(f"Products seen:     {job.products_seen}")
        print(f"Products inserted: {job.products_inserted}")
        print(f"Reviews seen:      {job.reviews_seen}")
        print(f"Reviews inserted:  {job.reviews_inserted}")
        print(f"Errors:            {job.error_count}")

    await engine.dispose()


if __name__ == "__main__":
    limit_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(import_kaggle_dataset(limit_arg))
