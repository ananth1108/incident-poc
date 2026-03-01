import click
import hashlib
import json
from .extractor.ingest import process_file
from .mapper.map_to_adt import map_extraction
from .adt.client import sync_incident
from .db.repository import create_extraction_run

@click.group()
def cli():
    pass

@cli.command()
@click.option("--file", "file_path", required=True, type=click.Path(exists=True))
def ingest(file_path):
    """Ingest a report file via CLI"""
    file_hash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
    extracted = process_file(file_path)
    mapped = map_extraction(extracted)
    run = create_extraction_run(file_path, file_hash, extracted, mapped)
    adt_resp = sync_incident(mapped)
    # log sync
    from .db.repository import log_adt_sync
    try:
        log_adt_sync(run.id, adt_resp.get('action'),
                     adt_resp.get('response', {}).get('id'),
                     mapped, adt_resp.get('response'), 200, True)
    except Exception:
        pass
    with open('extracted.json','w') as f:
        json.dump(extracted, f, indent=2)
    with open('mapped_payload.json','w') as f:
        json.dump(mapped, f, indent=2)
    with open('adt_result.json','w') as f:
        json.dump(adt_resp, f, indent=2)
    click.echo('Done. Files written to cwd.')

if __name__ == '__main__':
    cli()