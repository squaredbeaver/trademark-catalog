import asyncio
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterator, Iterable, cast

from asyncpg import create_pool

from trademark_finder.models.trademark import Trademark
from trademark_finder.repositories.trademark import TrademarkRepository
from trademark_finder.services.application_parser import (
    ApplicationParsingResult,
    ParseApplicationRequest,
    TrademarkApplicationParserService,
)

XML_PATTERN = '*.xml'

logging.basicConfig(stream=sys.stdout, level='INFO')
logger = logging.getLogger('trademark-loader')


def count_xml_files(path: Path) -> int:
    return sum(1 for _ in path.rglob(XML_PATTERN))


def parse_from_directory(path: Path, parser: TrademarkApplicationParserService) -> Iterator[Trademark]:
    for xml_file in path.rglob(XML_PATTERN):
        request = ParseApplicationRequest(
            application_xml=xml_file.read_text(),
        )
        response = parser.parse_application(request)

        if not response.is_success():
            logger.error("Cannot parse trademark application from file %s", xml_file.absolute())
            continue

        application = cast(ApplicationParsingResult, response.application)
        if not application.is_valid():
            logger.error("Skipping invalid application from file %s", xml_file.absolute())
            continue

        yield Trademark(
            title=application.title,
            description=application.description,
            application_number=application.application_number,
            application_date=application.application_date,
            registration_date=application.registration_date,
            expiry_date=application.expiry_date,
        )


def iterate_trademark_batches(
        trademarks: Iterable[Trademark],
        batch_size: int,
) -> Iterator[list[Trademark]]:
    batch: list[Trademark] = []

    for trademark in trademarks:
        if len(batch) < batch_size:
            batch.append(trademark)
        else:
            yield batch
            batch.clear()


def init_arg_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Load trademarks data into a database')
    parser.add_argument(
        'directory',
        type=Path,
        help='path to a directory where source xml files are stored',
    )
    parser.add_argument(
        'dsn',
        type=str,
        help='database dsn to load the data into',
    )
    return parser


async def main() -> None:
    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    connection_pool = await create_pool(args.dsn, min_size=2, max_size=2)
    trademark_repository = TrademarkRepository(
        connection_pool=connection_pool,
        logger=logger,
    )
    xml_parser_service = TrademarkApplicationParserService(
        logger=logger,
    )

    total_files = count_xml_files(args.directory)
    batch_size = 1000
    processed_files = 0

    trademarks_iterator = parse_from_directory(args.directory, xml_parser_service)
    for batch in iterate_trademark_batches(trademarks_iterator, batch_size=batch_size):
        await trademark_repository.create_many(batch)
        processed_files += batch_size
        logger.info("Processed %s of %s files", processed_files, total_files)


if __name__ == '__main__':
    asyncio.run(main())
