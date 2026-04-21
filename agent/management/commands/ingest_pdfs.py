from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from agent.models import Document
from agent.rag_pipeline.config import DOCS_DIR
from agent.rag_pipeline.ingestor import index_document


class Command(BaseCommand):
    help = "Ingest all PDFs from the docs directory into ChromaDB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--docs-dir",
            default=DOCS_DIR,
            help="Directory containing PDF files to ingest.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of PDFs to ingest.",
        )

    def handle(self, *args, **options):
        docs_dir = Path(options["docs_dir"]).expanduser()
        limit = options["limit"]

        if not docs_dir.exists():
            raise CommandError(f"Docs directory does not exist: {docs_dir}")

        pdf_files = sorted(
            (path for path in docs_dir.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"),
            key=lambda path: path.name.lower(),
        )

        if limit is not None:
            pdf_files = pdf_files[:limit]

        if not pdf_files:
            self.stdout.write(self.style.WARNING(f"No PDF files found in {docs_dir}"))
            return

        ingested = 0
        skipped = 0
        failed = 0

        for pdf_path in pdf_files:
            if Document.objects.filter(doc_name=pdf_path.name).exists():
                skipped += 1
                self.stdout.write(f"Skipping existing PDF: {pdf_path.name}")
                continue

            title = pdf_path.stem.replace("_", " ").strip()

            try:
                self.stdout.write(f"Ingesting: {pdf_path.name}")
                index_document(str(pdf_path), title)
                ingested += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(self.style.ERROR(f"Failed to ingest {pdf_path.name}: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished ingestion. Added: {ingested}, skipped: {skipped}, failed: {failed}"
            )
        )
